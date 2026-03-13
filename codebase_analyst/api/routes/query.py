"""Query endpoint — the main RAG pipeline entrypoint."""
import logging
import time
from fastapi import APIRouter, HTTPException

from codebase_analyst.models.schemas import QueryRequest, QueryResponse
from codebase_analyst.services.cache import SemanticCache
from codebase_analyst.services.retrieval import run_retrieval
from codebase_analyst.services.answering import generate_answer
from codebase_analyst.monitoring.metrics import metrics
from codebase_analyst.core import get_system_components

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Execute Semantic Investigation",
    description="Query the indexed codebase using Hybrid RAG (Dense Vector + BM25 Sparse Search + Graph Context). Returns an AI-generated answer with exact file and line number citations."
)
async def query_codebase(request: QueryRequest):
    """
    Run a full RAG query against the indexed codebase.
    Retrieves context, reranks, generates grounded answer with citations.
    """
    t0 = time.time()

    try:
        components = get_system_components(repo_name=request.repo_name)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    cache = SemanticCache()

    # Check cache
    cached = cache.get(
        request.query,
        repo_name=components.get("repo_name", ""),
        index_version=components.get("commit_sha", ""),
    )
    if cached:
        total_ms = (time.time() - t0) * 1000
        metrics.record_query("cache_hit")
        return QueryResponse(
            answer=cached.get("answer", ""),
            citations=cached.get("citations", []),
            query_type=cached.get("query_type", "general"),
            latency_ms=total_ms,
            cache_hit=True,
            metadata={"source": "cache"},
        )

    # Run retrieval pipeline
    retrieval_result = run_retrieval(
        query=request.query,
        hybrid_retriever=components["hybrid_retriever"],
        chunks=components["all_chunks"],
        knowledge_graph=components.get("knowledge_graph"),
        top_k=request.top_k,
    )

    candidates = retrieval_result["candidates"]

    if not candidates:
        return QueryResponse(
            answer="No relevant code was found for your question. Please try rephrasing or ensure the codebase is indexed.",
            query_type=retrieval_result["query_type"],
            latency_ms=(time.time() - t0) * 1000,
            chunks_retrieved=0,
        )

    # Generate grounded answer
    answer_result = generate_answer(
        query=request.query,
        candidates=candidates,
        query_type=retrieval_result["query_type"],
    )

    total_ms = (time.time() - t0) * 1000
    metrics.record_query("success")
    metrics.record_query_latency(total_ms / 1000)

    response = QueryResponse(
        answer=answer_result["answer"],
        citations=answer_result["citations"],
        query_type=retrieval_result["query_type"],
        latency_ms=total_ms,
        llm_latency_ms=answer_result["llm_latency_ms"],
        retrieval_latency_ms=retrieval_result["retrieval_latency_ms"],
        rerank_latency_ms=retrieval_result["rerank_latency_ms"],
        cache_hit=False,
        chunks_retrieved=len(candidates),
    )

    # Cache the result
    cache.set(
        request.query,
        {"answer": response.answer, "citations": [c.model_dump() for c in response.citations], "query_type": response.query_type},
        repo_name=components.get("repo_name", ""),
        index_version=components.get("commit_sha", ""),
    )

    return response
