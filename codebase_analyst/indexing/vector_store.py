import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from ..config import config

class VectorStore:
    """Simple in-memory vector store with cosine similarity"""
    
    def __init__(self, collection_name: str, dimension: int, path: Path):
        self.collection_name = collection_name
        self.dimension = dimension
        self.path = path
        self._embeddings: Optional[np.ndarray] = None
        self._payloads: List[Dict[str, Any]] = []
        
    def _create_collection(self):
        self._embeddings = None
        self._payloads = []

    def add_vectors(self, embeddings: np.ndarray, payloads: List[Dict[str, Any]], batch_size: int = 100):
        if len(payloads) == 0:
            return
        assert embeddings.shape[0] == len(payloads)
        
        if self._embeddings is None:
            self._embeddings = embeddings.astype(np.float32)
        else:
            self._embeddings = np.vstack([self._embeddings, embeddings.astype(np.float32)])
        self._payloads.extend(payloads)

    def search(self, query_vec: np.ndarray, top_k: int = 10) -> List[Tuple[float, Dict[str, Any]]]:
        if self._embeddings is None or len(self._payloads) == 0:
            return []
        
        # Cosine similarity
        # items
        A = self._embeddings
        A_norm = np.linalg.norm(A, axis=1) + 1e-8
        
        # query
        q = query_vec / (np.linalg.norm(query_vec) + 1e-8)
        
        sims = (A @ q) / A_norm
        idx = np.argsort(-sims)[:top_k]
        
        return [(float(sims[i]), self._payloads[i]) for i in idx]

    def save(self):
        """Persist to disk"""
        self.path.mkdir(parents=True, exist_ok=True)
        file_path = self.path / f"{self.collection_name}.pkl"
        with open(file_path, "wb") as f:
            pickle.dump({
                "embeddings": self._embeddings,
                "payloads": self._payloads
            }, f)
        print(f"💾 VectorStore saved to {file_path}")

    def load(self):
        """Load from disk"""
        file_path = self.path / f"{self.collection_name}.pkl"
        if file_path.exists():
            with open(file_path, "rb") as f:
                data = pickle.load(f)
                self._embeddings = data["embeddings"]
                self._payloads = data["payloads"]
            print(f"📂 VectorStore loaded from {file_path}")
            return True
        return False
