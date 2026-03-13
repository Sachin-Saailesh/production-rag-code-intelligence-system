"""Tests for configuration loading."""
import os
import pytest


def test_settings_loads_defaults(monkeypatch):
    """Settings should load with default values when no env vars are set."""
    # Ignore .env file and environment variables for this test
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    from codebase_analyst.config import Settings
    s = Settings(_env_file=None)
    assert s.llm_provider == "openai"
    assert s.port == 8000
    assert s.max_lines_per_chunk == 80
    assert s.dense_weight == 0.6
    assert s.cache_ttl == 3600


def test_settings_from_env(monkeypatch):
    """Settings should be overridable via environment variables."""
    monkeypatch.setenv("LLM_PROVIDER", "azure")
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("DENSE_WEIGHT", "0.8")

    from codebase_analyst.config import Settings
    s = Settings()
    assert s.llm_provider == "azure"
    assert s.port == 9000
    assert s.dense_weight == 0.8


def test_settings_ensure_dirs(tmp_path, monkeypatch):
    """ensure_dirs should create data, index, and cache directories."""
    from codebase_analyst.config import Settings
    s = Settings(
        data_dir=tmp_path / "data",
        index_dir=tmp_path / "index",
        cache_dir=tmp_path / "cache",
    )
    s.ensure_dirs()
    assert (tmp_path / "data").exists()
    assert (tmp_path / "index").exists()
    assert (tmp_path / "cache").exists()
