"""
Grounded answer generation service.
Uses OpenAI to synthesize an answer from retrieved context, with citations.
"""
import logging
import time
from typing import List, Dict, Any

from ..config import settings
from ..llm.provider import get_llm_engine
from ..models.schemas import Citation
from ..monitoring.metrics import metrics

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert codebase analyst and senior software architect.
Answer the user's question based ONLY on the provided code context.

Rules:
1. Ground your answer in the retrieved code snippets. Cite file paths and line ranges.
2. If the context is insufficient to answer confidently, explicitly say so.
3. Use code blocks when quoting code.
4. Be concise but thorough.
5. At the end of your answer, list cited files in a "References" section."""


def build_context_prompt(candidates: List[Dict[str, Any]]) -> str:
    """Format retrieved candidates into a context string for the LLM."""
    parts = []
    for i, c in enumerate(candidates, 1):
        fp = c.get("file_path", "unknown")
        sl = c.get("start_line", 0)
        el = c.get("end_line", 0)
        lang = c.get("language", "")
        content = c.get("content", "")
        parts.append(
            f"[Context {i}] File: {fp} (Lines {sl}-{el})\n```{lang}\n{content}\n```"
        )
    return "\n\n".join(parts)


def generate_answer(
    query: str,
    candidates: List[Dict[str, Any]],
    query_type: str = "general",
) -> Dict[str, Any]:
    """
    Generate a grounded answer from retrieved candidates.

    Returns:
        dict with: answer, citations, llm_latency_ms
    """
    llm = get_llm_engine()
    context_str = build_context_prompt(candidates)

    user_message = f"Question: {query}\n\nRetrieved Code Context:\n{context_str}"

    t0 = time.time()
    answer = llm.chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])
    llm_latency = time.time() - t0
    metrics.record_llm_latency(llm_latency)

    # Build citation objects from candidates
    citations = []
    for c in candidates:
        citations.append(Citation(
            file_path=c.get("file_path", ""),
            start_line=c.get("start_line", 0),
            end_line=c.get("end_line", 0),
            language=c.get("language", ""),
            snippet=c.get("content", "")[:200],
            score=c.get("score", 0.0),
        ))

    return {
        "answer": answer,
        "citations": citations,
        "llm_latency_ms": llm_latency * 1000,
    }
