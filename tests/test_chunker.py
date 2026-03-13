"""Tests for the code chunker."""
import pytest
from codebase_analyst.ingestion.chunker import CodeChunker


def _make_doc(content: str, language: str = "python", functions=None, classes=None):
    return {
        "file_path": "test.py",
        "language": language,
        "content": content,
        "functions": functions or [],
        "classes": classes or [],
        "imports": [],
        "content_hash": "abc123",
    }


class TestLineChunking:
    def test_single_chunk(self):
        doc = _make_doc("line1\nline2\nline3")
        chunker = CodeChunker(max_lines=10)
        chunks = chunker.chunk_document(doc)
        assert len(chunks) == 1
        assert chunks[0]["start_line"] == 1
        assert chunks[0]["end_line"] == 3

    def test_multiple_chunks(self):
        content = "\n".join([f"line_{i}" for i in range(20)])
        doc = _make_doc(content)
        chunker = CodeChunker(max_lines=5)
        chunks = chunker.chunk_document(doc)
        assert len(chunks) == 4
        assert chunks[0]["start_line"] == 1
        assert chunks[0]["end_line"] == 5
        assert chunks[-1]["start_line"] == 16

    def test_chunk_metadata(self):
        doc = _make_doc("line1\nline2", language="javascript")
        chunker = CodeChunker(max_lines=10)
        chunks = chunker.chunk_document(doc)
        assert chunks[0]["language"] == "javascript"
        assert chunks[0]["file_path"] == "test.py"
        assert "chunk_id" in chunks[0]


class TestStructuralChunking:
    def test_python_function_boundaries(self):
        content = "import os\n\ndef foo():\n    pass\n\ndef bar():\n    return 42\n"
        functions = [
            {"name": "foo", "lineno": 3},
            {"name": "bar", "lineno": 6},
        ]
        doc = _make_doc(content, functions=functions)
        chunker = CodeChunker(max_lines=100)
        chunks = chunker.chunk_document(doc)
        # Should produce at least 2 chunks (preamble + functions)
        assert len(chunks) >= 2
        symbols = [c.get("symbol_name", "") for c in chunks]
        assert "foo" in symbols or "bar" in symbols

    def test_non_python_falls_back(self):
        doc = _make_doc("const x = 1;\nconst y = 2;", language="javascript")
        chunker = CodeChunker(max_lines=10)
        chunks = chunker.chunk_document(doc)
        assert len(chunks) == 1
