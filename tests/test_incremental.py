"""Tests for incremental synthesis feature.

Covers: FetchResult model, incremental fetch, sample/extract with use_cache,
merge_extractions, _group_observations, _build_evolve_prompt, evolve_wiki dry_run,
and CLI-level incremental pipeline routing.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from gitstyle.cli import app
from gitstyle.compile import (
    _build_evolve_prompt,
    _group_observations,
    evolve_wiki,
)
from gitstyle.config import GitStyleConfig
from gitstyle.extract import merge_extractions
from gitstyle.models import (
    ClusterExtraction,
    FetchResult,
    Observation,
    RawCommit,
    SampledCluster,
    StyleDimension,
    WikiArticle,
)

runner = CliRunner()

_BASE_DATE = datetime(2025, 12, 31, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_commit(
    sha: str,
    repo: str = "user/repo",
    additions: int = 5,
    days_ago: int = 0,
    languages: list[str] | None = None,
) -> RawCommit:
    return RawCommit(
        sha=sha,
        repo=repo,
        message=f"commit {sha}",
        author="user",
        authored_at=_BASE_DATE - timedelta(days=days_ago),
        additions=additions,
        deletions=0,
        languages=languages or ["Python"],
    )


def _make_observation(
    dimension: StyleDimension = StyleDimension.CODE_STRUCTURE,
    claim: str = "Uses small functions",
    evidence: list[str] | None = None,
    confidence: float = 0.8,
    language: str | None = None,
) -> Observation:
    return Observation(
        dimension=dimension,
        claim=claim,
        evidence=evidence or ["abc1234"],
        confidence=confidence,
        language=language,
    )


def _make_extraction(
    repo: str = "user/repo",
    language: str = "Python",
    observations: list[Observation] | None = None,
) -> ClusterExtraction:
    return ClusterExtraction(
        repo=repo,
        language=language,
        observations=[_make_observation()] if observations is None else observations,
    )


def _make_article(
    slug: str = "code-structure",
    title: str = "Code Structure",
    category: str = "dimension",
    confidence: float = 0.8,
    content: str = "The developer uses small, focused functions.",
    source_repos: list[str] | None = None,
    wikilinks: list[str] | None = None,
) -> WikiArticle:
    return WikiArticle(
        slug=slug,
        title=title,
        category=category,
        confidence=confidence,
        source_repos=source_repos or ["user/repo"],
        content=content,
        wikilinks=wikilinks or [],
    )


def _make_config(cache_dir: Path, **kwargs) -> GitStyleConfig:
    defaults = dict(
        username="testuser",
        cache_dir=cache_dir,
        output_dir=cache_dir / "wiki",
        dry_run=False,
        fresh=False,
    )
    defaults.update(kwargs)
    return GitStyleConfig(**defaults)


def _save_commits_to_cache(path: Path, commits: list[RawCommit]) -> None:
    """Write commits in JSONL format, matching _save_commits in fetch.py."""
    with open(path, "w") as f:
        for c in commits:
            f.write(c.model_dump_json() + "\n")


def _save_articles_to_cache(path: Path, articles: list[WikiArticle]) -> None:
    with open(path, "w") as f:
        json.dump([a.model_dump(mode="json") for a in articles], f, indent=2)


def _save_extractions_to_cache(path: Path, extractions: list[ClusterExtraction]) -> None:
    with open(path, "w") as f:
        json.dump([e.model_dump(mode="json") for e in extractions], f, indent=2)


# ===========================================================================
# 1. FetchResult model
# ===========================================================================

class TestFetchResultModel:
    def test_creation_basic(self):
        commits = [_make_commit("aaa"), _make_commit("bbb")]
        result = FetchResult(all_commits=commits, new_commits=[commits[1]])
        assert len(result.all_commits) == 2
        assert len(result.new_commits) == 1
        assert result.new_commits[0].sha == "bbb"

    def test_is_incremental_default(self):
        result = FetchResult(all_commits=[], new_commits=[])
        assert result.is_incremental is False

    def test_is_incremental_true(self):
        result = FetchResult(
            all_commits=[_make_commit("a")],
            new_commits=[],
            is_incremental=True,
        )
        assert result.is_incremental is True

    def test_empty_new_commits(self):
        existing = [_make_commit("x"), _make_commit("y")]
        result = FetchResult(
            all_commits=existing,
            new_commits=[],
            is_incremental=True,
        )
        assert len(result.all_commits) == 2
        assert len(result.new_commits) == 0


# ===========================================================================
# 2. Incremental fetch
# ===========================================================================

class TestIncrementalFetch:
    def test_fresh_flag_forces_fresh_fetch(self):
        """When cache has commits and fresh=True, does a fresh fetch (not incremental)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, fresh=True, github_token="fake")

            # Pre-populate cache
            existing = [_make_commit("old1", days_ago=10), _make_commit("old2", days_ago=5)]
            config.ensure_cache_dir()
            _save_commits_to_cache(config.commits_path(), existing)

            fresh_commits = [_make_commit("fresh1"), _make_commit("fresh2"), _make_commit("fresh3")]

            with patch("gitstyle.fetch._fetch_from_github", return_value=fresh_commits):
                from gitstyle.fetch import fetch
                result = fetch(config)

            # Should be a fresh fetch, not incremental
            assert result.is_incremental is False
            assert len(result.all_commits) == 3
            assert len(result.new_commits) == 3
            assert {c.sha for c in result.all_commits} == {"fresh1", "fresh2", "fresh3"}

    def test_cache_exists_returns_incremental(self):
        """When cache has commits and fresh=False, returns is_incremental=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, fresh=False, github_token="fake")

            existing = [_make_commit("old1", days_ago=10)]
            config.ensure_cache_dir()
            _save_commits_to_cache(config.commits_path(), existing)

            new_from_api = [_make_commit("new1", days_ago=0)]

            with patch("gitstyle.fetch._fetch_from_github", return_value=new_from_api):
                from gitstyle.fetch import fetch
                result = fetch(config)

            assert result.is_incremental is True
            assert len(result.new_commits) == 1
            assert result.new_commits[0].sha == "new1"

    def test_deduplication(self):
        """New commits with same SHA as existing are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, fresh=False, github_token="fake")

            existing = [_make_commit("dup1", days_ago=5), _make_commit("old2", days_ago=10)]
            config.ensure_cache_dir()
            _save_commits_to_cache(config.commits_path(), existing)

            # API returns one dup and one new
            api_result = [_make_commit("dup1", days_ago=5), _make_commit("brand_new", days_ago=0)]

            with patch("gitstyle.fetch._fetch_from_github", return_value=api_result):
                from gitstyle.fetch import fetch
                result = fetch(config)

            assert result.is_incremental is True
            # Only the truly new commit should appear in new_commits
            assert len(result.new_commits) == 1
            assert result.new_commits[0].sha == "brand_new"
            # All commits = existing + new (not including duplicates)
            all_shas = {c.sha for c in result.all_commits}
            assert all_shas == {"dup1", "old2", "brand_new"}

    def test_merge_appends_new(self):
        """New commits are appended to existing ones after dedup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, fresh=False, github_token="fake")

            existing = [_make_commit("a", days_ago=10), _make_commit("b", days_ago=5)]
            config.ensure_cache_dir()
            _save_commits_to_cache(config.commits_path(), existing)

            new_from_api = [_make_commit("c", days_ago=1), _make_commit("d", days_ago=0)]

            with patch("gitstyle.fetch._fetch_from_github", return_value=new_from_api):
                from gitstyle.fetch import fetch
                result = fetch(config)

            assert len(result.all_commits) == 4
            assert len(result.new_commits) == 2
            # Order: existing + new
            shas = [c.sha for c in result.all_commits]
            assert shas == ["a", "b", "c", "d"]

    def test_graceful_fallback_on_api_error(self):
        """When API fails during incremental, falls back to cached commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, fresh=False, github_token="fake")

            existing = [_make_commit("cached1", days_ago=5), _make_commit("cached2", days_ago=3)]
            config.ensure_cache_dir()
            _save_commits_to_cache(config.commits_path(), existing)

            with patch(
                "gitstyle.fetch._fetch_from_github",
                side_effect=Exception("API is down"),
            ):
                from gitstyle.fetch import fetch
                result = fetch(config)

            assert result.is_incremental is True
            assert len(result.new_commits) == 0
            assert len(result.all_commits) == 2
            assert {c.sha for c in result.all_commits} == {"cached1", "cached2"}


