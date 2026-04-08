"""Tests for CLI interface."""

from typer.testing import CliRunner

from gitstyle.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.3.3" in result.stdout


def test_no_args():
    result = runner.invoke(app, [])
    # Typer exits with code 0 or 2 for no_args_is_help depending on version
    assert result.exit_code in (0, 2)


def test_run_no_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    result = runner.invoke(app, ["run", "someuser"])
    assert result.exit_code == 1
    assert "GITHUB_TOKEN" in result.stdout


def test_clean_nothing():
    result = runner.invoke(app, ["clean", "--cache", "/tmp/nonexistent_gitstyle_cache"])
    assert result.exit_code == 0
