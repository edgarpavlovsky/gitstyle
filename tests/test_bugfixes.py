"""Tests for org detection, wikilink post-processing, and JSON retry fixes.

Covers:
- GitHubClient.detect_account_type()
- Org-aware fetch (no author filter for orgs)
- _fix_wikilinks() post-processing
- Valid slugs passed to compile prompts
- LLMClient.complete_json() retry logic
- LLMClient._extract_json_text()
- Config: context_type, max_repos fields
"""

from __future__ import annotations

import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import anthropic
import pytest

from gitstyle.compile import _fix_wikilinks, _build_dimension_prompt, _build_language_prompt
from gitstyle.config import GitStyleConfig
from gitstyle.llm_client import LLMClient
from gitstyle.models import (
    Observation,
    StyleDimension,
    WikiArticle,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_article(slug: str, content: str = "", wikilinks: list[str] | None = None) -> WikiArticle:
    return WikiArticle(
        slug=slug,
        title=slug.replace("-", " ").title(),
        category="dimension",
        confidence=0.8,
        source_repos=["user/repo"],
        content=content,
        wikilinks=wikilinks or [],
    )


def _make_observation(
    dim: StyleDimension = StyleDimension.CODE_STRUCTURE,
    claim: str = "test claim",
    language: str | None = None,
) -> Observation:
    return Observation(
        dimension=dim,
        claim=claim,
        evidence=["abc1234"],
        confidence=0.8,
        language=language,
    )


# ---------------------------------------------------------------------------
# Config: new fields
# ---------------------------------------------------------------------------

class TestConfigNewFields:
    def test_context_type_defaults_to_none(self):
        config = GitStyleConfig(username="test")
        assert config.context_type is None

    def test_context_type_can_be_set(self):
        config = GitStyleConfig(username="test", context_type="Organization")
        assert config.context_type == "Organization"

    def test_max_repos_defaults_to_30(self):
        config = GitStyleConfig(username="test")
        assert config.max_repos == 30

    def test_max_repos_can_be_set(self):
        config = GitStyleConfig(username="test", max_repos=10)
        assert config.max_repos == 10

    def test_max_repos_zero_means_no_limit(self):
        config = GitStyleConfig(username="test", max_repos=0)
        assert config.max_repos == 0


# ---------------------------------------------------------------------------
# GitHubClient: detect_account_type
# ---------------------------------------------------------------------------

class TestDetectAccountType:
    def test_detects_user(self):
        from gitstyle.github_client import GitHubClient

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"login": "torvalds", "type": "User"}

        with patch.object(GitHubClient, '_request', return_value=mock_resp) as mock_req:
            client = GitHubClient.__new__(GitHubClient)
            client._client = MagicMock()
            result = client.detect_account_type("torvalds")

        assert result == "User"
        mock_req.assert_called_once_with("GET", "/users/torvalds")

    def test_detects_organization(self):
        from gitstyle.github_client import GitHubClient

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"login": "NousResearch", "type": "Organization"}

        with patch.object(GitHubClient, '_request', return_value=mock_resp) as mock_req:
            client = GitHubClient.__new__(GitHubClient)
            client._client = MagicMock()
            result = client.detect_account_type("NousResearch")

        assert result == "Organization"

    def test_defaults_to_user_if_type_missing(self):
        from gitstyle.github_client import GitHubClient

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"login": "someone"}

        with patch.object(GitHubClient, '_request', return_value=mock_resp):
            client = GitHubClient.__new__(GitHubClient)
            client._client = MagicMock()
            result = client.detect_account_type("someone")

        assert result == "User"


# ---------------------------------------------------------------------------
# GitHubClient: list_repos with org mode
# ---------------------------------------------------------------------------

