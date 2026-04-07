"""Stage 2: Sample — group commits by repo × language, sample representative commits."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

from rich.console import Console

from gitstyle.config import GitStyleConfig
from gitstyle.models import RawCommit, SampledCluster

console = Console()


def sample(commits: list[RawCommit], config: GitStyleConfig) -> list[SampledCluster]:
    """Group commits by repo × language and sample representative ones."""
    config.ensure_cache_dir()
    cache = config.samples_path()

    if cache.exists():
        console.print(f"[dim]Using cached samples from {cache}[/dim]")
        return _load_samples(cache)

    console.print("[bold]Sampling representative commits...[/bold]")

    # Group by repo × language
    groups: dict[tuple[str, str], list[RawCommit]] = defaultdict(list)
    for c in commits:
        if c.languages:
            for lang in c.languages:
                groups[(c.repo, lang)].append(c)
        else:
            groups[(c.repo, "unknown")].append(c)

    clusters: list[SampledCluster] = []
    for (repo, lang), group_commits in groups.items():
        total = len(group_commits)
        sampled = _sample_group(group_commits, config.samples_per_group)
        clusters.append(SampledCluster(
            repo=repo,
            language=lang,
            commits=sampled,
            total_in_group=total,
        ))

    # Cache
    with open(cache, "w") as f:
        json.dump([c.model_dump(mode="json") for c in clusters], f, indent=2, default=str)

    total_sampled = sum(len(c.commits) for c in clusters)
    console.print(
        f"  [green]{len(clusters)}[/green] clusters, "
        f"[green]{total_sampled}[/green] sampled commits"
    )
    return clusters


def _sample_group(commits: list[RawCommit], n: int) -> list[RawCommit]:
    """Sample up to n commits: most recent + largest diffs + random fill."""
    if len(commits) <= n:
        return commits

    selected: dict[str, RawCommit] = {}

    # Most recent (top 1/3)
    by_date = sorted(commits, key=lambda c: c.authored_at, reverse=True)
    recent_n = n // 3
    for c in by_date[:recent_n]:
        selected[c.sha] = c

    # Largest diffs (top 1/3)
    by_size = sorted(commits, key=lambda c: c.additions + c.deletions, reverse=True)
    large_n = n // 3
    for c in by_size[:large_n]:
        selected[c.sha] = c

    # Random fill
    remaining = [c for c in commits if c.sha not in selected]
    fill_n = n - len(selected)
    if fill_n > 0 and remaining:
        random.seed(42)  # reproducible
        for c in random.sample(remaining, min(fill_n, len(remaining))):
            selected[c.sha] = c

    return list(selected.values())


def _load_samples(path: Path) -> list[SampledCluster]:
    with open(path) as f:
        data = json.load(f)
    return [SampledCluster.model_validate(d) for d in data]
