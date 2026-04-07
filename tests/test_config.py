"""Tests for configuration models."""

from pathlib import Path

from gitstyle.config import FetchConfig, LLMConfig, PipelineConfig, SampleConfig


def test_fetch_config_defaults():
    config = FetchConfig(username="testuser")
    assert config.max_commits_per_repo == 200
    assert config.include_forks is False
    assert config.include_repos is None
    assert config.exclude_repos is None


def test_sample_config_defaults():
    config = SampleConfig()
    assert config.max_samples_per_cluster == 20
    assert config.strategy == "balanced"
    assert config.min_diff_lines == 5


def test_llm_config_defaults():
    config = LLMConfig()
    assert "claude" in config.model.lower() or "sonnet" in config.model.lower()
    assert config.max_tokens == 4096


def test_pipeline_config():
    config = PipelineConfig(fetch=FetchConfig(username="testuser"))
    assert config.output_dir == Path("wiki")
    assert config.cache_dir == Path(".gitstyle")
    assert config.sample.max_samples_per_cluster == 20
