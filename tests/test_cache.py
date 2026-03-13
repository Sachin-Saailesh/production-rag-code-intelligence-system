"""Tests for cache key versioning and behavior."""
import pytest
from codebase_analyst.services.cache import SemanticCache


class TestSemanticCache:
    def test_miss_returns_none(self):
        cache = SemanticCache()
        result = cache.get("some query")
        assert result is None

    def test_set_and_get(self):
        cache = SemanticCache()
        # Store with no repo/version
        cache.set("test query", {"answer": "hello"})
        result = cache.get("test query")
        assert result is not None
        assert result["answer"] == "hello"

    def test_version_aware_keys(self):
        """Different repo/version combos should produce different cache keys."""
        cache = SemanticCache()
        cache.set("query", {"v": 1}, repo_name="repo_a", index_version="v1")
        cache.set("query", {"v": 2}, repo_name="repo_a", index_version="v2")

        r1 = cache.get("query", repo_name="repo_a", index_version="v1")
        r2 = cache.get("query", repo_name="repo_a", index_version="v2")
        assert r1["v"] == 1
        assert r2["v"] == 2

    def test_invalidate(self):
        cache = SemanticCache()
        cache.set("q", {"data": True})
        assert cache.get("q") is not None
        cache.invalidate("q")
        assert cache.get("q") is None

    def test_stats(self):
        cache = SemanticCache()
        cache.get("miss1")
        cache.get("miss2")
        cache.set("hit", {"data": True})
        cache.get("hit")
        stats = cache.stats
        assert stats["misses"] >= 2
        assert stats["hits"] >= 1
        assert "hit_rate" in stats