class TestListReposOrg:
    def _setup_client(self, pages: list[list[dict]]):
        """Create a GitHubClient mock that returns paginated repo responses."""
        from gitstyle.github_client import GitHubClient

        call_count = [0]
        def mock_request(method, url, **kwargs):
            resp = MagicMock()
            if "/repos" in url:
                page_idx = call_count[0]
                resp.json.return_value = pages[page_idx] if page_idx < len(pages) else []
                call_count[0] += 1
            else:
                # For individual repo star lookups
                repo_name = url.replace("/repos/", "")
                for page in pages:
                    for r in page:
                        if r["full_name"] == repo_name:
                            resp.json.return_value = r
                            return resp
                resp.json.return_value = {"stargazers_count": 0}
            return resp

        client = GitHubClient.__new__(GitHubClient)
        client._client = MagicMock()
        client._request = mock_request
        return client

    def test_org_uses_orgs_endpoint(self):
        from gitstyle.github_client import GitHubClient

        calls = []
        def mock_request(method, url, **kwargs):
            calls.append(url)
            resp = MagicMock()
            resp.json.return_value = []
            return resp

        client = GitHubClient.__new__(GitHubClient)
        client._client = MagicMock()
        client._request = mock_request

        client.list_repos("NousResearch", is_org=True)
        assert any("/orgs/NousResearch/repos" in c for c in calls)

    def test_user_uses_users_endpoint(self):
        from gitstyle.github_client import GitHubClient

        calls = []
        def mock_request(method, url, **kwargs):
            calls.append(url)
            resp = MagicMock()
            resp.json.return_value = []
            return resp

        client = GitHubClient.__new__(GitHubClient)
        client._client = MagicMock()
        client._request = mock_request

        client.list_repos("torvalds", is_org=False)
        assert any("/users/torvalds/repos" in c for c in calls)

    def test_org_skips_forks(self):
        repos = [
            {"full_name": "org/real-repo", "fork": False, "stargazers_count": 10},
            {"full_name": "org/forked-repo", "fork": True, "stargazers_count": 100},
        ]
        client = self._setup_client([repos, []])
        result = client.list_repos("org", is_org=True)
        assert "org/real-repo" in result
        assert "org/forked-repo" not in result


# ---------------------------------------------------------------------------
# GitHubClient: list_commits without author filter
# ---------------------------------------------------------------------------

class TestListCommitsNoAuthor:
    def test_commits_without_author_filter(self):
        from gitstyle.github_client import GitHubClient

        captured_params = {}
        def mock_request(method, url, **kwargs):
            captured_params.update(kwargs.get("params", {}))
            resp = MagicMock()
            resp.json.return_value = []
            return resp

        client = GitHubClient.__new__(GitHubClient)
        client._client = MagicMock()
        client._request = mock_request

        client.list_commits("org/repo", author=None)
        assert "author" not in captured_params

    def test_commits_with_author_filter(self):
        from gitstyle.github_client import GitHubClient

        captured_params = {}
        def mock_request(method, url, **kwargs):
            captured_params.update(kwargs.get("params", {}))
            resp = MagicMock()
            resp.json.return_value = []
            return resp

        client = GitHubClient.__new__(GitHubClient)
        client._client = MagicMock()
        client._request = mock_request

        client.list_commits("user/repo", author="torvalds")
        assert captured_params.get("author") == "torvalds"


# ---------------------------------------------------------------------------
# Fetch: org detection integration
# ---------------------------------------------------------------------------

