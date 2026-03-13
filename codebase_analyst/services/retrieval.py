"""
Full retrieval pipeline orchestrator.
classify → dense → sparse → symbol match → graph expand → fuse → rerank → assemble context.
"""
import logging
import re
import time
from typing import List, Dict, Any, Optional

from ..config import settings
from ..monitoring.metrics import metrics

logger = logging.getLogger(__name__)

# Query type constants
QT_SYMBOL = "symbol_lookup"
QT_SEMANTIC = "semantic"
QT_ARCHITECTURE = "architecture"
QT_DEPENDENCY = "dependency"
QT_CONFIG = "config"


def classify_query(query: str) -> Dict[str, Any]:
    """
    Lightweight query classification based on pattern matching.
    Returns query_type and extracted symbols.
    """
    q = query.lower().strip()
    symbols = re.findall(r'\b([A-Z][a-zA-Z0-9_]+|[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)\b', query)

    # Architecture patterns
    arch_keywords = ["architecture", "structure", "design pattern", "overview", "how is ", "organized"]
    if any(k in q for k in arch_keywords):
        return {"query_type": QT_ARCHITECTURE, "symbols": symbols}

    # Dependency patterns
    dep_keywords = ["depend", "import", "uses", "calls", "requires", "connected to"]
    if any(k in q for k in dep_keywords):
        return {"query_type": QT_DEPENDENCY, "symbols": symbols}

    # Config patterns
    config_keywords = ["config", "setting", "environment", "secret", "variable", ".env"]
    if any(k in q for k in config_keywords):
        return {"query_type": QT_CONFIG, "symbols": symbols}

    # Symbol lookup patterns
    symbol_patterns = [
        r'\bwhat (?:is|does)\s+\w+',
        r'\bfind\s+(?:function|class|method)\b',
        r'\bwhere\s+is\s+\w+\s+defined\b',
        r'\bshow\s+(?:me\s+)?(?:the\s+)?(?:function|class|method)\b',
    ]
    for pat in symbol_patterns:
        if re.search(pat, q):
            return {"query_type": QT_SYMBOL, "symbols": symbols}

    return {"query_type": QT_SEMANTIC, "symbols": symbols}


def symbol_search(
    query: str,
    symbols: List[str],
    chunks: List[Dict[str, Any]],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Exact symbol match against chunk content and metadata."""
    results = []
    for chunk in chunks:
        content_lower = chunk.get("content", "").lower()
        for sym in symbols:
            if sym.lower() in content_lower:
                hit = chunk.copy()
                hit["score"] = 1.0
                hit["source"] = "symbol"
                results.append(hit)
                break
    # Deduplicate and limit
    seen = set()
    unique = []
    for r in results:
        cid = r.get("chunk_id", id(r))
        if cid not in seen:
            seen.add(cid)
            unique.append(r)
    return unique[:top_k]


def fuse_candidates(
    dense: List[Dict[str, Any]],
    sparse: List[Dict[str, Any]],
    symbol: List[Dict[str, Any]],
    dense_weight: float = None,
) -> List[Dict[str, Any]]:
    """Fuse candidates from multiple retrieval sources using weighted scoring."""
    dw = dense_weight or settings.dense_weight
    sw = 1.0 - dw

    def _normalize(hits):
        if not hits:
            return []
        scores = [h.get("score", 0.0) for h in hits]
        mn, mx = min(scores), max(scores)
        rng = mx - mn if mx - mn > 1e-8 else 1.0
        return [((h.get("score", 0.0) - mn) / rng, h) for h in hits]

    score_map: Dict[str, float] = {}
    payload_map: Dict[str, Dict[str, Any]] = {}

    for norm_score, hit in _normalize(dense):
        cid = hit.get("chunk_id", "")
        score_map[cid] = score_map.get(cid, 0.0) + dw * norm_score
        payload_map[cid] = hit

    for norm_score, hit in _normalize(sparse):
        cid = hit.get("chunk_id", "")
        score_map[cid] = score_map.get(cid, 0.0) + sw * norm_score
        if cid not in payload_map:
            payload_map[cid] = hit

    # Symbol matches get a bonus
    for hit in symbol:
        cid = hit.get("chunk_id", "")
        score_map[cid] = score_map.get(cid, 0.0) + 0.3
        if cid not in payload_map:
            payload_map[cid] = hit

    ranked = sorted(score_map.items(), key=lambda x: -x[1])
    fused = []
    for cid, score in ranked:
        entry = payload_map[cid].copy()
        entry["score"] = float(score)
        fused.append(entry)
    return fused


def run_retrieval(
    query: str,
    hybrid_retriever,
    chunks: List[Dict[str, Any]],
    knowledge_graph=None,
    top_k: int = None,
) -> Dict[str, Any]:
    """
    Full retrieval pipeline:
    1. Classify query
    2. Dense + sparse via hybrid retriever
    3. Symbol search
    4. Graph expansion (if available)
    5. Fuse candidates
    6. Rerank with Cohere
    7. Return final candidates + metadata
    """
    from .rerank import rerank

    top_k = top_k or settings.top_k_rerank
    t0 = time.time()

    # 1. Classify
    classification = classify_query(query)
    query_type = classification["query_type"]
    symbols = classification["symbols"]

    # 2. Hybrid retrieval (dense + sparse)
    ret_t0 = time.time()
    hybrid_results = hybrid_retriever.search(query, top_k=top_k * 3)
    retrieval_latency = time.time() - ret_t0
    metrics.record_retrieval(retrieval_latency, len(hybrid_results))

    # 3. Symbol search
    symbol_results = []
    if symbols and query_type == QT_SYMBOL:
        symbol_results = symbol_search(query, symbols, chunks, top_k=top_k)

    # 4. Graph expansion
    graph_results = []
    if knowledge_graph and query_type in (QT_DEPENDENCY, QT_ARCHITECTURE):
        try:
            for hit in hybrid_results[:3]:
                fp = hit.get("file_path", "")
                deps = knowledge_graph.get_dependencies(fp)
                for dep_path in deps[:2]:
                    for ch in chunks:
                        if ch.get("file_path") == dep_path:
                            entry = ch.copy()
                            entry["score"] = 0.2
                            entry["source"] = "graph"
                            graph_results.append(entry)
                            break
        except Exception as e:
            logger.debug("Graph expansion error: %s", e)

    # 5. Fuse
    all_sparse = [h for h in hybrid_results if h.get("source") == "sparse"]
    all_dense = [h for h in hybrid_results if h.get("source") != "sparse"]
    if not all_sparse and not all_dense:
        all_dense = hybrid_results

    fused = fuse_candidates(all_dense, all_sparse, symbol_results + graph_results)

    # 6. Rerank
    rerank_t0 = time.time()
    reranked = rerank(query, fused, top_k=top_k)
    rerank_latency = time.time() - rerank_t0

    total_latency = time.time() - t0

    return {
        "candidates": reranked,
        "query_type": query_type,
        "classification": classification,
        "retrieval_latency_ms": retrieval_latency * 1000,
        "rerank_latency_ms": rerank_latency * 1000,
        "total_latency_ms": total_latency * 1000,
    }
