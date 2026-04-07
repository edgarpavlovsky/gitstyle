"""Tests for the sample stage."""

from datetime import datetime, timedelta, timezone

from gitstyle.config import GitStyleConfig
from gitstyle.models import RawCommit
from gitstyle.sample import _sample_group

_BASE_DATE = datetime(2025, 12, 31, tzinfo=timezone.utc)


def _make_commit(sha: str, additions: int = 5, days_ago: int = 0) -> RawCommit:
    return RawCommit(
        sha=sha,
        repo="u/r",
        message=f"commit {sha}",
        author="u",
        authored_at=_BASE_DATE - timedelta(days=days_ago),
        additions=additions,
        deletions=0,
        languages=["Python"],
    )


def test_sample_group_small():
    """When group has fewer commits than n, return all."""
    commits = [_make_commit(f"sha{i}") for i in range(5)]
    result = _sample_group(commits, n=20)
    assert len(result) == 5


def test_sample_group_exact():
    """When group has exactly n commits, return all."""
    commits = [_make_commit(f"sha{i}") for i in range(20)]
    result = _sample_group(commits, n=20)
    assert len(result) == 20


def test_sample_group_large():
    """When group has more than n, sample down to n."""
    commits = [_make_commit(f"sha{i:03d}", additions=i, days_ago=i) for i in range(100)]
    result = _sample_group(commits, n=20)
    assert len(result) == 20

    # Most recent should be included
    shas = {c.sha for c in result}
    assert "sha000" in shas  # most recent (days_ago=0)

    # Largest diff should be included
    assert "sha099" in shas  # most additions


def test_sample_group_deterministic():
    """Sampling should be deterministic (seeded random)."""
    commits = [_make_commit(f"sha{i:03d}", additions=i, days_ago=i) for i in range(100)]
    r1 = _sample_group(commits, n=20)
    r2 = _sample_group(commits, n=20)
    assert {c.sha for c in r1} == {c.sha for c in r2}