class TestFetchOrgDetection:
    def test_fetch_sets_context_type(self):
        """Fetch should auto-detect and store context_type on config."""
        config = GitStyleConfig(
            username="nousresearch",
            github_token="fake-token",
            cache_dir=Path(tempfile.mkdtemp()),
        )
        assert config.context_type is None

        with patch("gitstyle.fetch.GitHubClient") as MockClient:
            mock_gh = MagicMock()
            mock_gh.__enter__ = MagicMock(return_value=mock_gh)
            mock_gh.__exit__ = MagicMock(return_value=False)
            mock_gh.detect_account_type.return_value = "Organization"
            mock_gh.list_repos.return_value = ["org/repo"]
            mock_gh.get_repo_languages.return_value = ["Python"]
            mock_gh.fetch_commits_for_repo.return_value = []
            MockClient.return_value = mock_gh

            from gitstyle.fetch import _fetch_from_github
            _fetch_from_github(config)

        assert config.context_type == "Organization"

    def test_org_fetch_passes_author_none(self):
        """For orgs, fetch should pass author=None to skip author filtering."""
        config = GitStyleConfig(
            username="nousresearch",
            github_token="fake-token",
            cache_dir=Path(tempfile.mkdtemp()),
        )

        with patch("gitstyle.fetch.GitHubClient") as MockClient:
            mock_gh = MagicMock()
            mock_gh.__enter__ = MagicMock(return_value=mock_gh)
            mock_gh.__exit__ = MagicMock(return_value=False)
            mock_gh.detect_account_type.return_value = "Organization"
            mock_gh.list_repos.return_value = ["org/repo"]
            mock_gh.get_repo_languages.return_value = ["Python"]
            mock_gh.fetch_commits_for_repo.return_value = []
            MockClient.return_value = mock_gh

            from gitstyle.fetch import _fetch_from_github
            _fetch_from_github(config)

        # Verify author=None was passed
        call_kwargs = mock_gh.fetch_commits_for_repo.call_args
        assert call_kwargs.kwargs.get("author") is None or call_kwargs[1].get("author") is None

    def test_user_fetch_passes_author_username(self):
        """For users, fetch should pass author=username."""
        config = GitStyleConfig(
            username="torvalds",
            github_token="fake-token",
            cache_dir=Path(tempfile.mkdtemp()),
        )

        with patch("gitstyle.fetch.GitHubClient") as MockClient:
            mock_gh = MagicMock()
            mock_gh.__enter__ = MagicMock(return_value=mock_gh)
            mock_gh.__exit__ = MagicMock(return_value=False)
            mock_gh.detect_account_type.return_value = "User"
            mock_gh.list_repos.return_value = ["torvalds/linux"]
            mock_gh.get_repo_languages.return_value = ["C"]
            mock_gh.fetch_commits_for_repo.return_value = []
            MockClient.return_value = mock_gh

            from gitstyle.fetch import _fetch_from_github
            _fetch_from_github(config)

        call_kwargs = mock_gh.fetch_commits_for_repo.call_args
        # author should be "torvalds" for a user
        assert call_kwargs.kwargs.get("author") == "torvalds" or call_kwargs[1].get("author") == "torvalds"


# ---------------------------------------------------------------------------
# _fix_wikilinks: post-processing
# ---------------------------------------------------------------------------

