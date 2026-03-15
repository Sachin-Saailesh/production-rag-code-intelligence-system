"""Health and readiness check endpoints."""
from fastapi import APIRouter
from codebase_analyst.models.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health Diagnostics",
    description="Returns the active connection status of the Redis cache, Qdrant vector database, and Azure OpenAI LLM services."
)
async def health_check():
    """Basic health check."""
    services = {}

    # Check Redis
    try:
        import redis as redis_lib
        from codebase_analyst.config import settings
        r = redis_lib.from_url(settings.redis_url, decode_responses=True)
        r.ping()
        services["redis"] = "healthy"
    except Exception:
        services["redis"] = "unavailable"

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        from codebase_analyst.config import settings
        qc = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        qc.get_collections()
        services["qdrant"] = "healthy"
    except Exception:
        services["qdrant"] = "unavailable"

    services["llm"] = "configured" if settings.openai_api_key else "unconfigured"

    return HealthResponse(status="ok", version="1.0.0", services=services)


@router.get(
    "/ready",
    summary="Container Readiness Check",
    description="Lightweight ping for Kubernetes or Docker swarm readiness probes."
)
async def readiness_check():
    """Readiness check for container orchestration."""
    return {"ready": True}
