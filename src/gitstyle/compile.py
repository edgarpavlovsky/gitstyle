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


def compile_wiki(
    extractions: list[ClusterExtraction],
    config: GitStyleConfig,
) -> list[WikiArticle]:
    """Compile extractions into wiki articles."""
    config.ensure_cache_dir()
    cache = config.articles_path()

    if cache.exists():
        console.print(f"[dim]Using cached articles from {cache}[/dim]")
        return _load_articles(cache)

    # Group observations by dimension
    by_dimension: dict[StyleDimension, list[Observation]] = defaultdict(list)
    by_language: dict[str, list[Observation]] = defaultdict(list)
    all_repos: set[str] = set()

    for ext in extractions:
        all_repos.add(ext.repo)
        for obs in ext.observations:
            by_dimension[obs.dimension].append(obs)
            if obs.language and obs.dimension == StyleDimension.LANGUAGE_IDIOMS:
                by_language[obs.language].append(obs)

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

    # Cache
    with open(cache, "w") as f:
        json.dump([a.model_dump(mode="json") for a in articles], f, indent=2)

    console.print(f"  Compiled [green]{len(articles)}[/green] articles")
    return articles


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
