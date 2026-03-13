"""Tests for retrieval pipeline components."""
import pytest
from codebase_analyst.services.retrieval import classify_query, fuse_candidates


class TestQueryClassification:
    def test_symbol_lookup(self):
        result = classify_query("Where is UserModel defined?")
        assert result["query_type"] == "symbol_lookup"

    def test_architecture(self):
        result = classify_query("What is the overall architecture of the project?")
        assert result["query_type"] == "architecture"

    def test_dependency(self):
        result = classify_query("What does main.py import?")
        assert result["query_type"] == "dependency"

    def test_config(self):
        result = classify_query("What environment variables are used?")
        assert result["query_type"] == "config"

    def test_semantic_default(self):
        result = classify_query("Explain how error handling works")
        assert result["query_type"] == "semantic"


class TestFuseCandidates:
    def _chunk(self, cid, score=0.5):
        return {"chunk_id": cid, "content": f"content_{cid}", "score": score}

    def test_fusion_combines_sources(self):
        dense = [self._chunk("a", 0.9), self._chunk("b", 0.7)]
        sparse = [self._chunk("b", 0.8), self._chunk("c", 0.6)]
        fused = fuse_candidates(dense, sparse, [])
        ids = [f["chunk_id"] for f in fused]
        # b should be boosted (appears in both)
        assert "b" in ids
        assert "a" in ids
        assert "c" in ids

    def test_symbol_bonus(self):
        dense = [self._chunk("a", 0.5)]
        symbol = [self._chunk("b", 1.0)]
        fused = fuse_candidates(dense, [], symbol)
        ids = [f["chunk_id"] for f in fused]
        assert "b" in ids

    def test_empty_inputs(self):
        result = fuse_candidates([], [], [])
        assert result == []