# ===========================================================================
# 3. Sample with use_cache=False
# ===========================================================================

class TestSampleNoCache:
    def test_does_not_read_cache(self):
        """When use_cache=False, sample does not read from cache even if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir)
            config.ensure_cache_dir()

            # Write a cache file with a stale cluster
            stale = [SampledCluster(
                repo="stale/repo", language="Java",
                commits=[_make_commit("stale")], total_in_group=1,
            )]
            with open(config.samples_path(), "w") as f:
                json.dump([c.model_dump(mode="json") for c in stale], f, default=str)

            # Sample fresh commits with use_cache=False
            commits = [_make_commit("fresh1"), _make_commit("fresh2")]
            from gitstyle.sample import sample
            result = sample(commits, config, use_cache=False)

            # Should NOT return the stale Java data
            assert all(c.repo == "user/repo" for c in result)
            assert all(c.language == "Python" for c in result)

    def test_does_not_write_cache(self):
        """When use_cache=False, sample does not write to cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir)
            config.ensure_cache_dir()

            commits = [_make_commit("a"), _make_commit("b")]
            from gitstyle.sample import sample
            sample(commits, config, use_cache=False)

            assert not config.samples_path().exists()


# ===========================================================================
# 4. Extract with use_cache=False
# ===========================================================================

