"""Stage 4: Compile — merge observations into markdown wiki articles."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from rich.console import Console

from gitstyle.config import GitStyleConfig
from gitstyle.llm_client import LLMClient
from gitstyle.models import (
    ClusterExtraction,
    Observation,
    StyleDimension,
    WikiArticle,
)

console = Console()

COMPILE_SYSTEM = """\
You are compiling a developer's engineering style wiki from extracted observations.

You will receive observations grouped by style dimension. Your job is to synthesize \
them into a single, coherent wiki article for that dimension.

Requirements:
- Write in third person ("The developer tends to...")
- Use Obsidian-compatible `[[wikilinks]]` to cross-reference other dimensions
- Cite specific commit SHAs inline as evidence (format: `[abc1234]`)
- Include a confidence assessment
- Be specific and concrete — avoid vague generalities
- If observations conflict, note the contradiction and which has stronger evidence

Return valid JSON:
{
  "title": "...",
  "content": "... markdown body ...",
  "confidence": 0.0-1.0,
  "wikilinks": ["other-dimension-slug", ...]
}\
"""

LANGUAGE_COMPILE_SYSTEM = """\
You are compiling a language-specific engineering style article from observations.

Write about the developer's idiomatic usage, patterns, and preferences specific to \
this programming language. Cross-reference universal style dimensions with `[[wikilinks]]`.

Cite commit SHAs inline. Be specific.

Return valid JSON:
{
  "title": "...",
  "content": "... markdown body ...",
  "confidence": 0.0-1.0,
  "wikilinks": ["other-slug", ...]
}\
"""

EVOLVE_SYSTEM = """\
You are updating a developer's engineering style wiki article with new information \
from recent commits.

You have an existing article (written from earlier analysis) and new observations \
from recent commits. Your job is to EVOLVE the article:

- Preserve insights from the existing article that remain valid
- Incorporate new observations naturally into the existing text
- If new observations contradict existing claims, note the evolution \
("Initially X, but recent commits suggest Y")
- If new observations reinforce existing claims, strengthen the evidence and \
increase confidence
- Add new sections if the observations reveal genuinely new patterns
- Cite new commit SHAs inline as evidence (format: `[abc1234]`)
- Keep the same writing style (third person, specific, evidence-based)
- Use Obsidian-compatible `[[wikilinks]]` for cross-references

Return valid JSON:
{
  "title": "...",
  "content": "... updated markdown body ...",
  "confidence": 0.0-1.0,
  "wikilinks": ["other-slug", ...],
  "changes_summary": "brief description of what changed"
}\
"""

EVOLVE_LANGUAGE_SYSTEM = """\
You are updating a language-specific engineering style article with new information \
from recent commits.

You have an existing article and new observations. Evolve the article — preserve \
what's valid, incorporate new patterns, note contradictions, strengthen confirmed \
patterns. Cite new commit SHAs inline.

