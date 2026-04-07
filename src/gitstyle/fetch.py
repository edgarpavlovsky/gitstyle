"""Fetch stage — pull commits + diffs from GitHub API into cache."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from gitstyle.config import FetchConfig
from gitstyle.github_client import GitHubClient
from gitstyle.models import Commit, RepoInfo

console = Console()


def run_fetch(config: FetchConfig, cache_dir: Path) -> tuple[list[RepoInfo], list[Commit]]:
    """Fetch all commits for a user and cache them locally.

    Returns (repos, commits) — commits have summary info only (no diffs yet).
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    repos_path = cache_dir / "repos.jsonl"
    commits_path = cache_dir / "commits.jsonl"

    # Check cache
    if repos_path.exists() and commits_path.exists():
        console.print("[dim]Using cached fetch data. Delete .gitstyle/repos.jsonl to re-fetch.[/dim]")
        repos = [RepoInfo.model_validate_json(line) for line in repos_path.read_text().splitlines() if line.strip()]
        commits = [Commit.model_validate_json(line) for line in commits_path.read_text().splitlines() if line.strip()]
        return repos, commits

    console.print(f"[bold]Fetching commits for [cyan]{config.username}[/cyan]...[/bold]")

    with GitHubClient(token=config.token) as client:
        repos, commits = client.fetch_all(
            username=config.username,
            include_forks=config.include_forks,
            include_repos=config.include_repos,
            exclude_repos=config.exclude_repos,
            max_commits_per_repo=config.max_commits_per_repo,
            since=config.since,
            until=config.until,
        )

    # Write cache
    repos_path.write_text("\n".join(r.model_dump_json() for r in repos) + "\n")
    commits_path.write_text("\n".join(c.model_dump_json() for c in commits) + "\n")

    console.print(f"[green]Fetched {len(commits)} commits across {len(repos)} repos.[/green]")
    return repos, commits


def fetch_diffs(
    commits: list[Commit],
    config: FetchConfig,
    cache_dir: Path,
) -> list[Commit]:
    """Fetch full diffs for a list of commits. Caches each individually."""
    diffs_dir = cache_dir / "diffs"
    diffs_dir.mkdir(parents=True, exist_ok=True)

    enriched: list[Commit] = []
    with GitHubClient(token=config.token) as client:
        for commit in commits:
            diff_path = diffs_dir / f"{commit.sha}.json"
            if diff_path.exists():
                enriched.append(Commit.model_validate_json(diff_path.read_text()))
                continue
            try:
                detailed = client.get_commit_detail(commit.repo, commit.sha)
                diff_path.write_text(detailed.model_dump_json())
                enriched.append(detailed)
            except Exception as e:
                console.print(f"[yellow]Skipping {commit.sha[:8]}: {e}[/yellow]")
                enriched.append(commit)

    return enriched
