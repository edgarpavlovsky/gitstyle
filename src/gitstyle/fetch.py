"""Stage 1: Fetch — GitHub REST API → raw commit data (JSONL)."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gitstyle.config import GitStyleConfig
from gitstyle.github_client import GitHubClient
from gitstyle.models import FetchResult, RawCommit

console = Console()


def fetch(config: GitStyleConfig) -> FetchResult:
    """Fetch commits from GitHub. Supports incremental fetch when cache exists."""
    config.ensure_cache_dir()
    cache = config.commits_path()

    # If cache exists and not --fresh, try incremental
    if cache.exists() and not config.fresh:
        existing = _load_commits(cache)
        if not existing:
            # Empty cache file — treat as fresh
            return _fetch_fresh(config, cache)

        return _fetch_incremental(config, cache, existing)

    return _fetch_fresh(config, cache)


def _fetch_fresh(config: GitStyleConfig, cache: Path) -> FetchResult:
    """Full fetch from scratch."""
    console.print(f"[bold]Fetching commits for [cyan]{config.username}[/cyan]...[/bold]")

    all_commits = _fetch_from_github(config)

    if not all_commits:
        console.print("[yellow]  Warning: 0 commits fetched (not caching empty result)[/yellow]")
        return FetchResult(all_commits=[], new_commits=[])

    _save_commits(cache, all_commits)
    console.print(f"  Fetched [green]{len(all_commits)}[/green] commits → {cache}")
    return FetchResult(all_commits=all_commits, new_commits=all_commits)


def _fetch_incremental(
    config: GitStyleConfig, cache: Path, existing: list[RawCommit],
) -> FetchResult:
    """Incremental fetch — only get commits newer than what's cached."""
    # Find the latest commit date across all repos
    latest_date = max(c.authored_at for c in existing)
    # Use ISO format for GitHub API, add 1 second to avoid re-fetching the boundary commit
    since_str = latest_date.isoformat()

    existing_shas = {c.sha for c in existing}
    console.print(
        f"[bold]Incremental fetch for [cyan]{config.username}[/cyan][/bold] "
        f"[dim](since {latest_date.strftime('%Y-%m-%d')})[/dim]"
    )

    try:
        new_commits = _fetch_from_github(config, since_override=since_str)
    except Exception as e:
        console.print(f"[yellow]  Could not check for new commits: {e}[/yellow]")
        console.print("[dim]  Using cached commits[/dim]")
        return FetchResult(
            all_commits=existing, new_commits=[], is_incremental=True,
        )

    # Deduplicate — remove any commits we already have
    new_commits = [c for c in new_commits if c.sha not in existing_shas]

    if not new_commits:
        console.print("  [dim]No new commits since last run[/dim]")
        return FetchResult(
            all_commits=existing, new_commits=[], is_incremental=True,
        )

    # Merge and save
    merged = existing + new_commits
    _save_commits(cache, merged)
    console.print(
        f"  Found [green]{len(new_commits)}[/green] new commits "
        f"(total: {len(merged)})"
    )
    return FetchResult(
        all_commits=merged, new_commits=new_commits, is_incremental=True,
    )


def _fetch_from_github(
    config: GitStyleConfig, since_override: str | None = None,
) -> list[RawCommit]:
    """Core fetch logic — pull commits from GitHub API."""
    since = since_override or config.since

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
                    since=since,
                    until=config.until,
                    max_commits=config.max_commits // max(len(repos), 1),
                )
                all_commits.extend(commits)
                progress.advance(task)

                if len(all_commits) >= config.max_commits:
                    all_commits = all_commits[: config.max_commits]
                    break

    return all_commits


def _save_commits(path: Path, commits: list[RawCommit]) -> None:
    with open(path, "w") as f:
        for c in commits:
            f.write(c.model_dump_json() + "\n")


def _load_commits(path: Path) -> list[RawCommit]:
    commits = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                commits.append(RawCommit.model_validate_json(line))
    return commits