class TestFixWikilinks:
    def test_strips_invalid_wikilinks_from_list(self):
        articles = [
            _make_article("code-structure", wikilinks=["naming-conventions", "nonexistent"]),
            _make_article("naming-conventions", wikilinks=["code-structure"]),
        ]
        fixed = _fix_wikilinks(articles)
        assert fixed[0].wikilinks == ["naming-conventions"]
        assert fixed[1].wikilinks == ["code-structure"]

    def test_strips_invalid_wikilinks_from_content(self):
        articles = [
            _make_article(
                "code-structure",
                content="See [[naming-conventions]] and [[nonexistent-article]] for more.",
            ),
            _make_article("naming-conventions"),
        ]
        fixed = _fix_wikilinks(articles)
        assert "[[naming-conventions]]" in fixed[0].content
        assert "[[nonexistent-article]]" not in fixed[0].content
        assert "nonexistent article" in fixed[0].content  # converted to plain text

    def test_preserves_valid_wikilinks(self):
        articles = [
            _make_article(
                "code-structure",
                content="Related: [[naming-conventions]], [[testing]]",
                wikilinks=["naming-conventions", "testing"],
            ),
            _make_article("naming-conventions"),
            _make_article("testing"),
        ]
        fixed = _fix_wikilinks(articles)
        assert "[[naming-conventions]]" in fixed[0].content
        assert "[[testing]]" in fixed[0].content
        assert fixed[0].wikilinks == ["naming-conventions", "testing"]

    def test_handles_no_wikilinks(self):
        articles = [
            _make_article("code-structure", content="No wikilinks here."),
        ]
        fixed = _fix_wikilinks(articles)
        assert fixed[0].content == "No wikilinks here."

    def test_handles_all_invalid_wikilinks(self):
        articles = [
            _make_article(
                "code-structure",
                content="See [[fake-a]], [[fake-b]]",
                wikilinks=["fake-a", "fake-b"],
            ),
        ]
        fixed = _fix_wikilinks(articles)
        assert fixed[0].wikilinks == []
        assert "[[" not in fixed[0].content
        assert "fake a" in fixed[0].content
        assert "fake b" in fixed[0].content

    def test_empty_article_list(self):
        assert _fix_wikilinks([]) == []

    def test_strips_self_referential_wikilinks_from_list(self):
        """Articles should not link to themselves."""
        articles = [
            _make_article(
                "code-structure",
                wikilinks=["code-structure", "naming-conventions"],
            ),
            _make_article("naming-conventions"),
        ]
        fixed = _fix_wikilinks(articles)
        assert "code-structure" not in fixed[0].wikilinks
        assert "naming-conventions" in fixed[0].wikilinks

    def test_strips_self_referential_wikilinks_from_content(self):
        """Self-referential [[wikilinks]] in content should become plain text."""
        articles = [
            _make_article(
                "python",
                content="See [[python]] for more about [[naming-conventions]].",
            ),
            _make_article("naming-conventions"),
        ]
        fixed = _fix_wikilinks(articles)
        assert "[[python]]" not in fixed[0].content
        assert "python" in fixed[0].content  # plain text preserved
        assert "[[naming-conventions]]" in fixed[0].content  # valid link kept

    def test_handles_pipe_syntax_wikilinks(self):
        """[[slug|display text]] format should be handled correctly."""
        articles = [
            _make_article(
                "testing",
                content="Related to [[commit-hygiene|commit messages]] and [[nonexistent|fake]].",
            ),
            _make_article("commit-hygiene"),
        ]
        fixed = _fix_wikilinks(articles)
        assert "[[commit-hygiene|commit messages]]" in fixed[0].content
        assert "[[nonexistent" not in fixed[0].content
        assert "fake" in fixed[0].content  # display text preserved

    def test_normalizes_slug_with_spaces(self):
        """Wikilinks with spaces in slug should be normalized to hyphens."""
        articles = [
            _make_article(
                "testing",
                content="See [[code structure]] for more.",
            ),
            _make_article("code-structure"),
        ]
        fixed = _fix_wikilinks(articles)
        assert "[[code-structure]]" in fixed[0].content

    def test_self_referential_pipe_syntax(self):
        """Self-referential [[slug|display]] should become just display text."""
        articles = [
            _make_article(
                "python",
                content="This is about [[python|Python patterns]].",
            ),
            _make_article("naming-conventions"),
        ]
        fixed = _fix_wikilinks(articles)
        assert "[[python" not in fixed[0].content
        assert "Python patterns" in fixed[0].content


# ---------------------------------------------------------------------------
# Truncation retry
# ---------------------------------------------------------------------------

class TestTruncationRetry:
    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_retries_on_max_tokens_truncation(self):
        """When stop_reason is max_tokens, should retry with doubled limit."""
        client = LLMClient()
        client.model = "test"
        client._last_stop_reason = "end_turn"
        call_count = [0]
        captured_max_tokens = []

        def mock_complete(system, prompt, max_tokens, temperature):
            call_count[0] += 1
            captured_max_tokens.append(max_tokens)
            if call_count[0] == 1:
                client._last_stop_reason = "max_tokens"
                return '{"truncated": true'  # incomplete JSON
            client._last_stop_reason = "end_turn"
            return '{"complete": true}'

        with patch.object(client, 'complete', side_effect=mock_complete):
            result = client.complete_json("system", "prompt")

        assert result == {"complete": True}
        assert call_count[0] == 2
        assert captured_max_tokens[1] > captured_max_tokens[0]


# ---------------------------------------------------------------------------
# Compile prompts: valid slugs passed
# ---------------------------------------------------------------------------

