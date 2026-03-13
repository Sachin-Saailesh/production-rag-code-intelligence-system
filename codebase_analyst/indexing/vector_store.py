"""
Vector store using Qdrant for production, with in-memory fallback for testing.
"""
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from ..config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Qdrant-backed vector store.
    Falls back to in-memory cosine similarity when Qdrant is unavailable.
    """

    def __init__(
        self,
        collection_name: str = None,
        dimension: int = None,
        path: Path = None,
    ):
        self.collection_name = collection_name or settings.qdrant_collection
        self.dimension = dimension or settings.embedding_dim
        self._qdrant_client = None
        self._use_qdrant = False

        # In-memory fallback state
        self._embeddings: Optional[np.ndarray] = None
        self._payloads: List[Dict[str, Any]] = []

        self._try_connect_qdrant()

    def _try_connect_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            if settings.qdrant_api_key:
                self._qdrant_client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                )
            else:
                self._qdrant_client = QdrantClient(url=settings.qdrant_url)

            # Ensure collection exists
            collections = [c.name for c in self._qdrant_client.get_collections().collections]
            if self.collection_name not in collections:
                self._qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("Created Qdrant collection: %s", self.collection_name)

            self._use_qdrant = True
            logger.info("Connected to Qdrant at %s", settings.qdrant_url)
        except Exception as e:
            logger.warning("Qdrant unavailable (%s) — using in-memory vector store", e)
            self._use_qdrant = False

    def add_vectors(
        self,
        embeddings: np.ndarray,
        payloads: List[Dict[str, Any]],
        batch_size: int = 100,
    ):
        if len(payloads) == 0:
            return
        assert embeddings.shape[0] == len(payloads)

        if self._use_qdrant:
            self._add_qdrant(embeddings, payloads, batch_size)
        else:
            self._add_memory(embeddings, payloads)

    def _add_qdrant(self, embeddings: np.ndarray, payloads: List[Dict[str, Any]], batch_size: int):
        from qdrant_client.models import PointStruct

        points = []
        for i, (vec, payload) in enumerate(zip(embeddings, payloads)):
            # Use chunk_id as deterministic integer hash for point ID
            point_id = abs(hash(payload.get("chunk_id", str(i)))) % (2**63)
            points.append(PointStruct(
                id=point_id,
                vector=vec.tolist(),
                payload=payload,
            ))

        for start in range(0, len(points), batch_size):
            batch = points[start : start + batch_size]
            self._qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        logger.info("Upserted %d vectors to Qdrant collection %s", len(points), self.collection_name)

    def _add_memory(self, embeddings: np.ndarray, payloads: List[Dict[str, Any]]):
        if self._embeddings is None:
            self._embeddings = embeddings.astype(np.float32)
        else:
            self._embeddings = np.vstack([self._embeddings, embeddings.astype(np.float32)])
        self._payloads.extend(payloads)

    def search(self, query_vec: np.ndarray, top_k: int = 10) -> List[Tuple[float, Dict[str, Any]]]:
        if self._use_qdrant:
            return self._search_qdrant(query_vec, top_k)
        return self._search_memory(query_vec, top_k)

    def _search_qdrant(self, query_vec: np.ndarray, top_k: int) -> List[Tuple[float, Dict[str, Any]]]:
        response = self._qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_vec.tolist(),
            limit=top_k,
        )
        return [(hit.score, hit.payload) for hit in response.points]

    def _search_memory(self, query_vec: np.ndarray, top_k: int) -> List[Tuple[float, Dict[str, Any]]]:
        if self._embeddings is None or len(self._payloads) == 0:
            return []
        A = self._embeddings
        A_norm = np.linalg.norm(A, axis=1) + 1e-8
        q = query_vec / (np.linalg.norm(query_vec) + 1e-8)
        sims = (A @ q) / A_norm
        idx = np.argsort(-sims)[:top_k]
        return [(float(sims[i]), self._payloads[i]) for i in idx]

    def delete_collection(self):
        if self._use_qdrant:
            try:
                self._qdrant_client.delete_collection(self.collection_name)
                logger.info("Deleted Qdrant collection: %s", self.collection_name)
            except Exception as e:
                logger.warning("Failed to delete collection: %s", e)
        self._embeddings = None
        self._payloads = []

    def count(self) -> int:
        if self._use_qdrant:
            try:
                info = self._qdrant_client.get_collection(self.collection_name)
                return info.points_count
            except Exception:
                return 0
        return len(self._payloads)

    def save(self):
        """Persist in-memory store to disk (only used for in-memory fallback)."""
        if self._use_qdrant:
            return  # Qdrant persists automatically
        import pickle
        path = settings.index_dir
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / f"{self.collection_name}.pkl"
        with open(file_path, "wb") as f:
            pickle.dump({"embeddings": self._embeddings, "payloads": self._payloads}, f)
        logger.info("In-memory VectorStore saved to %s", file_path)

    def load(self) -> bool:
        """Load in-memory store from disk (only used for in-memory fallback)."""
        if self._use_qdrant:
            return True
        import pickle
        file_path = settings.index_dir / f"{self.collection_name}.pkl"
        if file_path.exists():
            with open(file_path, "rb") as f:
                data = pickle.load(f)
                self._embeddings = data["embeddings"]
                self._payloads = data["payloads"]
            logger.info("In-memory VectorStore loaded from %s", file_path)
            return True
        return False
