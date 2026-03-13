"""Internal domain models for the codebase analyst."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class CodeChunk:
    """Represents a chunk of source code with metadata."""
    chunk_id: str
    file_path: str
    language: str
    content: str
    start_line: int
    end_line: int
    repo_name: str = ""
    branch: str = ""
    commit_sha: str = ""
    symbol_name: str = ""
    symbol_type: str = ""  # function, class, method, module
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    content_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "file_path": self.file_path,
            "language": self.language,
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "repo_name": self.repo_name,
            "branch": self.branch,
            "commit_sha": self.commit_sha,
            "symbol_name": self.symbol_name,
            "symbol_type": self.symbol_type,
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "tags": self.tags,
            "content_hash": self.content_hash,
        }


@dataclass
class RetrievedCandidate:
    """A candidate chunk returned from retrieval."""
    chunk_id: str
    file_path: str
    language: str
    content: str
    start_line: int
    end_line: int
    score: float = 0.0
    source: str = ""  # dense, sparse, symbol, graph


@dataclass
class QueryClassification:
    """Lightweight classification of a user query."""
    query_type: str  # symbol_lookup, semantic, architecture, dependency, config
    confidence: float = 1.0
    extracted_symbols: List[str] = field(default_factory=list)
