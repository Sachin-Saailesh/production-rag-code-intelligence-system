from typing import List, Dict, Any
from ..indexing.vector_store import VectorStore
from ..indexing.embedding import EmbeddingEngine
from .sparse import SparseRetriever

class HybridRetriever:
    """Combines Dense (Vector) and Sparse (TF-IDF) retrieval"""
    
    def __init__(self, vector_store: VectorStore, sparse_retriever: SparseRetriever,
                 embedding_engine: EmbeddingEngine, dense_weight: float = 0.5):
        self.vector_store = vector_store
        self.sparse = sparse_retriever
        self.embedding_engine = embedding_engine
        self.dense_weight = dense_weight

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        # Dense
        qvec = self.embedding_engine.encode([query], batch_size=1, show_progress=False)[0]
        dense_hits = self.vector_store.search(qvec, top_k=top_k*3)
        
        # Sparse
        sparse_hits = self.sparse.search(query, top_k=top_k*3)

        # Score fusion (Reciprocal Rank Fusion or simple normalization)
        # Using simple MinMax normalization as per original notebook
        def normalize(scores):
            if not scores: return []
            vals = [s for s,_ in scores]
            mn, mx = min(vals), max(vals)
            if mx - mn < 1e-8:
                return [(0.5, p) for s,p in scores]
            return [((s - mn) / (mx - mn), p) for s,p in scores]

        dense_n = normalize(dense_hits)
        sparse_n = normalize(sparse_hits)

        # Index by chunk_id
        score_map = {}
        payload_map = {}

        for s, p in dense_n:
            cid = p["chunk_id"]
            score_map[cid] = score_map.get(cid, 0.0) + self.dense_weight * s
            payload_map[cid] = p
            
        for s, p in sparse_n:
            cid = p["chunk_id"]
            score_map[cid] = score_map.get(cid, 0.0) + (1 - self.dense_weight) * s
            payload_map[cid] = p

        fused = sorted(score_map.items(), key=lambda x: -x[1])[:top_k]
        
        out = []
        for cid, sc in fused:
            p = payload_map[cid]
            # Helper to safely copy
            item = p.copy()
            item["score"] = float(sc)
            out.append(item)
            
        return out
