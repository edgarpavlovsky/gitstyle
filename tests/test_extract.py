"""Tests for the extract stage."""

from pathlib import Path
from unittest.mock import MagicMock

from gitstyle.models import Commit, CommitCluster, CommitFile
from gitstyle.extract import extract_cluster, _format_commit


def test_format_commit():
    commit = Commit(
        sha="abc12345678",
        repo="user/repo",
        message="fix: handle edge case\n\nLonger description",
        date="2026-01-01T00:00:00Z",
        files=[CommitFile(filename="main.py", status="modified", additions=5, deletions=2, patch="+ new line")],
    )
    text = _format_commit(commit)
    assert "abc12345" in text
    assert "fix: handle edge case" in text
    assert "main.py" in text
    assert "+ new line" in text


def test_extract_cluster_parses_json(tmp_path: Path):
    llm = MagicMock()
    llm.complete_json.return_value = [
        {
            "category": "naming-conventions",
            "observation": "Uses snake_case",
            "evidence": ["abc123"],
            "confidence": "high",
        }
    ]

    cluster = CommitCluster(
        label="user/repo:python",
        repo="user/repo",
        language="python",
        commits=[
            Commit(
                sha="abc123",
                repo="user/repo",
                message="test",
                date="2026-01-01",
                files=[CommitFile(filename="main.py", additions=10, deletions=5, patch="+ code")],
            )
        ],
    )

    result = extract_cluster(cluster, llm, tmp_path)
    assert len(result.observations) == 1
    assert result.observations[0].category == "naming-conventions"
    assert result.observations[0].confidence == "high"


def test_extract_cluster_handles_error(tmp_path: Path):
    llm = MagicMock()
    llm.complete_json.side_effect = Exception("API error")

    cluster = CommitCluster(
        label="user/repo:python",
        repo="user/repo",
        language="python",
        commits=[Commit(sha="abc", repo="user/repo", message="t", date="2026-01-01")],
    )

    result = extract_cluster(cluster, llm, tmp_path)
    assert len(result.observations) == 0


def test_extract_cluster_uses_cache(tmp_path: Path):
    from gitstyle.models import StyleExtractionResult, StyleObservation

    cache_path = tmp_path / "extractions" / "user_repo_python.json"
    cache_path.parent.mkdir(parents=True)
    cached = StyleExtractionResult(
        cluster_label="user/repo:python",
        observations=[
            StyleObservation(
                cluster_label="user/repo:python",
                category="testing",
                observation="Cached result",
                evidence=["sha1"],
            )
        ],
    )
    cache_path.write_text(cached.model_dump_json())

    llm = MagicMock()  # Should NOT be called
    cluster = CommitCluster(
        label="user/repo:python",
        repo="user/repo",
        language="python",
        commits=[],
    )

    result = extract_cluster(cluster, llm, tmp_path)
    assert len(result.observations) == 1
    assert result.observations[0].observation == "Cached result"
    llm.complete_json.assert_not_called()