class TestExtractNoCache:
    def test_does_not_read_cache(self):
        """When use_cache=False, extract does not read from cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, dry_run=True)
            config.ensure_cache_dir()

            # Write a stale cache
            stale = [_make_extraction(repo="stale/repo")]
            _save_extractions_to_cache(config.extractions_path(), stale)

            cluster = SampledCluster(
                repo="user/repo", language="Python",
                commits=[_make_commit("c1")], total_in_group=1,
            )
            from gitstyle.extract import extract
            result = extract([cluster], config, use_cache=False)

            # dry_run returns [], but it should NOT have returned the stale cache
            assert result == []

    def test_does_not_write_cache(self):
        """When use_cache=False, extract does not write to cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir)
            config.ensure_cache_dir()

            cluster = SampledCluster(
                repo="user/repo", language="Python",
                commits=[_make_commit("c1")], total_in_group=1,
            )

            mock_obs = {"observations": [
                {
                    "dimension": "code-structure",
                    "claim": "Uses small functions",
                    "evidence": ["c1"],
                    "confidence": 0.8,
                }
            ]}

            with patch("gitstyle.extract.LLMClient") as MockLLM:
                mock_instance = MockLLM.return_value
                mock_instance.complete_json.return_value = mock_obs
                from gitstyle.extract import extract
                result = extract([cluster], config, use_cache=False)

            assert len(result) == 1
            assert not config.extractions_path().exists()


# ===========================================================================
# 5. merge_extractions
# ===========================================================================

class TestMergeExtractions:
    def test_merges_same_repo_lang(self):
        """Merges observations from same (repo, lang) pair."""
        existing = [_make_extraction(
            repo="u/r", language="Python",
            observations=[_make_observation(claim="Uses small functions")],
        )]
        new = [_make_extraction(
            repo="u/r", language="Python",
            observations=[_make_observation(claim="Prefers list comprehensions")],
        )]

        result = merge_extractions(existing, new)
        assert len(result) == 1
        assert result[0].repo == "u/r"
        assert result[0].language == "Python"
        claims = {o.claim for o in result[0].observations}
        assert claims == {"Uses small functions", "Prefers list comprehensions"}

    def test_deduplicates_by_claim(self):
        """Duplicate claims (same text) are not added twice."""
        existing = [_make_extraction(
            repo="u/r", language="Python",
            observations=[_make_observation(claim="Uses small functions")],
        )]
        new = [_make_extraction(
            repo="u/r", language="Python",
            observations=[
                _make_observation(claim="Uses small functions"),  # duplicate
                _make_observation(claim="New observation"),
            ],
        )]

        result = merge_extractions(existing, new)
        assert len(result) == 1
        claims = [o.claim for o in result[0].observations]
        assert claims.count("Uses small functions") == 1
        assert "New observation" in claims

    def test_keeps_new_repo_lang_pairs(self):
        """Extractions for (repo, lang) pairs only in 'new' are kept."""
        existing = [_make_extraction(repo="u/r", language="Python")]
        new = [_make_extraction(repo="u/r", language="Rust",
                                observations=[_make_observation(claim="Uses pattern matching")])]

        result = merge_extractions(existing, new)
        assert len(result) == 2
        langs = {e.language for e in result}
        assert langs == {"Python", "Rust"}

    def test_preserves_existing_when_no_new(self):
        """Existing extractions are preserved when no new data for that pair."""
        existing = [
            _make_extraction(repo="u/r", language="Python",
                             observations=[_make_observation(claim="Existing claim")]),
            _make_extraction(repo="u/r", language="Go",
                             observations=[_make_observation(claim="Go claim")]),
        ]
        new = [_make_extraction(repo="u/r", language="Python",
                                observations=[_make_observation(claim="New Python claim")])]

        result = merge_extractions(existing, new)
        assert len(result) == 2

        # Go should be untouched
        go_ext = [e for e in result if e.language == "Go"][0]
        assert len(go_ext.observations) == 1
        assert go_ext.observations[0].claim == "Go claim"

        # Python should be merged
        py_ext = [e for e in result if e.language == "Python"][0]
        claims = {o.claim for o in py_ext.observations}
        assert "Existing claim" in claims
        assert "New Python claim" in claims


