"""Configuration for gitstyle."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class GitStyleConfig(BaseModel):
    username: str
    github_token: Optional[str] = None
    output_dir: Path = Path("wiki")
    cache_dir: Path = Path(".gitstyle")
    max_commits: int = 2000
    max_repos: int = 30  # For orgs: limit repos (sorted by stars). 0 = no limit.
    samples_per_group: int = 20
    repos: Optional[list[str]] = None  # None = all public repos
    since: Optional[str] = None  # ISO date string
    until: Optional[str] = None
    llm_model: str = "claude-sonnet-4-20250514"
    dry_run: bool = False
    fresh: bool = False  # --fresh forces a full re-run, ignoring cache
    context_type: Optional[str] = None  # "User" or "Organization" — auto-detected

    def commits_path(self) -> Path:
        return self.cache_dir / "commits.jsonl"

    def samples_path(self) -> Path:
        return self.cache_dir / "samples.json"

    def extractions_path(self) -> Path:
        return self.cache_dir / "extractions.json"

    def articles_path(self) -> Path:
        return self.cache_dir / "articles.json"

    def lint_path(self) -> Path:
        return self.cache_dir / "lint.json"

    def ensure_cache_dir(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
