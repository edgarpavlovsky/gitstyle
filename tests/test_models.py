"""Tests for pydantic models."""

from datetime import datetime, timezone

from gitstyle.models import (
    ClusterExtraction,
    CommitFile,
    LintIssue,
    LintReport,
    LintSeverity,
    Observation,
    RawCommit,
    SampledCluster,
    StyleDimension,
    WikiArticle,
)


def test_raw_commit_roundtrip():
    c = RawCommit(
        sha="abc1234",
        repo="user/repo",
        message="fix: handle edge case",
        author="testuser",
        authored_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        additions=10,
        deletions=3,
        files=[
            CommitFile(filename="src/main.py", status="modified", additions=10, deletions=3)
        ],
        languages=["Python"],
    )
    json_str = c.model_dump_json()
    restored = RawCommit.model_validate_json(json_str)
    assert restored.sha == "abc1234"
    assert restored.repo == "user/repo"
    assert len(restored.files) == 1
    assert restored.files[0].filename == "src/main.py"


def test_observation_confidence_bounds():
    obs = Observation(
        dimension=StyleDimension.NAMING,
        claim="Uses snake_case for functions",
        evidence=["abc1234", "def5678"],
        confidence=0.9,
        language="Python",
    )
    assert obs.confidence == 0.9
    assert obs.dimension == StyleDimension.NAMING


def test_sampled_cluster():
    commit = RawCommit(
        sha="abc",
        repo="u/r",
        message="test",
        author="u",
        authored_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    cluster = SampledCluster(
        repo="u/r",
        language="Python",
        commits=[commit],
        total_in_group=50,
    )
    assert cluster.total_in_group == 50
    assert len(cluster.commits) == 1


def test_wiki_article():
    article = WikiArticle(
        slug="naming-conventions",
        title="Naming Conventions",
        category="dimension",
        confidence=0.85,
        source_repos=["user/repo1", "user/repo2"],
        content="# Naming\n\nThe developer uses snake_case...",
        wikilinks=["code-structure", "patterns"],
    )
    assert article.slug == "naming-conventions"
    assert len(article.wikilinks) == 2


def test_lint_report():
    report = LintReport(
        issues=[
            LintIssue(
                article="naming-conventions",
                severity=LintSeverity.WARNING,
                message="Weak evidence for claim about camelCase",
                suggestion="Add more commit references",
            )
        ],
        passed=False,
    )
    assert not report.passed
    assert len(report.issues) == 1
    assert report.issues[0].severity == LintSeverity.WARNING


def test_cluster_extraction():
    ext = ClusterExtraction(
        repo="u/r",
        language="Python",
        observations=[
            Observation(
                dimension=StyleDimension.CODE_STRUCTURE,
                claim="Small, focused functions",
                evidence=["abc"],
            )
        ],
    )
    assert len(ext.observations) == 1