# ===========================================================================
# 6. _group_observations
# ===========================================================================

class TestGroupObservations:
    def test_groups_by_dimension(self):
        extractions = [
            _make_extraction(observations=[
                _make_observation(dimension=StyleDimension.CODE_STRUCTURE, claim="a"),
                _make_observation(dimension=StyleDimension.NAMING, claim="b"),
            ]),
            _make_extraction(repo="u/r2", observations=[
                _make_observation(dimension=StyleDimension.CODE_STRUCTURE, claim="c"),
            ]),
        ]

        by_dim, _, _ = _group_observations(extractions)

        assert len(by_dim[StyleDimension.CODE_STRUCTURE]) == 2
        assert len(by_dim[StyleDimension.NAMING]) == 1

    def test_groups_by_language(self):
        """Language idioms observations are grouped by language."""
        extractions = [_make_extraction(observations=[
            _make_observation(
                dimension=StyleDimension.LANGUAGE_IDIOMS,
                claim="Uses list comprehensions",
                language="Python",
            ),
            _make_observation(
                dimension=StyleDimension.LANGUAGE_IDIOMS,
                claim="Uses pattern matching",
                language="Rust",
            ),
        ])]

        _, by_lang, _ = _group_observations(extractions)

        assert "Python" in by_lang
        assert "Rust" in by_lang
        assert len(by_lang["Python"]) == 1
        assert len(by_lang["Rust"]) == 1

    def test_collects_repos(self):
        extractions = [
            _make_extraction(repo="user/repo1"),
            _make_extraction(repo="user/repo2"),
        ]

        _, _, repos = _group_observations(extractions)
        assert repos == {"user/repo1", "user/repo2"}

    def test_non_idiom_observations_not_in_by_language(self):
        """Only LANGUAGE_IDIOMS observations go into by_language."""
        extractions = [_make_extraction(observations=[
            _make_observation(
                dimension=StyleDimension.NAMING,
                claim="Uses snake_case",
                language="Python",
            ),
        ])]

        _, by_lang, _ = _group_observations(extractions)
        # NAMING dimension with language should NOT appear in by_language
        assert len(by_lang) == 0


# ===========================================================================
# 7. _build_evolve_prompt
# ===========================================================================

class TestBuildEvolvePrompt:
    def test_contains_existing_content(self):
        article = _make_article(
            content="The developer organizes code into small modules.",
            title="Code Structure",
            confidence=0.85,
        )
        observations = [_make_observation(claim="Uses single-responsibility pattern")]
        prompt = _build_evolve_prompt(article, observations)

        assert "The developer organizes code into small modules." in prompt
        assert "Code Structure" in prompt

    def test_contains_new_observations(self):
        article = _make_article()
        observations = [
            _make_observation(claim="Uses dependency injection", evidence=["sha111"]),
            _make_observation(claim="Prefers composition over inheritance", evidence=["sha222"]),
        ]
        prompt = _build_evolve_prompt(article, observations)

        assert "Uses dependency injection" in prompt
        assert "Prefers composition over inheritance" in prompt
        assert "sha111" in prompt
        assert "sha222" in prompt

    def test_contains_confidence(self):
        article = _make_article(confidence=0.85)
        observations = [_make_observation(confidence=0.9)]
        prompt = _build_evolve_prompt(article, observations)

        assert "85%" in prompt
        assert "90%" in prompt

    def test_contains_section_headers(self):
        article = _make_article()
        observations = [_make_observation()]
        prompt = _build_evolve_prompt(article, observations)

        assert "Existing Article" in prompt
        assert "New Observations" in prompt


