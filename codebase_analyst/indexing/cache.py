import hashlib
import numpy as np
from typing import Dict, Any, List
from .embedding import EmbeddingEngine

class SemanticCache:
    """Cache LLM responses based on query semantic similarity"""
    
    def __init__(self, embedding_engine: EmbeddingEngine, similarity_threshold: float = 0.95):
        self.embedding_engine = embedding_engine
        self.similarity_threshold = similarity_threshold
        self.cache: Dict[str, Dict[str, Any]] = {} 
        self.keys: List[str] = []

    def _cosine_sim(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-8))

    def get(self, query: str):
        if not self.cache:
            return None

        # Normalize logic
        q_norm = query.strip().lower() # simplified normalization
        
        query_vec = self.embedding_engine.encode([q_norm], show_progress=False)[0]

        best_sim = 0
        best_val = None
        for key, data in self.cache.items():
            sim = self._cosine_sim(query_vec, data["embedding"])
            if sim > best_sim:
                best_sim = sim
                best_val = data["value"]

        if best_sim >= self.similarity_threshold:
            print(f"🧠 Semantic cache HIT (sim={best_sim:.3f})")
            return best_val
        return None

    def set(self, query: str, value: Any):
        q_norm = query.strip().lower()
        query_vec = self.embedding_engine.encode([q_norm], show_progress=False)[0]
        hashed_key = hashlib.md5(q_norm.encode()).hexdigest()
        
        self.cache[hashed_key] = {"embedding": query_vec, "value": value}
        self.keys.append(hashed_key)
