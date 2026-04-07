"""Tests for configuration."""

import tempfile
from pathlib import Path

from gitstyle.config import GitStyleConfig


def test_config_defaults():
    c = GitStyleConfig(username="testuser")
    assert c.max_commits == 2000
    assert c.samples_per_group == 20
    assert c.output_dir == Path("wiki")
    assert c.cache_dir == Path(".gitstyle")
    assert c.dry_run is False


def test_config_paths():
    c = GitStyleConfig(username="test", cache_dir=Path("/tmp/gs"))
    assert c.commits_path() == Path("/tmp/gs/commits.jsonl")
    assert c.samples_path() == Path("/tmp/gs/samples.json")
    assert c.extractions_path() == Path("/tmp/gs/extractions.json")
    assert c.articles_path() == Path("/tmp/gs/articles.json")
    assert c.lint_path() == Path("/tmp/gs/lint.json")


def test_ensure_cache_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Path(tmpdir) / "deep" / "cache"
        c = GitStyleConfig(username="test", cache_dir=cache)
        c.ensure_cache_dir()
        assert cache.exists()
