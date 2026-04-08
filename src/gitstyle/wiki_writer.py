"""Write compiled wiki articles to disk as markdown files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

from gitstyle.config import GitStyleConfig
from gitstyle.models import LintReport, WikiArticle

console = Console()


def write_wiki(
    articles: list[WikiArticle],
    lint_report: LintReport,
    config: GitStyleConfig,
) -> Path:
    """Write all articles to the output directory."""
    out = config.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "languages").mkdir(exist_ok=True)
    (out / "_meta").mkdir(exist_ok=True)

    console.print(f"[bold]Writing wiki to [cyan]{out}[/cyan]...[/bold]")

    # Write dimension articles
    for article in articles:
        if article.category == "language":
            path = out / "languages" / f"{article.slug}.md"
        else:
            path = out / f"{article.slug}.md"
        _write_article(path, article)

    # Write index
    _write_index(out, articles)

    # Write meta files
    _write_sources(out, articles)
    _write_generation_config(out, config)
    _write_log(out, articles, lint_report)

    total = len(articles) + 4  # +index, sources, config, log
    console.print(f"  Written [green]{total}[/green] files")
    return out


def _write_article(path: Path, article: WikiArticle) -> None:
    frontmatter = {
        "title": article.title,
        "category": article.category,
        "confidence": round(article.confidence, 2),
        "source_repos": article.source_repos,
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    fm_lines = ["---"]
    for k, v in frontmatter.items():
        if isinstance(v, list):
            fm_lines.append(f"{k}:")
            for item in v:
                fm_lines.append(f"  - {item}")
        else:
            fm_lines.append(f"{k}: {v}")
    fm_lines.append("---")
    fm_lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(fm_lines))
        f.write(article.content)
        f.write("\n")


def _write_index(out: Path, articles: list[WikiArticle]) -> None:
    lines = [
        "---",
        "title: Engineering Style Wiki",
        "category: index",
        f"last_updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Engineering Style Wiki",
        "",
        "## Style Dimensions",
        "",
    ]
    for a in articles:
        if a.category == "dimension":
            lines.append(f"- [[{a.slug}|{a.title}]] ({a.confidence:.0%} confidence)")
    lines.append("")
    lines.append("## Languages")
    lines.append("")
    for a in articles:
        if a.category == "language":
            lines.append(f"- [[languages/{a.slug}|{a.title}]] ({a.confidence:.0%} confidence)")
    lines.append("")
    lines.append("## Meta")
    lines.append("")
    lines.append("- [[_meta/sources|Sources]]")
    lines.append("- [[_meta/generation-config|Generation Config]]")
    lines.append("- [[_meta/log|Generation Log]]")
    lines.append("")

    with open(out / "index.md", "w") as f:
        f.write("\n".join(lines))


def _write_sources(out: Path, articles: list[WikiArticle]) -> None:
    repos: set[str] = set()
    for a in articles:
        repos.update(a.source_repos)

    lines = [
        "---",
        "title: Sources",
        "category: meta",
        f"last_updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Sources",
        "",
        "## Repositories Analyzed",
        "",
    ]
    for r in sorted(repos):
        lines.append(f"- [{r}](https://github.com/{r})")
    lines.append("")

    with open(out / "_meta" / "sources.md", "w") as f:
        f.write("\n".join(lines))


def _write_generation_config(out: Path, config: GitStyleConfig) -> None:
    lines = [
        "---",
        "title: Generation Config",
        "category: meta",
        f"last_updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Generation Config",
        "",
        f"- **Username:** {config.username}",
        f"- **Max commits:** {config.max_commits}",
        f"- **Samples per group:** {config.samples_per_group}",
        f"- **LLM model:** {config.llm_model}",
    ]
    if config.repos:
        lines.append(f"- **Filtered repos:** {', '.join(config.repos)}")
    if config.since:
        lines.append(f"- **Since:** {config.since}")
    if config.until:
        lines.append(f"- **Until:** {config.until}")
    lines.append("")

    with open(out / "_meta" / "generation-config.md", "w") as f:
        f.write("\n".join(lines))


def _write_log(out: Path, articles: list[WikiArticle], lint_report: LintReport) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "---",
        "title: Generation Log",
        "category: meta",
        f"last_updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Generation Log",
        "",
        f"**Generated at:** {now}",
        "",
        f"**Articles:** {len(articles)}",
        f"**Lint passed:** {'Yes' if lint_report.passed else 'No'}",
        "",
    ]
    if lint_report.issues:
        lines.append("## Lint Issues")
        lines.append("")
        for issue in lint_report.issues:
            lines.append(f"- **{issue.severity.value}** ({issue.article}): {issue.message}")
        lines.append("")

    with open(out / "_meta" / "log.md", "w") as f:
        f.write("\n".join(lines))
