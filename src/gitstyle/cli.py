"""gitstyle CLI — powered by Typer."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from gitstyle import __version__
from gitstyle.config import GitStyleConfig

app = typer.Typer(
    name="gitstyle",
    help="Analyze a developer's GitHub commit history → engineering style wiki.",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool):
    if value:
        console.print(f"gitstyle {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=_version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    pass


@app.command()
def run(
    username: str = typer.Argument(..., help="GitHub username to analyze."),
    output: Path = typer.Option(Path("wiki"), "--output", "-o", help="Output directory for wiki."),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache", help="Cache directory."),
    max_commits: int = typer.Option(2000, "--max-commits", "-n", help="Max commits to fetch."),
    samples: int = typer.Option(20, "--samples", "-s", help="Samples per repo×language group."),
    repos: Optional[str] = typer.Option(None, "--repos", "-r", help="Comma-separated repo filter (owner/name)."),
    since: Optional[str] = typer.Option(None, "--since", help="Only commits after this date (ISO 8601)."),
    until: Optional[str] = typer.Option(None, "--until", help="Only commits before this date (ISO 8601)."),
    model: str = typer.Option("claude-sonnet-4-20250514", "--model", "-m", help="LLM model to use."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen without making LLM calls."),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN env var)."),
    fresh: bool = typer.Option(False, "--fresh", help="Force full re-run, ignoring cache."),
):
    """Run the full pipeline: fetch → sample → extract → compile → lint → write.

    By default, runs incrementally — only fetching new commits since the last run
    and evolving the existing wiki. Use --fresh to force a full rebuild.
    """
    github_token = token or os.environ.get("GITHUB_TOKEN")
    if not github_token:
        console.print("[red]Error: Set GITHUB_TOKEN env var or pass --token[/red]")
        raise typer.Exit(1)

    repos_list = [r.strip() for r in repos.split(",")] if repos else None

    config = GitStyleConfig(
        username=username,
        github_token=github_token,
        output_dir=output,
        cache_dir=cache_dir,
        max_commits=max_commits,
        samples_per_group=samples,
        repos=repos_list,
        since=since,
        until=until,
        llm_model=model,
        dry_run=dry_run,
        fresh=fresh,
    )

    # Validate GitHub token early
    from gitstyle.github_client import GitHubClient
    try:
        with GitHubClient(github_token) as gh:
            resp = gh._request("GET", "/user")
            console.print(f"[dim]GitHub auth: {resp.json().get('login', 'ok')}[/dim]")
    except Exception as e:
        console.print(
            f"[red]Error: GitHub token is invalid or expired.[/red]\n"
            f"[dim]{e}[/dim]"
        )
        raise typer.Exit(1)

    # Validate LLM credentials early (before fetching anything)
    if not dry_run:
        from gitstyle.llm_client import LLMClient
        try:
            llm = LLMClient(model=model)
            console.print(f"[dim]LLM auth: {llm._auth_method}[/dim]")
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

    console.print(Panel(
        f"[bold]gitstyle[/bold] v{__version__}\n"
        f"Analyzing [cyan]{username}[/cyan]'s engineering style"
        f"{' [dim](fresh run)[/dim]' if fresh else ''}",
        border_style="blue",
    ))

    _run_pipeline(config)


@app.command()
def fetch_cmd(
    username: str = typer.Argument(..., help="GitHub username."),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache"),
    max_commits: int = typer.Option(2000, "--max-commits", "-n"),
    repos: Optional[str] = typer.Option(None, "--repos", "-r"),
    since: Optional[str] = typer.Option(None, "--since"),
    until: Optional[str] = typer.Option(None, "--until"),
    token: Optional[str] = typer.Option(None, "--token", "-t"),
    fresh: bool = typer.Option(False, "--fresh"),
):
    """Run only the fetch stage."""
    from gitstyle.fetch import fetch

    github_token = token or os.environ.get("GITHUB_TOKEN")
    repos_list = [r.strip() for r in repos.split(",")] if repos else None
    config = GitStyleConfig(
        username=username, github_token=github_token, cache_dir=cache_dir,
        max_commits=max_commits, repos=repos_list, since=since, until=until,
        fresh=fresh,
    )
    result = fetch(config)
    console.print(f"Total commits: {len(result.all_commits)}")
    if result.is_incremental:
        console.print(f"New commits: {len(result.new_commits)}")


@app.command()
def sample_cmd(
    username: str = typer.Argument(..., help="GitHub username."),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache"),
    samples: int = typer.Option(20, "--samples", "-s"),
):
    """Run only the sample stage (requires cached commits)."""
    from gitstyle.fetch import fetch
    from gitstyle.sample import sample

    config = GitStyleConfig(username=username, cache_dir=cache_dir, samples_per_group=samples)
    result = fetch(config)
    sample(result.all_commits, config)


@app.command()
def extract_cmd(
    username: str = typer.Argument(..., help="GitHub username."),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache"),
    model: str = typer.Option("claude-sonnet-4-20250514", "--model", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Run only the extract stage (requires cached samples)."""
    from gitstyle.extract import extract
    from gitstyle.fetch import fetch
    from gitstyle.sample import sample

    config = GitStyleConfig(
        username=username, cache_dir=cache_dir, llm_model=model, dry_run=dry_run,
    )
    result = fetch(config)
    clusters = sample(result.all_commits, config)
    extract(clusters, config)


