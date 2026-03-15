import hashlib
import logging
import numpy as np
from typing import List

from ..config import settings

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    from openai import OpenAI, AzureOpenAI
except ImportError:
    OpenAI = None
    AzureOpenAI = None


class EmbeddingEngine:
    """Embedding engine supporting OpenAI, Azure OpenAI, SentenceTransformers, and fallback."""

    def __init__(self, model_name: str = None, provider: str = None):
        self.provider = provider or settings.embedding_provider
        self.model_name = model_name or settings.embedding_model
        self.dimension = settings.embedding_dim
        self.model = None
        self.openai_client = None

        if self.provider == "openai":
            if not OpenAI:
                logger.warning("openai package not installed. Falling back to MiniHash.")
                self.provider = "minihash"
                self.dimension = 512
            else:
                logger.info("Using OpenAI embeddings: %s", self.model_name)
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                # Ensure dimension matches typical OpenAI models if not explicitly customized
                if "text-embedding-3-small" in self.model_name:
                    self.dimension = 1536
                elif "text-embedding-3-large" in self.model_name:
                    self.dimension = 3072
                elif "text-embedding-ada-002" in self.model_name:
                    self.dimension = 1536
                    
        elif self.provider == "azure":
            if not AzureOpenAI:
                 logger.warning("openai package not installed. Falling back to MiniHash.")
                 self.provider = "minihash"
                 self.dimension = 512
            else:
                 logger.info("Using Azure OpenAI embeddings: %s", self.model_name)
                 self.openai_client = AzureOpenAI(
                     api_key=settings.openai_api_key,
                     api_version=settings.azure_api_version,
                     azure_endpoint=settings.azure_endpoint
                 )
                 self.dimension = 1536

        elif self.provider == "sentence_transformers":
            if SentenceTransformer:
                logger.info("Loading embedding model: %s", self.model_name)
                try:
                    self.model = SentenceTransformer(self.model_name)
                    self.dimension = self.model.get_sentence_embedding_dimension()
                except Exception as e:
                    logger.warning("Failed to load SentenceTransformer: %s", e)
                    self.provider = "minihash"
                    self.dimension = 512
            else:
                logger.warning("sentence-transformers not installed. Falling back.")
                self.provider = "minihash"
                self.dimension = 512

        if self.provider not in ["openai", "azure", "sentence_transformers"]:
            logger.warning("Using fallback MiniHash embeddings (low quality)")
            self.dimension = 512
            self.provider = "minihash"

    def encode(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        if not texts:
            return np.array([])
            
        if self.provider in ["openai", "azure"]:
            return self._openai_batch(texts, batch_size)
        elif self.provider == "sentence_transformers" and self.model:
            return self.model.encode(
                texts, batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
            )
        return self._minihash_batch(texts)
        
    def _openai_batch(self, texts: List[str], batch_size: int) -> np.ndarray:
        import time
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            try:
                # Truncate very long texts to avoid token limit errors for basic resilience
                safe_batch = [t[:30000] for t in batch] 
                response = self.openai_client.embeddings.create(
                    model=self.model_name,
                    input=safe_batch
                )
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error("OpenAI embedding failed for batch: %s", e)
                # Fallback to zero vectors for this batch to avoid crashing the whole pipeline
                all_embeddings.extend([np.zeros(self.dimension).tolist() for _ in batch])
                time.sleep(1) # Backoff
                
        return np.array(all_embeddings, dtype=np.float32)

    def _minihash_batch(self, texts: List[str]) -> np.ndarray:
        return np.vstack([self._minihash_vec(t) for t in texts])

    def _minihash_vec(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimension, dtype=np.float32)
        for seed in (17, 101, 313, 997):
            h = int(hashlib.md5((str(seed) + text).encode()).hexdigest(), 16)
            for i in range(self.dimension):
                vec[i] += ((h >> (i % 64)) & 1)
        norm = np.linalg.norm(vec) + 1e-8
        return (vec / norm).astype(np.float32)
