"""Tests for the compile stage."""

from pathlib import Path
from unittest.mock import MagicMock

from gitstyle.models import StyleExtractionResult, StyleObservation, WikiArticle
from gitstyle.compile import compile_category_article, _group_observations


def _make_extraction(category: str, obs_text: str, cluster: str = "user/repo:python") -> StyleExtractionResult:
    return StyleExtractionResult(
        cluster_label=cluster,
        observations=[
            StyleObservation(
                cluster_label=cluster,
                category=category,
                observation=obs_text,
                evidence=["sha1"],
                confidence="high",
            )
        ],
    )


def test_group_observations():
    extractions = [
        _make_extraction("naming-conventions", "Uses snake_case"),
        _make_extraction("naming-conventions", "PascalCase for classes"),
        _make_extraction("testing", "Uses pytest"),
    ]
    by_category, by_language = _group_observations(extractions)
    assert len(by_category["naming-conventions"]) == 2
    assert len(by_category["testing"]) == 1


def test_compile_category_article(tmp_path: Path):
    llm = MagicMock()
    llm.complete_json.return_value = {
        "title": "Naming Conventions",
        "content": "# Naming\n\nThe developer uses snake_case.",
        "confidence": "high",
        "sources": ["user/repo"],
        "related": ["code-structure"],
    }

    observations = [
        StyleObservation(
            cluster_label="user/repo:python",
            category="naming-conventions",
            observation="Uses snake_case",
            evidence=["abc123"],
            confidence="high",
        )
    ]

    article = compile_category_article("naming-conventions", "Naming Conventions", observations, llm, tmp_path)
    assert isinstance(article, WikiArticle)
    assert article.slug == "naming-conventions"
    assert "snake_case" in article.content

    # Verify cache was written
    cache_path = tmp_path / "articles" / "naming-conventions.json"
    assert cache_path.exists()


def test_compile_uses_cache(tmp_path: Path):
    cached = WikiArticle(
        slug="testing",
        title="Testing",
        category="style",
        content="Cached article content",
        confidence="medium",
    )
    cache_path = tmp_path / "articles" / "testing.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text(cached.model_dump_json(indent=2))

    llm = MagicMock()
    observations = [
        StyleObservation(
            cluster_label="user/repo:python",
            category="testing",
            observation="Uses pytest",
            evidence=["sha1"],
        )
    ]

    article = compile_category_article("testing", "Testing", observations, llm, tmp_path)
    assert article.content == "Cached article content"
    llm.complete_json.assert_not_called()
