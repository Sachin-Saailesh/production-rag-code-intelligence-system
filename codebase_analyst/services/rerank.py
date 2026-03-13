"""
Cohere Rerank service.
Sends retrieved candidates to the Cohere Rerank API and returns re-scored results.
Degrades gracefully if disabled or if the API key is missing.
"""
import logging
import time
from typing import List, Dict, Any

from ..config import settings
from ..monitoring.metrics import metrics

logger = logging.getLogger(__name__)

_cohere_client = None


def _get_cohere_client():
    global _cohere_client
    if _cohere_client is None:
        if not settings.cohere_api_key:
            return None
        try:
            import cohere
            _cohere_client = cohere.Client(api_key=settings.cohere_api_key)
        except ImportError:
            logger.warning("cohere package not installed — reranking disabled")
            return None
    return _cohere_client


def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = None,
) -> List[Dict[str, Any]]:
    """
    Rerank candidates using Cohere Rerank API.

    Falls back to returning candidates as-is if:
    - reranking is disabled via config
    - COHERE_API_KEY is not set
    - cohere library is missing
    """
    top_k = top_k or settings.top_k_rerank

    if not settings.rerank_enabled:
        logger.debug("Reranking disabled via config")
        return candidates[:top_k]

    client = _get_cohere_client()
    if client is None:
        logger.debug("Cohere client unavailable — skipping rerank")
        return candidates[:top_k]

    documents = [c.get("content", "") for c in candidates]
    if not documents:
        return []

    t0 = time.time()
    try:
        response = client.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=documents,
            top_n=top_k,
        )
        latency = time.time() - t0
        metrics.record_rerank_latency(latency)

        reranked = []
        for result in response.results:
            candidate = candidates[result.index].copy()
            candidate["rerank_score"] = result.relevance_score
            candidate["score"] = result.relevance_score
            reranked.append(candidate)

        logger.info("Reranked %d → %d candidates in %.3fs", len(candidates), len(reranked), latency)
        return reranked

    except Exception as e:
        logger.error("Cohere rerank failed: %s — falling back to original order", e)
        return candidates[:top_k]
