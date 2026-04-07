"""Write wiki articles to disk as markdown with YAML frontmatter."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from gitstyle.models import WikiArticle


def write_article(article: WikiArticle, output_dir: Path) -> Path:
    """Write a single wiki article to the output directory."""
    # Determine subdirectory
    if article.category == "language":
        dest_dir = output_dir / "languages"
    elif article.category == "meta":
        dest_dir = output_dir / "_meta"
    else:
        dest_dir = output_dir

    dest_dir.mkdir(parents=True, exist_ok=True)
    filepath = dest_dir / f"{article.slug}.md"

    frontmatter = [
        "---",
        f"title: \"{article.title}\"",
        f"category: {article.category}",
        f"confidence: {article.confidence}",
        f"sources: [{', '.join(article.sources)}]",
        f"related: [{', '.join(article.related)}]",
        f"last_updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "---",
    ]

    content = "\n".join(frontmatter) + "\n\n" + article.content + "\n"
    filepath.write_text(content, encoding="utf-8")
    return filepath


def write_index(articles: list[WikiArticle], output_dir: Path) -> Path:
    """Write the master index.md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / "index.md"

    lines = [
        "---",
        "title: \"Engineering Style Wiki\"",
        "category: index",
        f"last_updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Engineering Style Wiki",
        "",
        "## Style Dimensions",
        "",
    ]

    core = [a for a in articles if a.category not in ("language", "meta")]
    langs = [a for a in articles if a.category == "language"]

    for a in sorted(core, key=lambda x: x.slug):
        lines.append(f"- [[{a.slug}]] — {a.title}")

    if langs:
        lines.append("")
        lines.append("## Language-Specific")
        lines.append("")
        for a in sorted(langs, key=lambda x: x.slug):
            lines.append(f"- [[languages/{a.slug}]] — {a.title}")

    lines.append("")
    lines.append("## Meta")
    lines.append("")
    lines.append("- [[_meta/sources]] — Data sources and commit counts")
    lines.append("- [[_meta/generation-config]] — Pipeline configuration")
    lines.append("- [[_meta/log]] — Generation log")
    lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath


def write_meta(
    config_snapshot: dict,
    stats: dict,
    log_entries: list[str],
    output_dir: Path,
) -> None:
    """Write _meta/ files."""
    meta_dir = output_dir / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    # sources.md
    sources_lines = [
        "---",
        "title: \"Data Sources\"",
        "category: meta",
        "---",
        "",
        "# Data Sources",
        "",
    ]
    for repo, count in sorted(stats.get("repos", {}).items()):
        sources_lines.append(f"- **{repo}**: {count} commits analyzed")
    sources_lines.append("")
    sources_lines.append(f"**Total commits fetched:** {stats.get('total_fetched', 0)}")
    sources_lines.append(f"**Total commits sampled:** {stats.get('total_sampled', 0)}")
    sources_lines.append("")
    (meta_dir / "sources.md").write_text("\n".join(sources_lines), encoding="utf-8")

    # generation-config.md
    import json

    config_lines = [
        "---",
        "title: \"Generation Config\"",
        "category: meta",
        "---",
        "",
        "# Generation Configuration",
        "",
        "```json",
        json.dumps(config_snapshot, indent=2, default=str),
        "```",
        "",
    ]
    (meta_dir / "generation-config.md").write_text(
        "\n".join(config_lines), encoding="utf-8"
    )

    # log.md
    log_lines = [
        "---",
        "title: \"Generation Log\"",
        "category: meta",
        "---",
        "",
        "# Generation Log",
        "",
    ]
    for entry in log_entries:
        log_lines.append(f"- {entry}")
    log_lines.append("")
    (meta_dir / "log.md").write_text("\n".join(log_lines), encoding="utf-8")
