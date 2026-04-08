"""Stage 1: Fetch — GitHub REST API → raw commit data (JSONL)."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gitstyle.config import GitStyleConfig
from gitstyle.github_client import GitHubClient
from gitstyle.models import RawCommit

console = Console()


def fetch(config: GitStyleConfig) -> list[RawCommit]:
    """Fetch commits from GitHub and cache as JSONL."""
    config.ensure_cache_dir()
    cache = config.commits_path()

    # Resume from cache
    if cache.exists():
        console.print(f"[dim]Using cached commits from {cache}[/dim]")
        return _load_commits(cache)

    console.print(f"[bold]Fetching commits for [cyan]{config.username}[/cyan]...[/bold]")

    with GitHubClient(config.github_token) as gh:
        repos = gh.list_repos(config.username, config.repos)
        console.print(f"  Found [green]{len(repos)}[/green] repos")

        all_commits: list[RawCommit] = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching...", total=len(repos))
            for repo in repos:
                progress.update(task, description=f"Fetching {repo}...")
                languages = gh.get_repo_languages(repo)
                commits = gh.fetch_commits_for_repo(
                    repo=repo,
                    author=config.username,
                    languages=languages,
                    since=config.since,
                    until=config.until,
                    max_commits=config.max_commits // max(len(repos), 1),
                )
                all_commits.extend(commits)
                progress.advance(task)

                if len(all_commits) >= config.max_commits:
                    all_commits = all_commits[: config.max_commits]
                    break

    if not all_commits:
        console.print("[yellow]  Warning: 0 commits fetched (not caching empty result)[/yellow]")
        return all_commits

    # Write JSONL cache
    with open(cache, "w") as f:
        for c in all_commits:
            f.write(c.model_dump_json() + "\n")

    console.print(f"  Fetched [green]{len(all_commits)}[/green] commits → {cache}")
    return all_commits


def _load_commits(path: Path) -> list[RawCommit]:
    commits = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                commits.append(RawCommit.model_validate_json(line))
    return commits
