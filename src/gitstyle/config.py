"""Configuration models for gitstyle."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class FetchConfig(BaseModel):
    """Configuration for the fetch stage."""

    username: str
    token: str | None = Field(default_factory=lambda: os.environ.get("GITHUB_TOKEN"))
    include_repos: list[str] | None = None
    exclude_repos: list[str] | None = None
    include_forks: bool = False
    include_contributions: bool = False
    max_commits_per_repo: int = 200
    since: str | None = None
    until: str | None = None


class SampleConfig(BaseModel):
    """Configuration for the sampling stage."""

    max_samples_per_cluster: int = 20
    min_diff_lines: int = 5
    strategy: str = "balanced"  # balanced | recent | largest


class LLMConfig(BaseModel):
    """Configuration for LLM stages."""

    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    api_key: str | None = Field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY"))


class PipelineConfig(BaseModel):
    """Top-level configuration."""

    fetch: FetchConfig
    sample: SampleConfig = SampleConfig()
    llm: LLMConfig = LLMConfig()
    output_dir: Path = Path("wiki")
    cache_dir: Path = Path(".gitstyle")
