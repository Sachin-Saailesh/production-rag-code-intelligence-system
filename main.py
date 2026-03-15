"""
FastAPI application entry point for the Codebase Analyst.
Serves REST API + Prometheus /metrics + optional Gradio UI mount.
"""
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from codebase_analyst.config import settings
from codebase_analyst.monitoring.metrics import metrics
from codebase_analyst.api.routes import query, ingest, health, repos, analyze

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Starting Codebase Analyst API on %s:%s", settings.host, settings.port)
    settings.ensure_dirs()
    yield
    logger.info("Shutting down Codebase Analyst API")


app = FastAPI(
    title="Codebase Analyst API",
    description="AI-powered codebase analysis with hybrid RAG retrieval",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track HTTP request metrics."""
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start
    metrics.record_http_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        latency=latency,
    )
    return response


# Mount routes
app.include_router(health.router, tags=["health"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(repos.router, prefix="/api", tags=["repos"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])


@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    metrics.update_system_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint for health checks and API discovery."""
    return {
        "status": "online", 
        "message": "Codebase Analyst API is running. Access /docs for API documentation."
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True,
    )
