import numpy as np
from typing import List
from ..config import config

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class EmbeddingEngine:
    """
    Embedding engine using SentenceTransformers.
    Falls back to a deterministic minihash if ST is missing (for lightweight testing).
    """
    def __init__(self, model_name: str = None, use_gpu: bool = None):
        self.model_name = model_name or config.embedding_model
        self.use_gpu = use_gpu if use_gpu is not None else config.use_gpu
        self.model = None
        self.dimension = config.embedding_dim

        if SentenceTransformer:
            print(f"🔹 Loading Embedding Model: {self.model_name}")
            device = "cuda" if self.use_gpu else "cpu"
            try:
                self.model = SentenceTransformer(self.model_name, device=device)
                self.dimension = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                print(f"Warning: Failed to load SentenceTransformer: {e}")
                self.model = None
        
        if not self.model:
            print("⚠️ using fallback MiniHash embeddings (low quality)")
            self.dimension = 512

    def encode(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        if self.model:
            return self.model.encode(texts, batch_size=batch_size, show_progress_bar=show_progress, convert_to_numpy=True)
        else:
            return self._minihash_batch(texts)

    def _minihash_batch(self, texts: List[str]) -> np.ndarray:
        out = []
        for t in texts:
            out.append(self._minihash_vec(t))
        return np.vstack(out)

    def _minihash_vec(self, text: str) -> np.ndarray:
        # deterministic random vector
        import hashlib
        vec = np.zeros(self.dimension, dtype=np.float32)
        for seed in (17, 101, 313, 997):
            h = int(hashlib.md5((str(seed) + text).encode()).hexdigest(), 16)
            for i in range(self.dimension):
                vec[i] += ((h >> (i % 64)) & 1)
        norm = np.linalg.norm(vec) + 1e-8
        return (vec / norm).astype(np.float32)
