"""Lint stage — LLM health check for contradictions and weak evidence."""

from __future__ import annotations

from rich.console import Console

from gitstyle.config import LLMConfig
from gitstyle.llm_client import LLMClient
from gitstyle.models import LintIssue, WikiArticle

console = Console()

SYSTEM_PROMPT = """\
You are a quality reviewer for an auto-generated engineering style wiki. \
Review the wiki articles for:

1. **Contradictions**: Statements in one article that conflict with another
2. **Weak evidence**: Claims that cite too few commits or seem speculative
3. **Missing categories**: Important style dimensions that aren't covered
4. **Vague statements**: Generic observations that could apply to any developer
5. **Broken cross-references**: [[wikilinks]] that reference non-existent articles

For each issue found, return a JSON array of objects with:
- article: slug of the affected article (or "general" for cross-cutting issues)
- severity: "info", "warning", or "error"
- message: clear description of the issue
- suggestion: how to fix it (or null)

If the wiki is clean, return an empty array []."""


def _format_wiki_for_review(articles: list[WikiArticle]) -> str:
    lines = [f"Wiki contains {len(articles)} articles:\n"]
    existing_slugs = {a.slug for a in articles}

    for article in articles:
        lines.append(f"=== {article.slug}.md (category: {article.category}, confidence: {article.confidence}) ===")
        lines.append(article.content)
        lines.append("")

    lines.append(f"\nAvailable article slugs: {', '.join(sorted(existing_slugs))}")
    return "\n".join(lines)


def run_lint(
    articles: list[WikiArticle],
    llm_config: LLMConfig,
) -> list[LintIssue]:
    """Run LLM lint pass on compiled wiki articles."""
    if not articles:
        return []

    llm = LLMClient(llm_config)
    console.print("[bold]Running lint pass on wiki articles...[/bold]")

    prompt = _format_wiki_for_review(articles)
    raw = llm.complete_json(SYSTEM_PROMPT, prompt, max_tokens=4096)

    issues = []
    for item in raw:
        issues.append(
            LintIssue(
                article=item.get("article", "general"),
                severity=item.get("severity", "info"),
                message=item.get("message", ""),
                suggestion=item.get("suggestion"),
            )
        )

    errors = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")
    infos = sum(1 for i in issues if i.severity == "info")

    if issues:
        console.print(f"[yellow]Lint: {errors} errors, {warnings} warnings, {infos} info[/yellow]")
        for issue in issues:
            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "•")
            console.print(f"  {icon} [{issue.article}] {issue.message}")
            if issue.suggestion:
                console.print(f"    → {issue.suggestion}")
    else:
        console.print("[green]Lint passed — no issues found.[/green]")

    return issues
