import os
import sys
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Attempt to load from Colab Secrets if available
try:
    from google.colab import userdata
    known_keys = [
        "OPENAI_API_KEY", "COHERE_API_KEY", 
        "AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_MODEL", 
        "AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_ENDPOINT"
    ]
    for key in known_keys:
        if key not in os.environ:
            try:
                val = userdata.get(key)
                if val:
                    os.environ[key] = val
            except Exception:
                pass
except ImportError:
    pass

@dataclass
class Config:
    """System configuration"""
    # Paths
    # Detect if running in Colab to determine base path
    is_colab = "google.colab" in sys.modules
    base_dir: Path = Path("/content") if is_colab else Path(os.getcwd())
    
    work_dir: Path = base_dir
    data_dir: Path = base_dir / "data"
    index_dir: Path = base_dir / "index"
    cache_dir: Path = base_dir / "cache"

    # Repository
    repo_url: str = "https://github.com/tiangolo/fastapi.git"
    repo_name: str = "fastapi"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 128
    max_file_size: int = 1_000_000  # 1 MB
    max_lines_per_chunk: int = 80

    # Embeddings
    embedding_model: str = "mixedbread-ai/mxbai-embed-large-v1"
    embedding_dim: int = 1024

    # Retrieval
    top_k_dense: int = 5
    top_k_sparse: int = 5
    top_k_rerank: int = 5

    # LLM (Azure OpenAI Defaults)
    llm_provider: str = "azure_openai"
    # Using the hardcoded defaults requested by the user
    llm_model: str = os.getenv("AZURE_OPENAI_MODEL", "gpt-test")
    api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")
    azure_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "https://aifoundry2212.cognitiveservices.azure.com/")
    
    # Other API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")

    max_context_tokens: int = 128_000
    max_output_tokens: int = 4_096
    temperature: float = 0.1

    # Cache
    use_redis: bool = False  # Set to True if Redis is available
    cache_ttl: int = 3600

    # Performance
    batch_size: int = 32
    use_gpu: bool = True

    def ensure_dirs(self):
        """Ensure that all required directories exist."""
        for d in [self.data_dir, self.index_dir, self.cache_dir]:
            d.mkdir(parents=True, exist_ok=True)
        print(f"📂 Verified directories: {self.data_dir}, {self.index_dir}, {self.cache_dir}")

# Global config instance
config = Config()
