"""Tests for data models."""

from gitstyle.models import (
    Commit,
    CommitCluster,
    CommitFile,
    LintIssue,
    RepoInfo,
    StyleExtractionResult,
    StyleObservation,
    WikiArticle,
)


def test_repo_info_defaults():
    repo = RepoInfo(name="test", full_name="user/test")
    assert repo.language is None
    assert repo.is_fork is False
    assert repo.languages == {}


def test_commit_file():
    f = CommitFile(filename="main.py", status="modified", additions=10, deletions=3)
    assert f.filename == "main.py"
    assert f.patch is None


def test_commit_with_files():
    commit = Commit(
        sha="abc123",
        repo="user/repo",
        message="fix bug",
        date="2024-01-01T00:00:00Z",
        files=[CommitFile(filename="a.py", additions=5, deletions=2)],
        additions=5,
        deletions=2,
    )
    assert len(commit.files) == 1
    assert commit.additions == 5


def test_commit_cluster():
    commits = [
        Commit(sha="a", repo="user/repo", message="one", date="2024-01-01"),
        Commit(sha="b", repo="user/repo", message="two", date="2024-01-02"),
    ]
    cluster = CommitCluster(
        label="user/repo:python",
        repo="user/repo",
        language="python",
        commits=commits,
    )
    assert len(cluster.commits) == 2
    assert cluster.language == "python"


def test_style_observation():
    obs = StyleObservation(
        cluster_label="user/repo:python",
        category="naming-conventions",
        observation="Uses snake_case",
        evidence=["abc123"],
        confidence="high",
    )
    assert obs.category == "naming-conventions"


def test_style_extraction_result():
    result = StyleExtractionResult(cluster_label="user/repo:python")
    assert result.observations == []


def test_wiki_article():
    article = WikiArticle(
        slug="naming-conventions",
        title="Naming Conventions",
        category="style",
        content="# Naming\nUses snake_case.",
        sources=["user/repo"],
    )
    assert article.confidence == "medium"
    assert article.related == []


def test_lint_issue():
    issue = LintIssue(
        article="naming-conventions",
        severity="warning",
        message="Weak evidence",
    )
    assert issue.suggestion is None


def test_model_serialization():
    commit = Commit(sha="abc", repo="u/r", message="test", date="2024-01-01")
    json_str = commit.model_dump_json()
    restored = Commit.model_validate_json(json_str)
    assert restored.sha == "abc"
