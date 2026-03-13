"""
Repository ingestion: cloning, scanning, and file processing.
Supports incremental re-indexing via content hashing.
"""
import hashlib
import logging
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from tqdm import tqdm

from ..config import settings
from .parser import CodeParser

logger = logging.getLogger(__name__)

# Language detection by extension
EXT_TO_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".jsx": "javascript", ".java": "java", ".go": "go", ".rs": "rust", ".cpp": "cpp",
    ".cxx": "cpp", ".cc": "cpp", ".c": "c", ".h": "c", ".hpp": "cpp", ".cs": "csharp",
    ".rb": "ruby", ".php": "php", ".swift": "swift", ".kt": "kotlin", ".scala": "scala",
    ".sh": "bash", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".json": "json",
    ".md": "markdown", ".txt": "text",
}
CODE_EXTS = set(EXT_TO_LANG.keys())

# Directories to always skip
SKIP_DIRS: Set[str] = {
    ".git", ".svn", ".hg", ".venv", "venv", "env", "__pycache__",
    "node_modules", "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
    ".eggs", "*.egg-info", ".cache", ".gradle", "target", "bin", "obj",
    ".idea", ".vscode", ".DS_Store",
}

# Binary / non-code extensions to skip
SKIP_EXTS: Set[str] = {
    ".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe", ".o", ".a",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".bmp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".woff", ".woff2", ".ttf", ".eot",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".lock", ".min.js", ".min.css",
}


def guess_language(path: Path) -> str:
    return EXT_TO_LANG.get(path.suffix.lower(), "text")


def file_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_git_info(repo_dir: Path) -> Dict[str, str]:
    """Extract branch and commit SHA from a git repo."""
    info = {"branch": "", "commit_sha": ""}
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir), capture_output=True, text=True
        )
        if result.returncode == 0:
            info["commit_sha"] = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(repo_dir), capture_output=True, text=True
        )
        if result.returncode == 0:
            info["branch"] = result.stdout.strip()
    except Exception:
        pass
    return info


class RepositoryIngester:
    """Handles cloning, scanning, and parsing of repositories."""

    def __init__(self):
        self.parser = CodeParser()
        self._hash_cache: Dict[str, str] = {}  # file_path -> content_hash
        settings.ensure_dirs()

    def clone_repository(self, repo_url: str, repo_dir: Path) -> Path:
        if repo_dir.exists():
            logger.info("Repository already present at: %s", repo_dir)
            return repo_dir

        logger.info("Cloning %s → %s", repo_url, repo_dir)
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        except Exception as e:
            raise RuntimeError(f"Git clone failed: {e}")
        return repo_dir

    def scan_repository(self, repo_dir: Path) -> List[Path]:
        """Scan for code files, skipping junk directories and binary files."""
        logger.info("Scanning repository for code files...")
        code_paths: List[Path] = []
        for root, dirs, files in os.walk(repo_dir):
            # Filter out skip directories in-place
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            root_path = Path(root)
            for fn in files:
                p = root_path / fn
                if p.suffix.lower() in SKIP_EXTS:
                    continue
                if p.suffix.lower() in CODE_EXTS:
                    try:
                        if p.stat().st_size <= settings.max_file_size:
                            code_paths.append(p)
                    except OSError:
                        continue

        logger.info("Found %d code files", len(code_paths))
        return code_paths

    def process_files(
        self,
        code_files: List[Path],
        previous_hashes: Optional[Dict[str, str]] = None,
    ) -> tuple:
        """
        Parse files and return parsed docs.
        Returns (parsed_docs, new_hashes, skipped_count).
        """
        logger.info("Parsing %d files...", len(code_files))
        docs = []
        new_hashes: Dict[str, str] = {}
        skipped = 0

        for p in tqdm(code_files, desc="Reading files"):
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            content_hash = file_content_hash(content)
            fp_str = str(p)
            new_hashes[fp_str] = content_hash

            # Skip unchanged files
            if previous_hashes and previous_hashes.get(fp_str) == content_hash:
                skipped += 1
                continue

            parsed = self.parser.parse_file(p)
            if parsed:
                parsed["language"] = parsed.get("language") or guess_language(p)
                parsed["content_hash"] = content_hash
                docs.append(parsed)

        logger.info("Parsed %d files, skipped %d unchanged", len(docs), skipped)
        return docs, new_hashes, skipped
