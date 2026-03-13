"""Analysis API endpoint for codebase insights."""
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from codebase_analyst.core import get_system_components
from codebase_analyst.analysis.security import SecurityAnalyzer
from codebase_analyst.analysis.architecture import ArchitectureAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/analyze/security",
    summary="Security Audit",
    description="Run static AST vulnerability parsing on a multi-tenant target repo."
)
async def analyze_security(repo_name: str = Query(..., description="Target repository name to analyze")):
    """Runs a full security audit against target repository chunks."""
    try:
        components = get_system_components(repo_name=repo_name)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
        
    chunks = components.get("all_chunks", [])
    if not chunks:
        raise HTTPException(status_code=400, detail="Repository chunks not indexed or unavailable.")
        
    try:
        analyzer = SecurityAnalyzer(chunks=chunks, include_tests=False)
        report = analyzer.scan()
        report["recommendations"] = analyzer.get_recommendations(report.get("findings", []))
        return report
    except Exception as e:
        logger.error(f"Security Analysis failed for {repo_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/analyze/architecture",
    summary="Architecture Topological Profiler",
    description="Calculate design patterns structure against a multi-tenant target repo."
)
async def analyze_architecture(repo_name: str = Query(..., description="Target repository name to analyze")):
    """Runs an architectural summary against target repository chunks."""
    try:
        components = get_system_components(repo_name=repo_name)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
        
    chunks = components.get("all_chunks", [])
    if not chunks:
        raise HTTPException(status_code=400, detail="Repository chunks not indexed or unavailable.")
        
    try:
        analyzer = ArchitectureAnalyzer(chunks=chunks)
        report = analyzer.detect_patterns()
        report["summary"] = analyzer.get_summary()
        return report
    except Exception as e:
        logger.error(f"Architecture Analysis failed for {repo_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
