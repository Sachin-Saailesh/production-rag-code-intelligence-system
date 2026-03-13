"""Ingest endpoint — triggers repository indexing."""
import logging
import time
from fastapi import APIRouter, BackgroundTasks
from sse_starlette.sse import EventSourceResponse

from codebase_analyst.models.schemas import IngestRequest, IngestResponse
from codebase_analyst.core import run_ingestion

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/ingest",
    summary="Initialize Context Database via SSE stream",
    description="Ingest and index a new remote Git repository or local directory. Yields progress states Server-Sent Events."
)
async def ingest_repository(request: IngestRequest):
    """
    Ingest and index a repository yielding an EventSourceResponse stream.
    """
    
    async def event_generator():
        try:
            for progress_chunk in run_ingestion(
                repo_url=request.repo_url,
                repo_path=request.repo_path,
                repo_name=request.repo_name,
                force_reindex=request.force_reindex,
            ):
                # sse_starlette expects dictionaries with dict keys `data`, `event`, etc.
                yield {"data": progress_chunk}
        except Exception as e:
            logger.error("Ingestion failed: %s", e, exc_info=True)
            import json
            yield {"data": json.dumps({
                "status": "error",
                "repo_name": request.repo_name or "",
                "message": f"Ingestion failed: {str(e)}",
            })}

    return EventSourceResponse(event_generator())
