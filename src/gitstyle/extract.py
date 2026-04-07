"""Extract stage — LLM pass over each cluster to produce structured style observations."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from gitstyle.config import LLMConfig
from gitstyle.llm_client import LLMClient
from gitstyle.models import CommitCluster, StyleExtractionResult, StyleObservation

console = Console()

STYLE_CATEGORIES = [
    "code-structure",
    "naming-conventions",
    "patterns",
    "type-discipline",
    "testing",
    "comments-and-docs",
    "dependencies",
    "commit-hygiene",
    "language-idioms",
]

EXTRACT_SYSTEM = """You are an expert code analyst. You examine Git commits and extract observations about a developer's engineering style.

Given a cluster of commits from one repo/language, analyze them and produce structured observations.

For each observation, provide:
- category: one of {categories}
- observation: a clear, specific description of the pattern you see
- evidence: list of commit SHAs that support this observation
- confidence: low, medium, or high

Output ONLY a JSON array of observation objects. No markdown, no explanation. Example:
[
  {{
    "category": "naming-conventions",
    "observation": "Uses snake_case for Python functions and variables, PascalCase for classes",
    "evidence": ["abc1234", "def5678"],
    "confidence": "high"
  }}
]"""

EXTRACT_USER = """Cluster: {label}
Repository: {repo}
Language: {language}

Commits ({count} total):
{commits_text}

Analyze these commits and extract observations about the developer's engineering style. Cover as many categories as the evidence supports: {categories}"""


def _format_commit(commit) -> str:
    """Format a commit for the LLM prompt."""
    lines = [f"### {commit.sha[:8]} — {commit.message.split(chr(10))[0]}"]
    lines.append(f"Date: {commit.date}")
    for f in commit.files[:20]:
        lines.append(f"  {f.status} {f.filename} (+{f.additions}/-{f.deletions})")
        if f.patch:
            patch_lines = f.patch.split("\n")[:50]
            lines.append("  ```")
            lines.extend(f"  {pl}" for pl in patch_lines)
            lines.append("  ```")
    return "\n".join(lines)


def _cluster_cache_key(cluster: CommitCluster) -> str:
    """Generate a safe filename for caching a cluster extraction."""
    return cluster.label.replace("/", "_").replace(":", "_")


def extract_cluster(
    cluster: CommitCluster,
    llm: LLMClient,
    cache_dir: Path | None = None,
) -> StyleExtractionResult:
    """Run LLM extraction on a single cluster."""
    # Check cache
    if cache_dir:
        cache_path = cache_dir / "extractions" / f"{_cluster_cache_key(cluster)}.json"
        if cache_path.exists():
            return StyleExtractionResult.model_validate_json(cache_path.read_text())

    commits_text = "\n\n".join(_format_commit(c) for c in cluster.commits)
    if len(commits_text) > 80_000:
        commits_text = commits_text[:80_000] + "\n\n[... truncated]"

    system = EXTRACT_SYSTEM.format(categories=", ".join(STYLE_CATEGORIES))
    user = EXTRACT_USER.format(
        label=cluster.label,
        repo=cluster.repo,
        language=cluster.language or "mixed",
        count=len(cluster.commits),
        commits_text=commits_text,
        categories=", ".join(STYLE_CATEGORIES),
    )

    try:
        data = llm.complete_json(system, user)
    except (json.JSONDecodeError, Exception):
        console.print(f"[yellow]Warning: Could not parse extraction for {cluster.label}[/yellow]")
        return StyleExtractionResult(cluster_label=cluster.label)

    observations = [
        StyleObservation(
            cluster_label=cluster.label,
            category=obs.get("category", "unknown"),
            observation=obs.get("observation", ""),
            evidence=obs.get("evidence", []),
            confidence=obs.get("confidence", "medium"),
        )
        for obs in data
        if isinstance(obs, dict)
    ]

    result = StyleExtractionResult(cluster_label=cluster.label, observations=observations)

    # Write cache
    if cache_dir:
        cache_path = cache_dir / "extractions" / f"{_cluster_cache_key(cluster)}.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(result.model_dump_json(indent=2))

    return result


def run_extract(
    clusters: list[CommitCluster],
    llm_config: LLMConfig,
    cache_dir: Path,
) -> list[StyleExtractionResult]:
    """Run extraction across all clusters."""
    llm = LLMClient(llm_config)
    results: list[StyleExtractionResult] = []

    for i, cluster in enumerate(clusters, 1):
        if not cluster.commits:
            continue
        console.print(f"[bold]Extracting [{i}/{len(clusters)}]: {cluster.label} ({len(cluster.commits)} commits)...[/bold]")
        result = extract_cluster(cluster, llm, cache_dir)
        console.print(f"  [green]{len(result.observations)} observations[/green]")
        results.append(result)

    total = sum(len(r.observations) for r in results)
    console.print(f"[bold green]Extraction complete: {total} observations from {len(results)} clusters.[/bold green]")
    return results