Return valid JSON:
{
  "title": "...",
  "content": "... updated markdown body ...",
  "confidence": 0.0-1.0,
  "wikilinks": ["other-slug", ...],
  "changes_summary": "brief description of what changed"
}\
"""


def compile_wiki(
    extractions: list[ClusterExtraction],
    config: GitStyleConfig,
) -> list[WikiArticle]:
    """Compile extractions into wiki articles (full run)."""
    config.ensure_cache_dir()
    cache = config.articles_path()

    if cache.exists():
        console.print(f"[dim]Using cached articles from {cache}[/dim]")
        return _load_articles(cache)

    by_dimension, by_language, all_repos = _group_observations(extractions)

    # Estimate cost
    total_calls = len(by_dimension) + len(by_language)
    console.print(f"[bold]Compile stage:[/bold] {total_calls} LLM calls")
    if config.dry_run:
        console.print("[yellow]Dry run — skipping LLM calls[/yellow]")
        return []

    llm = LLMClient(model=config.llm_model)
    articles: list[WikiArticle] = []
    repos_list = sorted(all_repos)

    # Compile dimension articles
    for dim in StyleDimension:
        obs_list = by_dimension.get(dim, [])
        if not obs_list:
            continue
        console.print(f"  Compiling [cyan]{dim.value}[/cyan]...")
        prompt = _build_dimension_prompt(dim, obs_list)
        try:
            data = llm.complete_json(COMPILE_SYSTEM, prompt)
            articles.append(WikiArticle(
                slug=dim.value,
                title=data.get("title", dim.value.replace("-", " ").title()),
                category="dimension",
                confidence=data.get("confidence", 0.5),
                source_repos=repos_list,
                content=data.get("content", ""),
                wikilinks=data.get("wikilinks", []),
            ))
        except Exception as e:
            console.print(f"[red]  Error compiling {dim.value}: {e}[/red]")

    # Compile language articles
    for lang, obs_list in sorted(by_language.items()):
        if not obs_list:
            continue
        slug = lang.lower().replace(" ", "-").replace("#", "sharp").replace("+", "plus")
        console.print(f"  Compiling language: [cyan]{lang}[/cyan]...")
        prompt = _build_language_prompt(lang, obs_list)
        try:
            data = llm.complete_json(LANGUAGE_COMPILE_SYSTEM, prompt)
            articles.append(WikiArticle(
                slug=slug,
                title=data.get("title", f"{lang} Style"),
                category="language",
                confidence=data.get("confidence", 0.5),
                source_repos=repos_list,
                content=data.get("content", ""),
                wikilinks=data.get("wikilinks", []),
            ))
        except Exception as e:
            console.print(f"[red]  Error compiling {lang}: {e}[/red]")

    if not articles:
        console.print("[yellow]  Warning: 0 articles compiled (not caching empty result)[/yellow]")
        return articles

    # Cache
    with open(cache, "w") as f:
        json.dump([a.model_dump(mode="json") for a in articles], f, indent=2)

    console.print(f"  Compiled [green]{len(articles)}[/green] articles")
    return articles


def evolve_wiki(
    existing_articles: list[WikiArticle],
    new_extractions: list[ClusterExtraction],
    config: GitStyleConfig,
) -> list[WikiArticle]:
    """Evolve existing wiki articles with new observations from recent commits.

    This is the incremental compile path — instead of writing articles from scratch,
    the LLM updates existing articles by incorporating new observations.
    """
    by_dimension, by_language, new_repos = _group_observations(new_extractions)

    # Build lookup of existing articles by slug
    existing_by_slug: dict[str, WikiArticle] = {a.slug: a for a in existing_articles}

    total_new_obs = sum(len(obs) for obs in by_dimension.values()) + \
        sum(len(obs) for obs in by_language.values())
    if total_new_obs == 0:
        console.print("[dim]  No new observations to incorporate[/dim]")
        return existing_articles

    # Count how many articles will be evolved vs created
    evolve_count = 0
    create_count = 0
    for dim in StyleDimension:
        if by_dimension.get(dim):
            if dim.value in existing_by_slug:
                evolve_count += 1
            else:
                create_count += 1
    for lang in by_language:
        slug = lang.lower().replace(" ", "-").replace("#", "sharp").replace("+", "plus")
        if slug in existing_by_slug:
            evolve_count += 1
        else:
            create_count += 1

    total_calls = evolve_count + create_count
    console.print(
        f"[bold]Evolve stage:[/bold] {total_calls} LLM calls "
        f"({evolve_count} evolve, {create_count} new)"
    )
    if config.dry_run:
        console.print("[yellow]Dry run — skipping LLM calls[/yellow]")
        return existing_articles

    llm = LLMClient(model=config.llm_model)
    evolved_articles: list[WikiArticle] = []
    changes: list[str] = []

    # Evolve/create dimension articles
    for dim in StyleDimension:
        new_obs = by_dimension.get(dim, [])
        existing_article = existing_by_slug.get(dim.value)

        if existing_article and new_obs:
            # Evolve existing article with new observations
            console.print(f"  Evolving [cyan]{dim.value}[/cyan]...")
            article = _evolve_dimension_article(
                llm, existing_article, new_obs, new_repos,
            )
            if article:
                evolved_articles.append(article)
                changes.append(f"  evolved {dim.value}")
            else:
                evolved_articles.append(existing_article)
        elif not existing_article and new_obs:
            # New dimension not seen before — compile from scratch
            console.print(f"  Creating new [cyan]{dim.value}[/cyan]...")
            prompt = _build_dimension_prompt(dim, new_obs)
            try:
                data = llm.complete_json(COMPILE_SYSTEM, prompt)
                evolved_articles.append(WikiArticle(
                    slug=dim.value,
                    title=data.get("title", dim.value.replace("-", " ").title()),
                    category="dimension",
                    confidence=data.get("confidence", 0.5),
                    source_repos=sorted(new_repos),
                    content=data.get("content", ""),
                    wikilinks=data.get("wikilinks", []),
                ))
                changes.append(f"  created {dim.value}")
            except Exception as e:
                console.print(f"[red]  Error creating {dim.value}: {e}[/red]")
        elif existing_article:
            # No new observations — keep as-is
            evolved_articles.append(existing_article)

    # Evolve/create language articles
    for lang, new_obs in sorted(by_language.items()):
        slug = lang.lower().replace(" ", "-").replace("#", "sharp").replace("+", "plus")
        existing_article = existing_by_slug.get(slug)

        if existing_article and new_obs:
            console.print(f"  Evolving language: [cyan]{lang}[/cyan]...")
            article = _evolve_language_article(
                llm, existing_article, lang, new_obs, new_repos,
            )
            if article:
                evolved_articles.append(article)
                changes.append(f"  evolved {lang}")
            else:
                evolved_articles.append(existing_article)
        elif not existing_article and new_obs:
            console.print(f"  Creating language: [cyan]{lang}[/cyan]...")
            prompt = _build_language_prompt(lang, new_obs)
            try:
                data = llm.complete_json(LANGUAGE_COMPILE_SYSTEM, prompt)
                evolved_articles.append(WikiArticle(
                    slug=slug,
                    title=data.get("title", f"{lang} Style"),
                    category="language",
                    confidence=data.get("confidence", 0.5),
                    source_repos=sorted(new_repos),
                    content=data.get("content", ""),
                    wikilinks=data.get("wikilinks", []),
                ))
                changes.append(f"  created {lang}")
            except Exception as e:
                console.print(f"[red]  Error creating {lang}: {e}[/red]")
        elif existing_article:
            evolved_articles.append(existing_article)

    # Also include any existing articles for dimensions/languages we didn't touch
    evolved_slugs = {a.slug for a in evolved_articles}
    for article in existing_articles:
        if article.slug not in evolved_slugs:
            evolved_articles.append(article)

    if changes:
        console.print(f"  [green]Wiki evolved:[/green]")
        for c in changes:
            console.print(f"    {c}")

    # Update the articles cache
    cache = config.articles_path()
    with open(cache, "w") as f:
        json.dump([a.model_dump(mode="json") for a in evolved_articles], f, indent=2)

    return evolved_articles


def _evolve_dimension_article(
    llm: LLMClient,
    existing: WikiArticle,
    new_observations: list[Observation],
    new_repos: set[str],
) -> WikiArticle | None:
    """Evolve a single dimension article with new observations."""
    prompt = _build_evolve_prompt(existing, new_observations)
    try:
        data = llm.complete_json(EVOLVE_SYSTEM, prompt)
        repos = sorted(set(existing.source_repos) | new_repos)
        return WikiArticle(
            slug=existing.slug,
            title=data.get("title", existing.title),
            category="dimension",
            confidence=data.get("confidence", existing.confidence),
            source_repos=repos,
            content=data.get("content", existing.content),
            wikilinks=data.get("wikilinks", existing.wikilinks),
        )
    except Exception as e:
        console.print(f"[red]  Error evolving {existing.slug}: {e}[/red]")
        return None


def _evolve_language_article(
    llm: LLMClient,
    existing: WikiArticle,
    language: str,
    new_observations: list[Observation],
    new_repos: set[str],
) -> WikiArticle | None:
    """Evolve a single language article with new observations."""
    prompt = _build_evolve_prompt(existing, new_observations)
    try:
        data = llm.complete_json(EVOLVE_LANGUAGE_SYSTEM, prompt)
        repos = sorted(set(existing.source_repos) | new_repos)
        return WikiArticle(
            slug=existing.slug,
            title=data.get("title", existing.title),
            category="language",
            confidence=data.get("confidence", existing.confidence),
            source_repos=repos,
            content=data.get("content", existing.content),
            wikilinks=data.get("wikilinks", existing.wikilinks),
        )
    except Exception as e:
        console.print(f"[red]  Error evolving {existing.slug} ({language}): {e}[/red]")
        return None


def _build_evolve_prompt(
    existing: WikiArticle, new_observations: list[Observation],
) -> str:
    """Build prompt for evolving an existing article with new observations."""
    lines = [
        "## Existing Article",
        f"Title: {existing.title}",
        f"Current confidence: {existing.confidence:.0%}",
        "",
        existing.content,
        "",
        "---",
        "",
        "## New Observations from Recent Commits",
        f"Total new observations: {len(new_observations)}",
        "",
    ]
    for i, obs in enumerate(new_observations, 1):
        lines.append(f"{i}. [{obs.confidence:.0%} confidence] ({obs.dimension.value})")
        lines.append(f"   Claim: {obs.claim}")
        lines.append(f"   Evidence: {', '.join(obs.evidence)}")
        if obs.language:
            lines.append(f"   Language: {obs.language}")
        lines.append("")
    return "\n".join(lines)


def _group_observations(
    extractions: list[ClusterExtraction],
) -> tuple[
    dict[StyleDimension, list[Observation]],
    dict[str, list[Observation]],
    set[str],
]:
    """Group observations by dimension and by language. Returns (by_dimension, by_language, repos)."""
    by_dimension: dict[StyleDimension, list[Observation]] = defaultdict(list)
    by_language: dict[str, list[Observation]] = defaultdict(list)
    all_repos: set[str] = set()

    for ext in extractions:
        all_repos.add(ext.repo)
        for obs in ext.observations:
            by_dimension[obs.dimension].append(obs)
            if obs.language and obs.dimension == StyleDimension.LANGUAGE_IDIOMS:
                by_language[obs.language].append(obs)

    return by_dimension, by_language, all_repos


def _build_dimension_prompt(dim: StyleDimension, observations: list[Observation]) -> str:
    lines = [
        f"Dimension: {dim.value}",
        f"Total observations: {len(observations)}",
        "",
        "Observations:",
    ]
    for i, obs in enumerate(observations, 1):
        lines.append(f"\n{i}. [{obs.confidence:.0%} confidence]")
        lines.append(f"   Claim: {obs.claim}")
        lines.append(f"   Evidence: {', '.join(obs.evidence)}")
        if obs.language:
            lines.append(f"   Language: {obs.language}")
    return "\n".join(lines)


def _build_language_prompt(language: str, observations: list[Observation]) -> str:
    lines = [
        f"Language: {language}",
        f"Total observations: {len(observations)}",
        "",
        "Observations:",
    ]
    for i, obs in enumerate(observations, 1):
        lines.append(f"\n{i}. [{obs.confidence:.0%} confidence] ({obs.dimension.value})")
        lines.append(f"   Claim: {obs.claim}")
        lines.append(f"   Evidence: {', '.join(obs.evidence)}")
    return "\n".join(lines)


def _load_articles(path: Path) -> list[WikiArticle]:
    with open(path) as f:
        data = json.load(f)
    return [WikiArticle.model_validate(d) for d in data]
