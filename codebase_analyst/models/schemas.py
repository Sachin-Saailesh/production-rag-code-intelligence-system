"""Pydantic models for API request/response schemas."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language question about the codebase")
    repo_name: Optional[str] = Field(None, description="Repository name to query against")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    expand_query: bool = Field(default=False, description="Enable query expansion")


class Citation(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    language: str = ""
    snippet: str = ""
    score: float = 0.0


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    query_type: str = "general"
    latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    retrieval_latency_ms: float = 0.0
    rerank_latency_ms: float = 0.0
    cache_hit: bool = False
    chunks_retrieved: int = 0
    metadata: Dict[str, Any] = {}


class IngestRequest(BaseModel):
    repo_url: Optional[str] = Field(None, description="Git URL to clone and ingest")
    repo_path: Optional[str] = Field(None, description="Local path to ingest")
    repo_name: Optional[str] = Field(None, description="Repo identifier for indexing")
    force_reindex: bool = Field(default=False, description="Force full re-index even if unchanged")


class IngestResponse(BaseModel):
    status: str
    repo_name: str
    files_processed: int = 0
    chunks_created: int = 0
    files_skipped: int = 0
    duration_seconds: float = 0.0
    message: str = ""


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    services: Dict[str, str] = {}