@app.command()
def compile_cmd(
    username: str = typer.Argument(..., help="GitHub username."),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache"),
    output: Path = typer.Option(Path("wiki"), "--output", "-o"),
    model: str = typer.Option("claude-sonnet-4-20250514", "--model", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Run only the compile stage (requires cached extractions)."""
    from gitstyle.compile import compile_wiki
    from gitstyle.extract import extract
    from gitstyle.fetch import fetch
    from gitstyle.sample import sample

    config = GitStyleConfig(
        username=username, cache_dir=cache_dir, output_dir=output,
        llm_model=model, dry_run=dry_run,
    )
    result = fetch(config)
    clusters = sample(result.all_commits, config)
    extractions = extract(clusters, config)
    compile_wiki(extractions, config)


@app.command()
def lint_cmd(
    username: str = typer.Argument(..., help="GitHub username."),
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache"),
    model: str = typer.Option("claude-sonnet-4-20250514", "--model", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Run only the lint stage (requires cached articles)."""
    from gitstyle.compile import compile_wiki
    from gitstyle.extract import extract
    from gitstyle.fetch import fetch
    from gitstyle.lint import lint
    from gitstyle.sample import sample

    config = GitStyleConfig(
        username=username, cache_dir=cache_dir, llm_model=model, dry_run=dry_run,
    )
    result = fetch(config)
    clusters = sample(result.all_commits, config)
    extractions = extract(clusters, config)
    articles = compile_wiki(extractions, config)
    lint(articles, config)


@app.command()
def serve(
    wiki_dir: Path = typer.Option(Path("wiki"), "--wiki-dir", "-w", help="Wiki directory to serve."),
    port: int = typer.Option(8080, "--port", "-p", help="Port to listen on."),
    no_open: bool = typer.Option(False, "--no-open", help="Don't auto-open browser."),
):
    """Launch local web viewer with interactive graph visualization."""
    if not wiki_dir.exists():
        console.print(f"[red]Error: Wiki directory '{wiki_dir}' not found.[/red]")
        console.print("[dim]Run 'gitstyle run <username>' first to generate a wiki.[/dim]")
        raise typer.Exit(1)

    from gitstyle.serve import start_server

    server = start_server(wiki_dir, port)
    url = f"http://127.0.0.1:{port}"
    console.print(Panel(
        f"[bold]gitstyle viewer[/bold]\n"
        f"Serving [cyan]{wiki_dir}[/cyan] at [link={url}]{url}[/link]\n"
        f"Press [bold]Ctrl+C[/bold] to stop.",
        border_style="blue",
    ))

    if not no_open:
        import webbrowser
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[dim]Server stopped.[/dim]")
        server.server_close()


@app.command()
def clean(
    cache_dir: Path = typer.Option(Path(".gitstyle"), "--cache"),
):
    """Remove cached intermediate files."""
    import shutil
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        console.print(f"[green]Removed {cache_dir}[/green]")
    else:
        console.print("[dim]Nothing to clean[/dim]")


def _run_pipeline(config: GitStyleConfig) -> None:
    from gitstyle.compile import compile_wiki, evolve_wiki
    from gitstyle.extract import extract, merge_extractions
    from gitstyle.fetch import fetch
    from gitstyle.lint import lint
    from gitstyle.sample import sample
    from gitstyle.wiki_writer import write_wiki

    # Stage 1: Fetch (incremental-aware)
    console.rule("[bold blue]Stage 1: Fetch")
    fetch_result = fetch(config)
    if not fetch_result.all_commits:
        console.print(
            "[red]Error: No commits found.[/red]\n"
            "[dim]Check that the username is correct and has public repos with commits.\n"
            "If you previously ran this command and it failed, try: gitstyle clean[/dim]"
        )
        return

    # Decide: incremental or full pipeline
    has_existing_articles = config.articles_path().exists()
    has_new_commits = len(fetch_result.new_commits) > 0
    is_incremental = (
        fetch_result.is_incremental
        and has_new_commits
        and has_existing_articles
        and not config.fresh
    )

    if fetch_result.is_incremental and not has_new_commits:
        if has_existing_articles:
            console.print(
                "\n[green]No new commits since last run — wiki is up to date.[/green]\n"
                "[dim]Use --fresh to force a full rebuild.[/dim]"
            )
            return
        # Has cached commits but no articles — fall through to full pipeline

    if is_incremental:
        _run_incremental_pipeline(fetch_result, config)
    else:
        _run_full_pipeline(fetch_result.all_commits, config)


def _run_full_pipeline(commits: list, config: GitStyleConfig) -> None:
    """Standard full pipeline — analyze all commits from scratch."""
    from gitstyle.compile import compile_wiki
    from gitstyle.extract import extract
    from gitstyle.lint import lint
    from gitstyle.sample import sample
    from gitstyle.wiki_writer import write_wiki

    # Stage 2: Sample
    console.rule("[bold blue]Stage 2: Sample")
    clusters = sample(commits, config)
    if not clusters:
        console.print("[red]Error: No commit clusters to analyze.[/red]")
        return

    # Stage 3: Extract
    console.rule("[bold blue]Stage 3: Extract")
    extractions = extract(clusters, config)
    total_obs = sum(len(e.observations) for e in extractions)
    if total_obs == 0 and not config.dry_run:
        console.print(
            "[red]Error: LLM extraction produced 0 observations.[/red]\n"
            "[dim]This usually means your API key is invalid or the model returned errors.\n"
            "Check the error messages above and try: gitstyle clean[/dim]"
        )
        return

    # Stage 4: Compile
    console.rule("[bold blue]Stage 4: Compile")
    articles = compile_wiki(extractions, config)
    if not articles and not config.dry_run:
        console.print("[red]Error: No articles compiled.[/red]")
        return

    # Stage 5: Lint
    console.rule("[bold blue]Stage 5: Lint")
    lint_report = lint(articles, config)

    # Write wiki
    console.rule("[bold blue]Writing Wiki")
    wiki_path = write_wiki(articles, lint_report, config)

    console.print()
    console.print(Panel(
        f"[bold green]Done![/bold green]\n"
        f"Wiki written to [cyan]{wiki_path}[/cyan]\n"
        f"Open in Obsidian or any markdown viewer.",
        border_style="green",
    ))


def _run_incremental_pipeline(fetch_result, config: GitStyleConfig) -> None:
    """Incremental pipeline — process only new commits, evolve existing wiki."""
    from gitstyle.compile import evolve_wiki, _load_articles
    from gitstyle.extract import extract, merge_extractions, _load_extractions
    from gitstyle.lint import lint
    from gitstyle.sample import sample
    from gitstyle.wiki_writer import write_wiki

    new_commits = fetch_result.new_commits
    console.print(
        f"\n[bold cyan]Incremental mode:[/bold cyan] "
        f"processing {len(new_commits)} new commits"
    )

    # Stage 2: Sample NEW commits only (no caching — this is a delta)
    console.rule("[bold blue]Stage 2: Sample (new commits)")
    new_clusters = sample(new_commits, config, use_cache=False)
    if not new_clusters:
        console.print("[dim]No new clusters to analyze[/dim]")
        # Load existing articles and just re-serve them
        existing_articles = _load_articles(config.articles_path())
        lint_report = lint(existing_articles, config)
        write_wiki(existing_articles, lint_report, config)
        return

    # Stage 3: Extract from new clusters only (no caching)
    console.rule("[bold blue]Stage 3: Extract (new observations)")
    new_extractions = extract(new_clusters, config, use_cache=False)
    new_obs_count = sum(len(e.observations) for e in new_extractions)
    if new_obs_count == 0 and not config.dry_run:
        console.print("[yellow]No new observations extracted — keeping existing wiki[/yellow]")
        existing_articles = _load_articles(config.articles_path())
        lint_report = lint(existing_articles, config)
        write_wiki(existing_articles, lint_report, config)
        return

    # Merge new extractions into existing ones for the cache
    if config.extractions_path().exists():
        existing_extractions = _load_extractions(config.extractions_path())
        merged_extractions = merge_extractions(existing_extractions, new_extractions)
        # Update extractions cache
        import json
        with open(config.extractions_path(), "w") as f:
            json.dump([e.model_dump(mode="json") for e in merged_extractions], f, indent=2)

    # Stage 4: Evolve existing articles with new observations
    console.rule("[bold blue]Stage 4: Evolve Wiki")
    existing_articles = _load_articles(config.articles_path())
    articles = evolve_wiki(existing_articles, new_extractions, config)
    if not articles and not config.dry_run:
        console.print("[red]Error: Evolution produced no articles.[/red]")
        return

    # Invalidate stale caches (samples and lint are now stale)
    for stale in [config.samples_path(), config.lint_path()]:
        if stale.exists():
            stale.unlink()

    # Stage 5: Lint
    console.rule("[bold blue]Stage 5: Lint")
    lint_report = lint(articles, config)

    # Write wiki
    console.rule("[bold blue]Writing Wiki")
    wiki_path = write_wiki(articles, lint_report, config)

    console.print()
    console.print(Panel(
        f"[bold green]Wiki evolved![/bold green]\n"
        f"Incorporated [cyan]{len(new_commits)}[/cyan] new commits\n"
        f"Wiki written to [cyan]{wiki_path}[/cyan]",
        border_style="green",
    ))
