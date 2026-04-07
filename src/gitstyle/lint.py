"""Stage 5: Lint — LLM health check for wiki quality."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from gitstyle.config import GitStyleConfig
from gitstyle.llm_client import LLMClient
from gitstyle.models import LintIssue, LintReport, LintSeverity, WikiArticle

console = Console()

LINT_SYSTEM = """\
You are a quality checker for a developer engineering style wiki. Review the wiki \
articles for:

1. Contradictions — claims in one article that conflict with another
2. Weak evidence — claims citing only 1 commit or with low confidence
3. Missing categories — style dimensions that should be covered but aren't
4. Vague claims — observations too generic to be useful
5. Cross-reference errors — wikilinks to articles that don't exist

For each issue found, provide:
- article: the slug of the article with the issue
- severity: "info", "warning", or "error"
- message: description of the issue
- suggestion: how to fix it

Return valid JSON: {"issues": [...], "passed": true/false}\
"""


def lint(articles: list[WikiArticle], config: GitStyleConfig) -> LintReport:
    """Run LLM lint pass on compiled articles."""
    config.ensure_cache_dir()
    cache = config.lint_path()

    if cache.exists():
        console.print(f"[dim]Using cached lint from {cache}[/dim]")
        return _load_lint(cache)

    if not articles:
        console.print("[yellow]No articles to lint[/yellow]")
        return LintReport()

    llm = LLMClient(model=config.llm_model)

    console.print("[bold]Lint stage:[/bold] 1 LLM call")
    if config.dry_run:
        console.print("[yellow]Dry run — skipping LLM lint[/yellow]")
        return LintReport()

    prompt = _build_lint_prompt(articles)
    try:
        data = llm.complete_json(LINT_SYSTEM, prompt)
        issues = [LintIssue.model_validate(i) for i in data.get("issues", [])]
        report = LintReport(issues=issues, passed=data.get("passed", len(issues) == 0))
    except Exception as e:
        console.print(f"[red]  Lint error: {e}[/red]")
        report = LintReport(
            issues=[LintIssue(
                article="_meta",
                severity=LintSeverity.ERROR,
                message=f"Lint failed: {e}",
            )],
            passed=False,
        )

    # Cache
    with open(cache, "w") as f:
        f.write(report.model_dump_json(indent=2))

    _print_report(report)
    return report


def _build_lint_prompt(articles: list[WikiArticle]) -> str:
    lines = [f"Wiki contains {len(articles)} articles:\n"]
    existing_slugs = {a.slug for a in articles}
    for a in articles:
        lines.append(f"## {a.slug} (confidence: {a.confidence:.0%})")
        lines.append(f"Category: {a.category}")
        lines.append(f"Wikilinks: {', '.join(a.wikilinks)}")
        lines.append(a.content[:2000])  # cap for token budget
        lines.append("")
    lines.append(f"\nExisting article slugs: {', '.join(sorted(existing_slugs))}")
    return "\n".join(lines)


def _print_report(report: LintReport) -> None:
    if report.passed:
        console.print("  [green]✓ Lint passed[/green]")
    else:
        console.print("  [red]✗ Lint found issues:[/red]")
    for issue in report.issues:
        icon = {"info": "ℹ", "warning": "⚠", "error": "✗"}[issue.severity.value]
        color = {"info": "blue", "warning": "yellow", "error": "red"}[issue.severity.value]
        console.print(f"    [{color}]{icon} {issue.article}: {issue.message}[/{color}]")
        if issue.suggestion:
            console.print(f"      → {issue.suggestion}")


def _load_lint(path: Path) -> LintReport:
    with open(path) as f:
        return LintReport.model_validate_json(f.read())