class TestCompilePromptsValidSlugs:
    def test_dimension_prompt_includes_valid_slugs(self):
        obs = [_make_observation()]
        slugs = ["code-structure", "naming-conventions", "testing"]
        prompt = _build_dimension_prompt(StyleDimension.CODE_STRUCTURE, obs, valid_slugs=slugs)
        assert "code-structure" in prompt
        assert "naming-conventions" in prompt
        assert "IMPORTANT" in prompt
        assert "Do NOT invent" in prompt

    def test_dimension_prompt_without_slugs(self):
        obs = [_make_observation()]
        prompt = _build_dimension_prompt(StyleDimension.CODE_STRUCTURE, obs)
        assert "IMPORTANT" not in prompt

    def test_language_prompt_includes_valid_slugs(self):
        obs = [_make_observation(dim=StyleDimension.LANGUAGE_IDIOMS, language="Python")]
        slugs = ["code-structure", "python"]
        prompt = _build_language_prompt("Python", obs, valid_slugs=slugs)
        assert "code-structure" in prompt
        assert "python" in prompt
        assert "IMPORTANT" in prompt

    def test_language_prompt_without_slugs(self):
        obs = [_make_observation(dim=StyleDimension.LANGUAGE_IDIOMS, language="Python")]
        prompt = _build_language_prompt("Python", obs)
        assert "IMPORTANT" not in prompt


# ---------------------------------------------------------------------------
# LLMClient: _extract_json_text
# ---------------------------------------------------------------------------

class TestExtractJsonText:
    def test_extracts_from_json_code_block(self):
        text = 'Some text\n```json\n{"key": "value"}\n```\nMore text'
        assert LLMClient._extract_json_text(text) == '{"key": "value"}'

    def test_extracts_from_generic_code_block(self):
        text = 'Some text\n```\n{"key": "value"}\n```\nMore text'
        assert LLMClient._extract_json_text(text) == '{"key": "value"}'

    def test_returns_raw_json(self):
        text = '{"key": "value"}'
        assert LLMClient._extract_json_text(text) == '{"key": "value"}'

    def test_strips_whitespace(self):
        text = '  \n{"key": "value"}\n  '
        assert LLMClient._extract_json_text(text) == '{"key": "value"}'


# ---------------------------------------------------------------------------
# LLMClient: complete_json retry logic
# ---------------------------------------------------------------------------

class TestCompleteJsonRetry:
    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_succeeds_on_first_try(self):
        client = LLMClient()
        client.model = "test"
        with patch.object(client, 'complete', return_value='{"key": "value"}'):
            result = client.complete_json("system", "prompt")
        assert result == {"key": "value"}

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_retries_on_json_error(self):
        client = LLMClient()
        client.model = "test"
        call_count = [0]

        def mock_complete(system, prompt, max_tokens, temperature):
            call_count[0] += 1
            if call_count[0] == 1:
                return "not valid json {{"
            return '{"key": "fixed"}'

        with patch.object(client, 'complete', side_effect=mock_complete):
            result = client.complete_json("system", "prompt", retries=1)

        assert result == {"key": "fixed"}
        assert call_count[0] == 2

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_raises_after_all_retries_exhausted(self):
        client = LLMClient()
        client.model = "test"

        with patch.object(client, 'complete', return_value="not json {{"):
            with pytest.raises(json.JSONDecodeError):
                client.complete_json("system", "prompt", retries=1)

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_no_retry_when_retries_zero(self):
        client = LLMClient()
        client.model = "test"
        call_count = [0]

        def mock_complete(system, prompt, max_tokens, temperature):
            call_count[0] += 1
            return "not json"

        with patch.object(client, 'complete', side_effect=mock_complete):
            with pytest.raises(json.JSONDecodeError):
                client.complete_json("system", "prompt", retries=0)

        assert call_count[0] == 1

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_retry_prompt_includes_error_info(self):
        client = LLMClient()
        client.model = "test"
        prompts_seen = []

        def mock_complete(system, prompt, max_tokens, temperature):
            prompts_seen.append(prompt)
            if len(prompts_seen) == 1:
                return "broken {json"
            return '{"fixed": true}'

        with patch.object(client, 'complete', side_effect=mock_complete):
            client.complete_json("system", "original prompt", retries=1)

        assert len(prompts_seen) == 2
        assert "not valid JSON" in prompts_seen[1]
        assert "original prompt" in prompts_seen[1]

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_default_max_tokens_is_32768(self):
        """Verify max_tokens default was increased to 32768."""
        client = LLMClient()
        client.model = "test"
        client._last_stop_reason = "end_turn"
        captured_max_tokens = []

        def mock_complete(system, prompt, max_tokens, temperature):
            captured_max_tokens.append(max_tokens)
            client._last_stop_reason = "end_turn"
            return '{"ok": true}'

        with patch.object(client, 'complete', side_effect=mock_complete):
            client.complete_json("system", "prompt")

        assert captured_max_tokens[0] == 32768


