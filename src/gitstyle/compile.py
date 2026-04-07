"""Compile stage — merge observations into wiki articles."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from rich.console import Console

from gitstyle.config import LLMConfig
from gitstyle.llm_client import LLMClient
from gitstyle.models import StyleExtractionResult, StyleObservation, WikiArticle

console = Console()

STYLE_CATEGORIES = {
    "code-structure": "Code Structure",
    "naming-conventions": "Naming Conventions",
    "patterns": "Patterns & Architecture",
    "type-discipline": "Type Discipline",
    "testing": "Testing",
    "comments-and-docs": "Comments & Documentation",
    "dependencies": "Dependencies",
    "commit-hygiene": "Commit Hygiene",
}

SYSTEM_PROMPT = """\
You are compiling a developer's engineering style wiki from structured observations \
extracted from their GitHub commit history.

You will receive a set of observations for a specific style category, collected across \
multiple repositories and languages. Synthesize them into a clear, well-structured \
wiki article.

Requirements:
- Write in third person ("The developer prefers..." not "You prefer...")
- Cite specific commits using [SHA] notation where applicable
- Use markdown formatting with headers, bullet points, and code examples where helpful
- Note confidence levels and flag any contradictions between observations
- Use [[wikilinks]] to cross-reference other style dimension articles
- Be specific and concrete, not generic

Return a JSON object with:
- title: article title
- content: full markdown content (without frontmatter — that's added separately)
- confidence: overall confidence ("low", "medium", "high")
- sources: array of repo names that contributed observations
- related: array of other article slugs that are referenced"""


LANGUAGE_SYSTEM_PROMPT = """\
You are compiling a language-specific style guide from a developer's GitHub commit history. \
You will receive observations specific to a programming language.

Write a focused wiki article covering this developer's idioms, patterns, and conventions \
in this language. Reference specific commits and cross-link to the core style dimension articles.

Return a JSON object with:
- title: article title (e.g. "Python Style")
- content: full markdown content
- confidence: overall confidence
- sources: array of repo names
- related: array of related article slugs"""


def _group_observations(
    extractions: list[StyleExtractionResult],
) -> tuple[dict[str, list[StyleObservation]], dict[str, list[StyleObservation]]]:
    """Group observations by category and by language."""
    by_category: dict[str, list[StyleObservation]] = defaultdict(list)
    by_language: dict[str, list[StyleObservation]] = defaultdict(list)

    for extraction in extractions:
        # Detect language from cluster label
        parts = extraction.cluster_label.rsplit(":", 1)
        lang = parts[1] if len(parts) == 2 else None

        for obs in extraction.observations:
            by_category[obs.category].append(obs)
            if lang and lang != "unknown":
                by_language[lang].append(obs)

    return by_category, by_language


def _format_observations_prompt(category: str, observations: list[StyleObservation]) -> str:
    lines = [
        f"Category: {category}",
        f"Total observations: {len(observations)}",
        "",
    ]
    for obs in observations:
        lines.append(f"- [{obs.confidence}] {obs.observation}")
        if obs.evidence:
            lines.append(f"  Evidence: {', '.join(obs.evidence[:5])}")
        lines.append(f"  Source cluster: {obs.cluster_label}")
        lines.append("")
    return "\n".join(lines)


def compile_category_article(
    slug: str,
    category_name: str,
    observations: list[StyleObservation],
    llm: LLMClient,
    cache_dir: Path | None = None,
) -> WikiArticle:
    """Compile observations for one category into a wiki article."""
    if cache_dir:
        cache_path = cache_dir / "articles" / f"{slug}.json"
        if cache_path.exists():
            return WikiArticle.model_validate_json(cache_path.read_text())

    prompt = _format_observations_prompt(category_name, observations)
    raw = llm.complete_json(SYSTEM_PROMPT, prompt, max_tokens=4096)

    sources = list({obs.cluster_label.rsplit(":", 1)[0] for obs in observations})

    article = WikiArticle(
        slug=slug,
        title=raw.get("title", category_name),
        category="style",
        content=raw.get("content", ""),
        sources=raw.get("sources", sources),
        confidence=raw.get("confidence", "medium"),
        related=raw.get("related", []),
    )

    if cache_dir:
        cache_path = cache_dir / "articles" / f"{slug}.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(article.model_dump_json(indent=2))

    return article


def compile_language_article(
    language: str,
    observations: list[StyleObservation],
    llm: LLMClient,
    cache_dir: Path | None = None,
) -> WikiArticle:
    """Compile language-specific observations into a wiki article."""
    slug = language.lower().replace(" ", "-")

    if cache_dir:
        cache_path = cache_dir / "articles" / f"lang-{slug}.json"
        if cache_path.exists():
            return WikiArticle.model_validate_json(cache_path.read_text())

    prompt = _format_observations_prompt(language, observations)
    raw = llm.complete_json(LANGUAGE_SYSTEM_PROMPT, prompt, max_tokens=4096)

    sources = list({obs.cluster_label.rsplit(":", 1)[0] for obs in observations})

    article = WikiArticle(
        slug=slug,
        title=raw.get("title", f"{language.title()} Style"),
        category="language",
        content=raw.get("content", ""),
        sources=raw.get("sources", sources),
        confidence=raw.get("confidence", "medium"),
        related=raw.get("related", []),
    )

    if cache_dir:
        cache_path = cache_dir / "articles" / f"lang-{slug}.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(article.model_dump_json(indent=2))

    return article


def run_compile(
    extractions: list[StyleExtractionResult],
    llm_config: LLMConfig,
    cache_dir: Path | None = None,
) -> list[WikiArticle]:
    """Compile all observations into wiki articles."""
    llm = LLMClient(llm_config)
    by_category, by_language = _group_observations(extractions)
    articles: list[WikiArticle] = []

    console.print("[bold]Compiling wiki articles...[/bold]")

    # Core style dimension articles
    for slug, display_name in STYLE_CATEGORIES.items():
        observations = by_category.get(slug, [])
        if not observations:
            continue
        console.print(f"  Writing {slug}...")
        article = compile_category_article(slug, display_name, observations, llm, cache_dir)
        articles.append(article)

    # Language-idioms get folded into language-specific articles
    idiom_obs = by_category.get("language-idioms", [])
    for obs in idiom_obs:
        parts = obs.cluster_label.rsplit(":", 1)
        if len(parts) == 2 and parts[1] != "unknown":
            by_language[parts[1]].append(obs)

    # Language-specific articles
    for lang, observations in by_language.items():
        if len(observations) < 2:  # Skip languages with very few observations
            continue
        console.print(f"  Writing languages/{lang}...")
        article = compile_language_article(lang, observations, llm, cache_dir)
        articles.append(article)

    console.print(f"[green]Compiled {len(articles)} wiki articles.[/green]")
    return articles
