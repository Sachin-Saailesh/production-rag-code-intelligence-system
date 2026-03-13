"""
Embedding engine using SentenceTransformers.
Falls back to deterministic minihash if SentenceTransformer is missing.
"""
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


class EmbeddingEngine:
    """Embedding engine with SentenceTransformer and fallback."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.model = None
        self.dimension = settings.embedding_dim

        if SentenceTransformer:
            logger.info("Loading embedding model: %s", self.model_name)
            try:
                self.model = SentenceTransformer(self.model_name)
                self.dimension = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                logger.warning("Failed to load SentenceTransformer: %s", e)
                self.model = None

        if not self.model:
            logger.warning("Using fallback MiniHash embeddings (low quality)")
            self.dimension = 512

    def encode(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        if self.model:
            return self.model.encode(
                texts, batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
            )
        return self._minihash_batch(texts)

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