# ---------------------------------------------------------------------------
# fetch_commits_for_repo: author extraction from commit data
# ---------------------------------------------------------------------------

class TestFetchCommitsAuthorExtraction:
    def test_extracts_author_from_commit_when_author_is_none(self):
        """When author=None (org mode), should extract author from commit data."""
        from gitstyle.github_client import GitHubClient

        mock_commit = {
            "sha": "abc123",
            "commit": {
                "author": {"name": "John Doe", "date": "2025-01-01T00:00:00Z"},
                "message": "test commit",
            },
            "author": {"login": "johndoe"},
        }
        mock_detail = {
            "sha": "abc123",
            "files": [],
            "stats": {"additions": 5, "deletions": 2},
        }

        with patch.object(GitHubClient, 'list_commits', return_value=[mock_commit]):
            with patch.object(GitHubClient, 'get_commit_detail', return_value=mock_detail):
                client = GitHubClient.__new__(GitHubClient)
                client._client = MagicMock()
                results = client.fetch_commits_for_repo(
                    repo="org/repo", author=None, languages=["Python"],
                )

        assert len(results) == 1
        assert results[0].author == "johndoe"

    def test_uses_provided_author_when_given(self):
        """When author is provided (user mode), should use that author."""
        from gitstyle.github_client import GitHubClient

        mock_commit = {
            "sha": "abc123",
            "commit": {
                "author": {"name": "John Doe", "date": "2025-01-01T00:00:00Z"},
                "message": "test commit",
            },
            "author": {"login": "johndoe"},
        }
        mock_detail = {
            "sha": "abc123",
            "files": [],
            "stats": {"additions": 5, "deletions": 2},
        }

        with patch.object(GitHubClient, 'list_commits', return_value=[mock_commit]):
            with patch.object(GitHubClient, 'get_commit_detail', return_value=mock_detail):
                client = GitHubClient.__new__(GitHubClient)
                client._client = MagicMock()
                results = client.fetch_commits_for_repo(
                    repo="user/repo", author="torvalds", languages=["C"],
                )

        assert len(results) == 1
        assert results[0].author == "torvalds"

    def test_falls_back_to_commit_name_when_login_missing(self):
        """When author=None and commit has no login, fall back to name."""
        from gitstyle.github_client import GitHubClient

        mock_commit = {
            "sha": "abc123",
            "commit": {
                "author": {"name": "Bot User", "date": "2025-01-01T00:00:00Z"},
                "message": "automated commit",
            },
            "author": None,  # No GitHub user linked
        }
        mock_detail = {"sha": "abc123", "files": [], "stats": {}}

        with patch.object(GitHubClient, 'list_commits', return_value=[mock_commit]):
            with patch.object(GitHubClient, 'get_commit_detail', return_value=mock_detail):
                client = GitHubClient.__new__(GitHubClient)
                client._client = MagicMock()
                results = client.fetch_commits_for_repo(
                    repo="org/repo", author=None, languages=["Python"],
                )

        assert len(results) == 1
        assert results[0].author == "Bot User"


# ---------------------------------------------------------------------------
# LLMClient: retry on transient API errors (overloaded, rate limit)
# ---------------------------------------------------------------------------

