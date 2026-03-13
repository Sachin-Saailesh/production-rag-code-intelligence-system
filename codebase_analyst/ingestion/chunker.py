"""
Structure-aware code chunker.
Splits code at function/class boundaries where possible,
falls back to line-based chunking.
"""
import re
from typing import List, Dict, Any

from ..config import settings


class CodeChunker:
    """Chunks code documents respecting structural boundaries."""

    def __init__(self, max_lines: int = None):
        self.max_lines = max_lines or settings.max_lines_per_chunk

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a document into chunks.
        Uses function/class boundaries for Python, falls back to line-based splitting.
        """
        language = doc.get("language", "text")
        content = doc.get("content", "")
        functions = doc.get("functions", [])
        classes = doc.get("classes", [])

        if language == "python" and (functions or classes):
            return self._structural_chunk(doc, functions, classes)
        return self._line_chunk(doc)

    def _structural_chunk(
        self, doc: Dict[str, Any], functions: List[Dict], classes: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Chunk at function/class boundaries for Python files."""
        lines = doc["content"].splitlines()
        total_lines = len(lines)
        chunks = []
        chunk_idx = 0

        # Collect symbol boundaries sorted by line number
        boundaries = []
        for func in functions:
            boundaries.append({
                "name": func["name"],
                "type": "function",
                "lineno": func.get("lineno", 1),
            })
        for cls in classes:
            boundaries.append({
                "name": cls["name"],
                "type": "class",
                "lineno": cls.get("lineno", 1),
            })
        boundaries.sort(key=lambda b: b["lineno"])

        if not boundaries:
            return self._line_chunk(doc)

        # Build chunks from boundaries
        prev_line = 0
        for i, boundary in enumerate(boundaries):
            start = boundary["lineno"] - 1  # 0-indexed

            # If there's a gap before the first symbol or between symbols, chunk it
            if start > prev_line:
                gap_block = lines[prev_line:start]
                if gap_block and any(line.strip() for line in gap_block):
                    chunks.extend(self._split_block(
                        doc, gap_block, prev_line + 1, start, chunk_idx,
                        symbol_name="", symbol_type="module",
                    ))
                    chunk_idx += 1

            # Determine end of this symbol
            if i + 1 < len(boundaries):
                end = boundaries[i + 1]["lineno"] - 1
            else:
                end = total_lines

            symbol_block = lines[start:end]
            for sub_chunk in self._split_block(
                doc, symbol_block, start + 1, end, chunk_idx,
                symbol_name=boundary["name"],
                symbol_type=boundary["type"],
            ):
                chunks.append(sub_chunk)
                chunk_idx += 1

            prev_line = end

        # Remaining lines after last symbol
        if prev_line < total_lines:
            remaining = lines[prev_line:]
            if remaining and any(line.strip() for line in remaining):
                chunks.extend(self._split_block(
                    doc, remaining, prev_line + 1, total_lines, chunk_idx,
                    symbol_name="", symbol_type="module",
                ))

        return chunks if chunks else self._line_chunk(doc)

    def _split_block(
        self,
        doc: Dict[str, Any],
        block_lines: List[str],
        start_line: int,
        end_line: int,
        chunk_idx: int,
        symbol_name: str = "",
        symbol_type: str = "",
    ) -> List[Dict[str, Any]]:
        """Split a block of lines into chunks of max_lines."""
        chunks = []
        i = 0
        while i < len(block_lines):
            sub = block_lines[i : i + self.max_lines]
            sl = start_line + i
            el = sl + len(sub) - 1
            cid = f"{doc['file_path']}::chunk_{chunk_idx}"

            chunks.append({
                "chunk_id": cid,
                "file_path": doc["file_path"],
                "language": doc.get("language", "text"),
                "content": "\n".join(sub),
                "start_line": sl,
                "end_line": el,
                "symbol_name": symbol_name,
                "symbol_type": symbol_type,
                "functions": doc.get("functions", []),
                "classes": doc.get("classes", []),
                "imports": doc.get("imports", []),
                "content_hash": doc.get("content_hash", ""),
            })
            i += self.max_lines
            chunk_idx += 1
        return chunks

    def _line_chunk(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simple line-based chunking fallback."""
        lines = doc["content"].splitlines()
        chunks = []
        i = 0
        chunk_idx = 0

        while i < len(lines):
            block = lines[i : i + self.max_lines]
            start_line = i + 1
            end_line = i + len(block)

            chunks.append({
                "chunk_id": f"{doc['file_path']}::chunk_{chunk_idx}",
                "file_path": doc["file_path"],
                "language": doc.get("language", "text"),
                "content": "\n".join(block),
                "start_line": start_line,
                "end_line": end_line,
                "symbol_name": "",
                "symbol_type": "",
                "functions": [],
                "classes": [],
                "imports": doc.get("imports", []),
                "content_hash": doc.get("content_hash", ""),
            })
            i += self.max_lines
            chunk_idx += 1

        return chunks