# ===========================================================================
# 8. evolve_wiki dry_run
# ===========================================================================

class TestEvolveWikiDryRun:
    def test_dry_run_returns_existing_articles(self):
        """In dry_run mode, evolve_wiki returns existing articles unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, dry_run=True)
            config.ensure_cache_dir()

            existing_articles = [
                _make_article(slug="code-structure", content="Original content A"),
                _make_article(slug="naming-conventions", title="Naming",
                              content="Original content B"),
            ]

            new_extractions = [_make_extraction(observations=[
                _make_observation(dimension=StyleDimension.CODE_STRUCTURE,
                                  claim="Brand new observation"),
            ])]

            result = evolve_wiki(existing_articles, new_extractions, config)

            assert len(result) == 2
            # Content should be unchanged in dry_run
            slugs = {a.slug for a in result}
            assert "code-structure" in slugs
            assert "naming-conventions" in slugs
            for a in result:
                if a.slug == "code-structure":
                    assert a.content == "Original content A"
                if a.slug == "naming-conventions":
                    assert a.content == "Original content B"


# ===========================================================================
# 9. Full incremental pipeline routing
# ===========================================================================

class TestIncrementalPipelineRouting:
    def test_incremental_path_taken(self):
        """When fetch returns new commits and articles cache exists, evolve path is taken."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, dry_run=True, fresh=False)
            config.ensure_cache_dir()

            # Pre-populate articles cache so incremental is triggered
            existing_articles = [_make_article()]
            _save_articles_to_cache(config.articles_path(), existing_articles)

            old_commits = [_make_commit("old1", days_ago=30)]
            new_commits = [_make_commit("new1", days_ago=0)]

            fetch_result = FetchResult(
                all_commits=old_commits + new_commits,
                new_commits=new_commits,
                is_incremental=True,
            )

            with patch("gitstyle.cli._run_incremental_pipeline") as mock_incr, \
                 patch("gitstyle.cli._run_full_pipeline") as mock_full, \
                 patch("gitstyle.fetch.fetch", return_value=fetch_result):
                from gitstyle.cli import _run_pipeline
                _run_pipeline(config)

            mock_incr.assert_called_once()
            mock_full.assert_not_called()

    def test_full_path_when_no_articles_cache(self):
        """When articles cache does not exist, full pipeline is used even if incremental fetch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, dry_run=True, fresh=False)
            config.ensure_cache_dir()

            # No articles cache
            commits = [_make_commit("c1")]
            fetch_result = FetchResult(
                all_commits=commits,
                new_commits=commits,
                is_incremental=True,
            )

            with patch("gitstyle.cli._run_incremental_pipeline") as mock_incr, \
                 patch("gitstyle.cli._run_full_pipeline") as mock_full, \
                 patch("gitstyle.fetch.fetch", return_value=fetch_result):
                from gitstyle.cli import _run_pipeline
                _run_pipeline(config)

            mock_full.assert_called_once()
            mock_incr.assert_not_called()


# ===========================================================================
# 10. No new commits — early exit
# ===========================================================================

class TestNoNewCommits:
    def test_up_to_date_message(self, capsys):
        """When no new commits and articles exist, pipeline exits early."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, dry_run=True, fresh=False)
            config.ensure_cache_dir()

            # Pre-populate articles cache
            _save_articles_to_cache(config.articles_path(), [_make_article()])

            existing = [_make_commit("old1", days_ago=5)]
            fetch_result = FetchResult(
                all_commits=existing,
                new_commits=[],
                is_incremental=True,
            )

            with patch("gitstyle.cli._run_incremental_pipeline") as mock_incr, \
                 patch("gitstyle.cli._run_full_pipeline") as mock_full, \
                 patch("gitstyle.fetch.fetch", return_value=fetch_result):
                from gitstyle.cli import _run_pipeline
                _run_pipeline(config)

            # Neither pipeline should be called — it should exit early
            mock_incr.assert_not_called()
            mock_full.assert_not_called()


# ===========================================================================
# 11. Fresh flag forces full pipeline
# ===========================================================================

