"""Sample stage — cluster commits and select representative samples."""

from __future__ import annotations

import random
from collections import defaultdict

from rich.console import Console

from gitstyle.config import SampleConfig
from gitstyle.models import Commit, CommitCluster, RepoInfo

console = Console()

# Map file extensions to languages
EXT_LANG: dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".swift": "swift",
    ".kt": "kotlin",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp",
    ".cs": "csharp",
    ".php": "php",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".sql": "sql",
    ".html": "html", ".css": "css", ".scss": "scss",
    ".yaml": "yaml", ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
    ".toml": "toml",
    ".dockerfile": "docker",
}


def _detect_language(commit: Commit) -> str | None:
    """Detect primary language from changed files."""
    lang_counts: dict[str, int] = defaultdict(int)
    for f in commit.files:
        ext = "." + f.filename.rsplit(".", 1)[-1] if "." in f.filename else ""
        lang = EXT_LANG.get(ext.lower())
        if lang:
            lang_counts[lang] += f.additions + f.deletions
    if not lang_counts:
        return None
    return max(lang_counts, key=lambda k: lang_counts[k])


def _diff_size(commit: Commit) -> int:
    return commit.additions + commit.deletions


def cluster_commits(
    commits: list[Commit],
    repos: list[RepoInfo],
) -> list[CommitCluster]:
    """Group commits by repo × primary language."""
    buckets: dict[str, list[Commit]] = defaultdict(list)
    for commit in commits:
        lang = _detect_language(commit) or "unknown"
        key = f"{commit.repo}:{lang}"
        buckets[key].append(commit)

    clusters = []
    for key, group in buckets.items():
        repo_name, lang = key.rsplit(":", 1)
        clusters.append(
            CommitCluster(
                label=key,
                repo=repo_name,
                language=lang if lang != "unknown" else None,
                commits=group,
            )
        )
    return clusters


def sample_cluster(cluster: CommitCluster, config: SampleConfig) -> CommitCluster:
    """Select representative commits from a cluster using the configured strategy."""
    commits = cluster.commits
    n = config.max_samples_per_cluster

    if len(commits) <= n:
        return cluster

    # Filter out trivially small diffs
    nontrivial = [c for c in commits if _diff_size(c) >= config.min_diff_lines]
    if not nontrivial:
        nontrivial = commits

    if config.strategy == "recent":
        sampled = sorted(nontrivial, key=lambda c: c.date, reverse=True)[:n]
    elif config.strategy == "largest":
        sampled = sorted(nontrivial, key=_diff_size, reverse=True)[:n]
    else:
        # balanced: mix of recent, largest, and random
        by_date = sorted(nontrivial, key=lambda c: c.date, reverse=True)
        by_size = sorted(nontrivial, key=_diff_size, reverse=True)
        third = max(1, n // 3)
        selected = set()
        sampled = []
        for source in [by_date, by_size]:
            for c in source:
                if c.sha not in selected and len(sampled) < third * (1 + len(sampled) // third):
                    selected.add(c.sha)
                    sampled.append(c)
                if len(sampled) >= third * 2:
                    break
        remaining = [c for c in nontrivial if c.sha not in selected]
        if remaining:
            extras = random.sample(remaining, min(n - len(sampled), len(remaining)))
            sampled.extend(extras)

    return CommitCluster(
        label=cluster.label,
        repo=cluster.repo,
        language=cluster.language,
        commits=sampled[:n],
    )


def run_sample(
    commits: list[Commit],
    repos: list[RepoInfo],
    config: SampleConfig,
) -> list[CommitCluster]:
    """Cluster and sample commits. Returns sampled clusters."""
    clusters = cluster_commits(commits, repos)
    console.print(f"[bold]Formed {len(clusters)} clusters from {len(commits)} commits.[/bold]")

    sampled = [sample_cluster(c, config) for c in clusters]
    total = sum(len(c.commits) for c in sampled)
    console.print(f"[green]Sampled down to {total} representative commits.[/green]")

    return sampled
