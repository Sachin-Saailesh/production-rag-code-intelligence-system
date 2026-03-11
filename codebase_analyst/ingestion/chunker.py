from typing import List, Dict, Any, Optional
from ..config import config

class CodeChunker:
    """Chunks code documents into smaller pieces"""
    
    def __init__(self, max_lines: int = None):
        self.max_lines = max_lines or config.max_lines_per_chunk

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a document into chunks of max_lines.
        Preserves metadata.
        """
        lines = doc["content"].splitlines()
        chunks = []
        i = 0
        chunk_idx = 0
        
        while i < len(lines):
            block = lines[i : i + self.max_lines]
            start_line = i + 1
            end_line = i + len(block)
            
            chunk_id = f"{doc['file_path']}::chunk_{chunk_idx}"
            
            # Basic naive extraction of context (could be improved with tree-sitter context)
            # For now, we just pass empty function/class lists or filter from doc if strictly inside
            # In this simple version, we don't recalculate function/class ownership per chunk yet.
            
            chunks.append({
                "chunk_id": chunk_id,
                "file_path": doc["file_path"],
                "language": doc["language"],
                "content": "\n".join(block),
                "start_line": start_line,
                "end_line": end_line,
                "functions": [], # Placeholder or need logic to map doc functions to this chunk range
                "classes": [],
            })
            
            i += self.max_lines
            chunk_idx += 1
            
        return chunks
