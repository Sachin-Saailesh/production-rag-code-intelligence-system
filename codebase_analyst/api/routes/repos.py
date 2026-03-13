"""Repositories endpoint to list all historically indexed codebases."""
import json
import logging
import os
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from codebase_analyst.config import settings
from codebase_analyst.core import _components

logger = logging.getLogger(__name__)
router = APIRouter()

class RepoInfo(BaseModel):
    name: str
    files: int
    status: str
    branch: str = "main"

class ReposResponse(BaseModel):
    repos: List[RepoInfo]

@router.get(
    "/repos", 
    response_model=ReposResponse, 
    summary="List Indexed Repositories",
    description="Scan the cache system and return metadata for all repositories that have been locally indexed."
)
async def list_repositories():
    """Returns a list of all indexed repositories."""
    repos = []
    if settings.cache_dir.exists():
        for chunk_file in settings.cache_dir.glob("chunks_*.pkl"):
            try:
                # The stem is 'chunks_owner_repo' or similar. 
                # Our repo_names might contain slashes which were URL-encoded or flattened. 
                # Actually, in core.py, chunks_file = settings.cache_dir / f"chunks_{repo_name}.pkl"
                # If repo_name has a slash, it'll create a nested folder or a literal slash if pathlib allows.
                # Assuming repo_name is just the string after 'chunks_'
                # Wait, Path.stem gives the last component. If its "chunks_tiangolo/fastapi.pkl", that's tricky.
                # Let's cleanly parse it
                chunk_name = str(chunk_file.relative_to(settings.cache_dir))
                if chunk_name.startswith("chunks_") and chunk_name.endswith(".pkl"):
                    repo_name = chunk_name[7:-4]
                else:
                    continue
                
                # Count files from the hashes dictionary
                hash_file = settings.cache_dir / f"hashes_{repo_name}.json"
                files_count = 0
                if hash_file.exists():
                    try:
                        hashes = json.loads(hash_file.read_text())
                        files_count = len(hashes)
                    except json.JSONDecodeError:
                        pass
                
                # Get branch if possible from the actual git clone (data folder)
                branch = "main"
                repo_dir = settings.data_dir / repo_name
                head_file = repo_dir / ".git" / "HEAD"
                if head_file.exists():
                    head_content = head_file.read_text().strip()
                    if head_content.startswith("ref: refs/heads/"):
                        branch = head_content.replace("ref: refs/heads/", "")
                
                repos.append(RepoInfo(
                    name=repo_name,
                    files=files_count,
                    status="synced",
                    branch=branch
                ))
            except Exception as e:
                logger.error("Error parsing cache for repos: %s", e)
                
    return ReposResponse(repos=repos)

@router.delete(
    "/repos/{repo_name:path}", 
    summary="Delete Indexed Repository",
    description="Purge a repository from the vector cache, tracking manifests, and delete the Git clone from the local filesystem."
)
async def delete_repository(repo_name: str):
    """Securely deletes all trace of a repository."""
    
    # 1. Unbind Vector Store from RAM Multi-Tenant Dict
    _components.pop(repo_name, None)
    
    # 2. Scrub Local File Cache Manifests
    chunk_file = settings.cache_dir / f"chunks_{repo_name}.pkl"
    hash_file = settings.cache_dir / f"hashes_{repo_name}.json"
    
    try:
        if chunk_file.exists():
            chunk_file.unlink()
        if hash_file.exists():
            hash_file.unlink()
    except Exception as e:
        logger.warning("Could not delete cache tracking files for %s: %s", repo_name, e)
        
    # 3. Nuke raw code clone
    repo_dir = settings.data_dir / repo_name
    if repo_dir.exists() and repo_dir.is_dir():
        try:
            shutil.rmtree(repo_dir, ignore_errors=True)
        except Exception as e:
            logger.error("Could not delete raw repository clone for %s: %s", repo_name, e)
            
    return {"status": "success", "message": f"Successfully deleted {repo_name}"}