class TestTransientAPIRetry:
    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    @patch('gitstyle.llm_client.time.sleep')
    def test_retries_on_overloaded_error(self, mock_sleep):
        """Should retry with backoff on overloaded_error."""
        client = LLMClient()
        client.model = "test"
        client._client = MagicMock()
        call_count = [0]

        def mock_stream(**kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                error = anthropic.APIStatusError(
                    message="Overloaded",
                    response=MagicMock(status_code=529, headers={}),
                    body={"error": {"type": "overloaded_error", "message": "Overloaded"}},
                )
                raise error
            # Third call succeeds
            mock_ctx = MagicMock()
            mock_msg = MagicMock()
            mock_msg.stop_reason = "end_turn"
            mock_msg.content = [MagicMock(text="success")]
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_ctx.get_final_message.return_value = mock_msg
            return mock_ctx

        client._client.messages.stream = mock_stream
        result = client.complete("system", "prompt")
        assert result == "success"
        assert call_count[0] == 3
        assert mock_sleep.call_count == 2

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    @patch('gitstyle.llm_client.time.sleep')
    def test_retries_on_rate_limit_429(self, mock_sleep):
        """Should retry on HTTP 429 rate limit."""
        client = LLMClient()
        client.model = "test"
        client._client = MagicMock()
        call_count = [0]

        def mock_stream(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise anthropic.APIStatusError(
                    message="Rate limited",
                    response=MagicMock(status_code=429, headers={}),
                    body={"error": {"type": "rate_limit_error", "message": "Rate limited"}},
                )
            mock_ctx = MagicMock()
            mock_msg = MagicMock()
            mock_msg.stop_reason = "end_turn"
            mock_msg.content = [MagicMock(text="ok")]
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_ctx.get_final_message.return_value = mock_msg
            return mock_ctx

        client._client.messages.stream = mock_stream
        result = client.complete("system", "prompt")
        assert result == "ok"
        assert call_count[0] == 2

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    @patch('gitstyle.llm_client.time.sleep')
    def test_raises_after_max_retries(self, mock_sleep):
        """Should raise after exhausting all retries."""
        client = LLMClient()
        client.model = "test"
        client._client = MagicMock()

        def mock_stream(**kwargs):
            raise anthropic.APIStatusError(
                message="Overloaded",
                response=MagicMock(status_code=529, headers={}),
                body={"error": {"type": "overloaded_error", "message": "Overloaded"}},
            )

        client._client.messages.stream = mock_stream
        with pytest.raises(anthropic.APIStatusError):
            client.complete("system", "prompt")
        # Should have retried _MAX_RETRIES times
        assert mock_sleep.call_count == LLMClient._MAX_RETRIES

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    def test_does_not_retry_non_transient_errors(self):
        """Non-transient errors (e.g. 400 bad request) should not be retried."""
        client = LLMClient()
        client.model = "test"
        client._client = MagicMock()

        def mock_stream(**kwargs):
            raise anthropic.APIStatusError(
                message="Bad request",
                response=MagicMock(status_code=400, headers={}),
                body={"error": {"type": "invalid_request_error", "message": "Bad request"}},
            )

        client._client.messages.stream = mock_stream
        with pytest.raises(anthropic.APIStatusError):
            client.complete("system", "prompt")

    @patch.object(LLMClient, '__init__', lambda self, **kwargs: None)
    @patch('gitstyle.llm_client.time.sleep')
    def test_exponential_backoff_delays(self, mock_sleep):
        """Backoff should double each attempt: 2, 4, 8, ..."""
        client = LLMClient()
        client.model = "test"
        client._client = MagicMock()
        call_count = [0]

        def mock_stream(**kwargs):
            call_count[0] += 1
            if call_count[0] <= 3:
                raise anthropic.APIStatusError(
                    message="Overloaded",
                    response=MagicMock(status_code=529, headers={}),
                    body={"error": {"type": "overloaded_error", "message": "Overloaded"}},
                )
            mock_ctx = MagicMock()
            mock_msg = MagicMock()
            mock_msg.stop_reason = "end_turn"
            mock_msg.content = [MagicMock(text="ok")]
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_ctx.get_final_message.return_value = mock_msg
            return mock_ctx

        client._client.messages.stream = mock_stream
        client.complete("system", "prompt")
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [2.0, 4.0, 8.0]