class TestFreshFlag:
    def test_fresh_forces_full_pipeline(self):
        """Even with incremental fetch result and articles cache, --fresh forces full pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, dry_run=True, fresh=True)
            config.ensure_cache_dir()

            # Pre-populate articles cache
            _save_articles_to_cache(config.articles_path(), [_make_article()])

            commits = [_make_commit("c1"), _make_commit("c2")]
            fetch_result = FetchResult(
                all_commits=commits,
                new_commits=commits,
                is_incremental=False,  # fresh=True means fetch returns non-incremental
            )

            with patch("gitstyle.cli._run_incremental_pipeline") as mock_incr, \
                 patch("gitstyle.cli._run_full_pipeline") as mock_full, \
                 patch("gitstyle.fetch.fetch", return_value=fetch_result):
                from gitstyle.cli import _run_pipeline
                _run_pipeline(config)

            mock_full.assert_called_once()
            mock_incr.assert_not_called()

    def test_fresh_config_field(self):
        """The fresh field defaults to False and can be set to True."""
        config_default = GitStyleConfig(username="test")
        assert config_default.fresh is False

        config_fresh = GitStyleConfig(username="test", fresh=True)
        assert config_fresh.fresh is True


# ===========================================================================
# 12. CLI --fresh flag exists
# ===========================================================================

class TestCLIFreshFlag:
    def test_fresh_in_run_help(self):
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--fresh" in result.stdout

    def test_fresh_in_fetch_help(self):
        result = runner.invoke(app, ["fetch-cmd", "--help"])
        assert result.exit_code == 0
        assert "--fresh" in result.stdout


# ===========================================================================
# Additional edge-case tests
# ===========================================================================

class TestFetchLoadSaveRoundtrip:
    def test_commits_roundtrip_via_cache(self):
        """Commits saved to cache and loaded back are identical."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "commits.jsonl"
            commits = [
                _make_commit("sha1", days_ago=10),
                _make_commit("sha2", days_ago=5, additions=100),
            ]
            _save_commits_to_cache(path, commits)

            from gitstyle.fetch import _load_commits
            loaded = _load_commits(path)

            assert len(loaded) == 2
            assert loaded[0].sha == "sha1"
            assert loaded[1].sha == "sha2"
            assert loaded[1].additions == 100


class TestEmptyCacheTreatedAsFresh:
    def test_empty_cache_file(self):
        """An empty commits.jsonl triggers a fresh fetch, not incremental."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, fresh=False, github_token="fake")
            config.ensure_cache_dir()

            # Write an empty cache file
            config.commits_path().write_text("")

            fresh_commits = [_make_commit("c1")]
            with patch("gitstyle.fetch._fetch_from_github", return_value=fresh_commits):
                from gitstyle.fetch import fetch
                result = fetch(config)

            # Empty cache should trigger fresh fetch, not incremental
            assert result.is_incremental is False
            assert len(result.all_commits) == 1


class TestNoNewCommitsAllDeduped:
    def test_all_new_commits_are_duplicates(self):
        """When all API results are already in cache, new_commits is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir, fresh=False, github_token="fake")
            config.ensure_cache_dir()

            existing = [_make_commit("x", days_ago=5), _make_commit("y", days_ago=3)]
            _save_commits_to_cache(config.commits_path(), existing)

            # API returns the same commits
            api_result = [_make_commit("x", days_ago=5), _make_commit("y", days_ago=3)]

            with patch("gitstyle.fetch._fetch_from_github", return_value=api_result):
                from gitstyle.fetch import fetch
                result = fetch(config)

            assert result.is_incremental is True
            assert len(result.new_commits) == 0
            assert len(result.all_commits) == 2


class TestEvolveWikiNoNewObservations:
    def test_returns_existing_when_no_observations(self):
        """When new_extractions have no observations, returns existing articles as-is."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            config = _make_config(cache_dir)
            config.ensure_cache_dir()

            existing_articles = [
                _make_article(slug="code-structure", content="Content A"),
            ]

            # Extractions with zero observations
            empty_extractions = [_make_extraction(observations=[])]

            result = evolve_wiki(existing_articles, empty_extractions, config)
            assert len(result) == 1
            assert result[0].content == "Content A"


class TestMergeExtractionsEmpty:
    def test_merge_both_empty(self):
        result = merge_extractions([], [])
        assert result == []

    def test_merge_existing_only(self):
        existing = [_make_extraction(repo="u/r", language="Python")]
        result = merge_extractions(existing, [])
        assert len(result) == 1
        assert result[0].repo == "u/r"

    def test_merge_new_only(self):
        new = [_make_extraction(repo="u/r", language="Rust")]
        result = merge_extractions([], new)
        assert len(result) == 1
        assert result[0].language == "Rust"
