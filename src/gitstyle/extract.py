"""Stage 3: Extract — LLM pass per cluster → structured style observations."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gitstyle.config import GitStyleConfig
from gitstyle.llm_client import LLMClient
from gitstyle.models import ClusterExtraction, Observation, SampledCluster, StyleDimension

console = Console()

EXTRACT_SYSTEM = """\
You are a senior code reviewer analyzing a developer's commit history to identify \
their engineering style and patterns. You will receive a set of commits from a single \
repository and programming language.

Analyze the commits and produce observations across these 9 style dimensions:
1. code-structure — file organization, module boundaries, function/class sizing
2. naming-conventions — variable, function, class, file naming patterns
3. patterns — design patterns, architectural patterns, common abstractions
4. type-discipline — type annotations, generics, type safety approach
5. testing — test coverage, test style, testing frameworks, TDD signals
6. comments-and-docs — documentation style, comment density, docstrings
7. dependencies — dependency management, third-party library choices
8. commit-hygiene — commit message style, commit size, branching patterns
9. language-idioms — language-specific patterns, idiomatic usage

For each observation provide:
- dimension: one of the 9 dimensions above
- claim: a specific, concrete observation about the developer's style
- evidence: list of commit SHAs that support this claim
- confidence: 0.0–1.0 (how confident given the evidence)
- language: the programming language (if language-specific)

Return valid JSON: {"observations": [...]}\
"""


def extract(
    clusters: list[SampledCluster],
    config: GitStyleConfig,
) -> list[ClusterExtraction]:
    """Run LLM extraction on each cluster."""
    config.ensure_cache_dir()
    cache = config.extractions_path()

    if cache.exists():
        console.print(f"[dim]Using cached extractions from {cache}[/dim]")
        return _load_extractions(cache)

    llm = LLMClient(model=config.llm_model)

    # Cost estimate
    total_tokens = 0
    for cluster in clusters:
        prompt = _build_prompt(cluster)
        total_tokens += llm.estimate_tokens(prompt)
    estimated_calls = len(clusters)
    console.print(
        f"[bold]Extract stage:[/bold] {estimated_calls} LLM calls, "
        f"~{total_tokens:,} input tokens"
    )
    if config.dry_run:
        console.print("[yellow]Dry run — skipping LLM calls[/yellow]")
        return []

    extractions: list[ClusterExtraction] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting...", total=len(clusters))
        for cluster in clusters:
            progress.update(
                task, description=f"Extracting {cluster.repo} ({cluster.language})..."
            )
            prompt = _build_prompt(cluster)
            try:
                data = llm.complete_json(EXTRACT_SYSTEM, prompt)
                observations = [
                    Observation.model_validate(o) for o in data.get("observations", [])
                ]
            except Exception as e:
                console.print(
                    f"[red]  Error extracting {cluster.repo}/{cluster.language}: {e}[/red]"
                )
                observations = []

            extractions.append(ClusterExtraction(
                repo=cluster.repo,
                language=cluster.language,
                observations=observations,
            ))
            progress.advance(task)

    # Cache
    with open(cache, "w") as f:
        json.dump([e.model_dump(mode="json") for e in extractions], f, indent=2)

    total_obs = sum(len(e.observations) for e in extractions)
    console.print(f"  Extracted [green]{total_obs}[/green] observations")
    return extractions


def _build_prompt(cluster: SampledCluster) -> str:
    lines = [
        f"Repository: {cluster.repo}",
        f"Language: {cluster.language}",
        f"Commits ({len(cluster.commits)} of {cluster.total_in_group} total):",
        "",
    ]
    for c in cluster.commits:
        lines.append(f"--- Commit {c.sha[:8]} ---")
        lines.append(f"Date: {c.authored_at.isoformat()}")
        lines.append(f"Message: {c.message}")
        lines.append(f"Stats: +{c.additions} -{c.deletions}")
        if c.files:
            lines.append("Files:")
            for f in c.files[:20]:  # cap files per commit
                patch_preview = ""
                if f.patch:
                    patch_preview = f.patch[:500]
                lines.append(f"  {f.status} {f.filename} (+{f.additions} -{f.deletions})")
                if patch_preview:
                    lines.append(f"    {patch_preview}")
        lines.append("")
    return "\n".join(lines)


def _load_extractions(path: Path) -> list[ClusterExtraction]:
    with open(path) as f:
        data = json.load(f)
    return [ClusterExtraction.model_validate(d) for d in data]
