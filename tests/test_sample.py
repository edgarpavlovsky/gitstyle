"""Tests for the sample stage."""

from gitstyle.config import SampleConfig
from gitstyle.models import Commit, CommitCluster, CommitFile, RepoInfo
from gitstyle.sample import _detect_language, cluster_commits, run_sample, sample_cluster


def _make_commit(sha: str, repo: str, files: list[tuple[str, int, int]] | None = None) -> Commit:
    commit_files = []
    adds = 0
    dels = 0
    if files:
        for fname, a, d in files:
            commit_files.append(CommitFile(filename=fname, additions=a, deletions=d))
            adds += a
            dels += d
    return Commit(
        sha=sha,
        repo=repo,
        message=f"commit {sha}",
        date=f"2024-01-{int(sha, 16) % 28 + 1:02d}T00:00:00Z" if sha.isalnum() else "2024-01-01",
        files=commit_files,
        additions=adds,
        deletions=dels,
    )


def test_detect_language_python():
    commit = _make_commit("a1", "u/r", [("main.py", 10, 5), ("test.py", 3, 1)])
    assert _detect_language(commit) == "python"


def test_detect_language_typescript():
    commit = _make_commit("b2", "u/r", [("App.tsx", 20, 10), ("index.ts", 5, 2)])
    assert _detect_language(commit) == "typescript"


def test_detect_language_none():
    commit = _make_commit("c3", "u/r", [("Makefile", 5, 2)])
    assert _detect_language(commit) is None


def test_cluster_commits():
    commits = [
        _make_commit("a1", "u/repo1", [("main.py", 10, 5)]),
        _make_commit("b2", "u/repo1", [("util.py", 8, 3)]),
        _make_commit("c3", "u/repo2", [("app.ts", 15, 7)]),
    ]
    repos = [
        RepoInfo(name="repo1", full_name="u/repo1"),
        RepoInfo(name="repo2", full_name="u/repo2"),
    ]
    clusters = cluster_commits(commits, repos)
    labels = {c.label for c in clusters}
    assert "u/repo1:python" in labels
    assert "u/repo2:typescript" in labels


def test_sample_cluster_under_limit():
    commits = [_make_commit(f"{i:02x}", "u/r", [("f.py", 10, 5)]) for i in range(5)]
    cluster = CommitCluster(label="u/r:python", repo="u/r", language="python", commits=commits)
    config = SampleConfig(max_samples_per_cluster=20)
    result = sample_cluster(cluster, config)
    assert len(result.commits) == 5  # No sampling needed


def test_sample_cluster_over_limit():
    commits = [_make_commit(f"{i:02x}", "u/r", [("f.py", i * 5, i * 2)]) for i in range(50)]
    cluster = CommitCluster(label="u/r:python", repo="u/r", language="python", commits=commits)
    config = SampleConfig(max_samples_per_cluster=10, min_diff_lines=1)
    result = sample_cluster(cluster, config)
    assert len(result.commits) <= 10


def test_sample_cluster_recent_strategy():
    commits = [_make_commit(f"{i:02x}", "u/r", [("f.py", 10, 5)]) for i in range(30)]
    cluster = CommitCluster(label="u/r:python", repo="u/r", language="python", commits=commits)
    config = SampleConfig(max_samples_per_cluster=5, strategy="recent")
    result = sample_cluster(cluster, config)
    assert len(result.commits) <= 5


def test_run_sample():
    commits = [_make_commit(f"{i:02x}", "u/r", [("f.py", 10, 5)]) for i in range(10)]
    repos = [RepoInfo(name="r", full_name="u/r")]
    config = SampleConfig(max_samples_per_cluster=20)
    clusters = run_sample(commits, repos, config)
    assert len(clusters) >= 1
    assert all(isinstance(c, CommitCluster) for c in clusters)
