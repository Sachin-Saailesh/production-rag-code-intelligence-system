"""
Centralized configuration using Pydantic Settings.
All values are loaded from environment variables / .env file.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # --- API Keys ---
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    cohere_api_key: str = Field(default="", alias="COHERE_API_KEY")

    # --- LLM ---
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, alias="LLM_TEMPERATURE")
    max_output_tokens: int = Field(default=4096, alias="MAX_OUTPUT_TOKENS")
    max_context_tokens: int = Field(default=128_000, alias="MAX_CONTEXT_TOKENS")

    # Azure-specific
    azure_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    azure_api_version: str = Field(default="2025-01-01-preview", alias="AZURE_OPENAI_API_VERSION")
    azure_deployment: str = Field(default="", alias="AZURE_OPENAI_DEPLOYMENT")

    # --- Embeddings ---
    embedding_provider: str = Field(default="sentence_transformers", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="mixedbread-ai/mxbai-embed-large-v1", alias="EMBEDDING_MODEL")
    embedding_dim: int = Field(default=1024, alias="EMBEDDING_DIM")

    # --- Qdrant ---
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="codebase_analyst", alias="QDRANT_COLLECTION")

    # --- Redis ---
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")

    # --- Repository ---
    default_repo_url: str = Field(
        default="https://github.com/tiangolo/fastapi.git",
        alias="DEFAULT_REPO_URL",
    )
    default_repo_name: str = Field(default="fastapi", alias="DEFAULT_REPO_NAME")

    # --- Retrieval ---
    top_k_dense: int = Field(default=10, alias="TOP_K_DENSE")
    top_k_sparse: int = Field(default=10, alias="TOP_K_SPARSE")
    top_k_rerank: int = Field(default=5, alias="TOP_K_RERANK")
    dense_weight: float = Field(default=0.6, alias="DENSE_WEIGHT")
    rerank_enabled: bool = Field(default=True, alias="RERANK_ENABLED")

    # --- Chunking ---
    max_lines_per_chunk: int = Field(default=80, alias="MAX_LINES_PER_CHUNK")
    max_file_size: int = Field(default=1_000_000, alias="MAX_FILE_SIZE")

    # --- Server ---
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    # --- Paths ---
    data_dir: Path = Field(default=Path("data"))
    index_dir: Path = Field(default=Path("index"))
    cache_dir: Path = Field(default=Path("cache"))
    batch_size: int = Field(default=32)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
        "extra": "ignore",
    }

    def ensure_dirs(self) -> None:
        for d in [self.data_dir, self.index_dir, self.cache_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
