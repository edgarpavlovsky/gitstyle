"""Tests for wiki writer."""

import tempfile
from pathlib import Path

from gitstyle.config import GitStyleConfig
from gitstyle.models import LintReport, WikiArticle
from gitstyle.wiki_writer import write_wiki


def test_write_wiki_creates_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "wiki"
        config = GitStyleConfig(username="test", output_dir=out, cache_dir=Path(tmpdir) / ".gs")
        articles = [
            WikiArticle(
                slug="naming-conventions",
                title="Naming Conventions",
                category="dimension",
                confidence=0.85,
                source_repos=["u/r"],
                content="# Naming\nUses snake_case.",
                wikilinks=["code-structure"],
            ),
            WikiArticle(
                slug="python",
                title="Python Style",
                category="language",
                confidence=0.8,
                source_repos=["u/r"],
                content="# Python\nIdiomatic usage.",
            ),
        ]
        lint_report = LintReport()

        result = write_wiki(articles, lint_report, config)

        assert (result / "index.md").exists()
        assert (result / "naming-conventions.md").exists()
        assert (result / "languages" / "python.md").exists()
        assert (result / "_meta" / "sources.md").exists()
        assert (result / "_meta" / "generation-config.md").exists()
        assert (result / "_meta" / "log.md").exists()

        # Check frontmatter in dimension article
        content = (result / "naming-conventions.md").read_text()
        assert "---" in content
        assert "title: Naming Conventions" in content
        assert "confidence: 0.85" in content

        # Check index has wikilinks
        index = (result / "index.md").read_text()
        assert "[[naming-conventions" in index
        assert "[[languages/python" in index
