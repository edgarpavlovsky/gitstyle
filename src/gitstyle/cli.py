"""CLI interface for gitstyle."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from gitstyle import __version__
from gitstyle.config import FetchConfig, LLMConfig, PipelineConfig, SampleConfig

app = typer.Typer(
    name="gitstyle",
    help="Generate a personal engineering style wiki from your GitHub commit history.",
    no_args_is_help=True,
)
console = Console()


def _build_config(
    username: str,
    output_dir: Path = Path("wiki"),
    cache_dir: Path = Path(".gitstyle"),
    model: str = "claude-sonnet-4-20250514",
    include_forks: bool = False,
    max_commits: int = 200,
    max_repos: int = 30,
    max_samples: int = 20,
    since: Optional[str] = None,
    until: Optional[str] = None,
    include_repos: Optional[list[str]] = None,
    exclude_repos: Optional[list[str]] = None,
    strategy: str = "balanced",
) -> PipelineConfig:
    return PipelineConfig(
        fetch=FetchConfig(
            username=username,
            include_forks=include_forks,
            include_repos=include_repos,
            exclude_repos=exclude_repos,
            max_commits_per_repo=max_commits,
            max_repos=max_repos,
            since=since,
            until=until,
        ),
        sample=SampleConfig(max_samples_per_cluster=max_samples, strategy=strategy),
        llm=LLMConfig(model=model),
        output_dir=output_dir,
        cache_dir=cache_dir,
    )


@app.command()
def run(
    username: str = typer.Argument(help="GitHub username or organization to analyze"),
    output_dir: Path = typer.Option(Path("wiki"), "--output", "-o", help="Output directory for wiki"),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache", help="Cache directory"),
    model: str = typer.Option("claude-sonnet-4-20250514", "--model", "-m", help="LLM model to use"),
    include_forks: bool = typer.Option(False, "--forks", help="Include forked repos"),
    max_commits: int = typer.Option(200, "--max-commits", help="Max commits per repo"),
    max_repos: int = typer.Option(30, "--max-repos", help="Max repos to analyze (sorted by stars for orgs)"),
    max_samples: int = typer.Option(20, "--max-samples", help="Max samples per cluster"),
    since: Optional[str] = typer.Option(None, "--since", help="Fetch commits after this date (ISO format)"),
    until: Optional[str] = typer.Option(None, "--until", help="Fetch commits before this date (ISO format)"),
    skip_lint: bool = typer.Option(False, "--skip-lint", help="Skip the lint stage"),
    include_repos: Optional[str] = typer.Option(None, "--include-repos", help="Comma-separated repos to include"),
    exclude_repos: Optional[str] = typer.Option(None, "--exclude-repos", help="Comma-separated repos to exclude"),
    strategy: str = typer.Option("balanced", "--strategy", help="Sampling: balanced, recent, largest"),
) -> None:
    """Run the full pipeline: fetch → sample → extract → compile → lint."""
    from gitstyle.compile import run_compile
    from gitstyle.extract import run_extract
    from gitstyle.fetch import fetch_diffs, run_fetch
    from gitstyle.lint import run_lint
    from gitstyle.sample import run_sample
    from gitstyle.wiki_writer import write_article, write_index, write_meta

    config = _build_config(
        username=username,
        output_dir=output_dir,
        cache_dir=cache_dir,
        model=model,
        include_forks=include_forks,
        max_commits=max_commits,
        max_repos=max_repos,
        max_samples=max_samples,
        since=since,
        until=until,
        include_repos=include_repos.split(",") if include_repos else None,
        exclude_repos=exclude_repos.split(",") if exclude_repos else None,
        strategy=strategy,
    )

    console.print(f"\n[bold cyan]gitstyle v{__version__}[/bold cyan]")
    console.print(f"Analyzing [bold]{username}[/bold]...\n")

    # Stage 1: Fetch (auto-detects user vs org)
    console.rule("[bold]Stage 1: Fetch[/bold]")
    repos, commits, account_type = run_fetch(config.fetch, config.cache_dir)
    context_type = "organization" if account_type == "Organization" else "individual"
    config.context_type = context_type

    if context_type == "organization":
        console.print(f"[bold cyan]Detected organization — analyzing org engineering patterns[/bold cyan]")
    else:
        console.print(f"Analyzing [bold]{username}[/bold]'s engineering style...")

    if not commits:
        console.print("[red]No commits found. Check the username and try again.[/red]")
        raise typer.Exit(1)

    # Stage 2: Sample
    console.rule("[bold]Stage 2: Sample[/bold]")
    # Fetch diffs for all commits before sampling
    enriched = fetch_diffs(commits, config.fetch, config.cache_dir)
    clusters = run_sample(enriched, repos, config.sample)

    # Stage 3: Extract
    console.rule("[bold]Stage 3: Extract[/bold]")
    extractions = run_extract(clusters, config.llm, config.cache_dir, context_type=context_type)

    # Stage 4: Compile
    console.rule("[bold]Stage 4: Compile[/bold]")
    articles = run_compile(extractions, config.llm, config.cache_dir, context_type=context_type)

    # Stage 5: Lint
    if not skip_lint:
        console.rule("[bold]Stage 5: Lint[/bold]")
        run_lint(articles, config.llm)

    # Write output
    console.rule("[bold]Writing Wiki[/bold]")
    for article in articles:
        filepath = write_article(article, config.output_dir)
        console.print(f"  Wrote {filepath}")

    write_index(articles, config.output_dir)

    stats = {
        "total_fetched": len(commits),
        "total_sampled": sum(len(c.commits) for c in clusters),
        "repos": {r.full_name: len([c for c in commits if c.repo == r.full_name]) for r in repos},
    }
    log_entries = [
        f"Generated by gitstyle v{__version__}",
        f"User: {username}",
        f"Model: {config.llm.model}",
        f"Repos analyzed: {len(repos)}",
        f"Total commits: {len(commits)}",
        f"Clusters formed: {len(clusters)}",
        f"Articles written: {len(articles)}",
    ]
    write_meta(
        config.model_dump(mode="json", exclude={"fetch": {"token"}, "llm": {"api_key"}}),
        stats,
        log_entries,
        config.output_dir,
    )

    console.print(f"\n[bold green]✓ Wiki generated at {config.output_dir}/[/bold green]")
    console.print(f"  {len(articles)} articles across {len(repos)} repos")


@app.command()
def fetch(
    username: str = typer.Argument(help="GitHub username"),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache"),
    include_forks: bool = typer.Option(False, "--forks"),
    max_commits: int = typer.Option(200, "--max-commits"),
    since: Optional[str] = typer.Option(None, "--since"),
    until: Optional[str] = typer.Option(None, "--until"),
) -> None:
    """Run only the fetch stage."""
    from gitstyle.fetch import run_fetch

    config = FetchConfig(
        username=username,
        include_forks=include_forks,
        max_commits_per_repo=max_commits,
        since=since,
        until=until,
    )
    repos, commits, _account_type = run_fetch(config, cache_dir)
    console.print(f"[green]Fetched {len(commits)} commits from {len(repos)} repos.[/green]")


@app.command()
def version() -> None:
    """Show version."""
    console.print(f"gitstyle v{__version__}")


def main() -> None:
    app()
