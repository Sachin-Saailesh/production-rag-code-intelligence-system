import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
from ..config import config
from .parser import CodeParser

# Language detection constants
EXT_TO_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".jsx": "javascript", ".java": "java", ".go": "go", ".rs": "rust", ".cpp": "cpp",
    ".cxx": "cpp", ".cc": "cpp", ".c": "c", ".h": "c", ".hpp": "cpp", ".cs": "csharp",
    ".rb": "ruby", ".php": "php", ".swift": "swift", ".kt": "kotlin", ".scala": "scala",
    ".sh": "bash", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".json": "json",
    ".md": "markdown", ".txt": "text"
}
CODE_EXTS = set(EXT_TO_LANG.keys())

def guess_language(path: Path) -> str:
    return EXT_TO_LANG.get(path.suffix.lower(), "text")

class RepositoryIngester:
    """Handles cloning, scanning, and parsing of repositories"""
    
    def __init__(self):
        self.parser = CodeParser()
        config.ensure_dirs()

    def clone_repository(self, repo_url: str, repo_dir: Path) -> Path:
        if repo_dir.exists():
            print(f"📁 Repository already present at: {repo_dir}")
            return repo_dir
            
        print(f"⬇️  Cloning {repo_url} → {repo_dir}")
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except Exception as e:
            raise RuntimeError(f"Git clone failed: {e}")
        return repo_dir

    def scan_repository(self, repo_dir: Path) -> List[Path]:
        print("🔎 Scanning repository for code files...")
        code_paths: List[Path] = []
        for root, dirs, files in os.walk(repo_dir):
            if any(sk in root for sk in [".git", ".venv", "node_modules", "dist", "build", "__pycache__"]):
                continue
            for fn in files:
                p = Path(root) / fn
                if p.suffix.lower() in CODE_EXTS:
                    code_paths.append(p)
        print(f"📄 Found {len(code_paths)} code files")
        return code_paths

    def process_files(self, code_files: List[Path]) -> List[Dict[str, Any]]:
        print("🧩 Parsing files...")
        docs = []
        for p in tqdm(code_files, desc="Reading files"):
            parsed = self.parser.parse_file(p)
            if parsed:
                # Use parsed metadata if available, else usage raw content with guesses
                parsed["language"] = parsed.get("language") or guess_language(p)
                docs.append(parsed)
            else:
                 # Fallback for failed parse (e.g. non-code or too large handled by parser returning None)
                 # But valid text files might return None from parser if extension not supported?
                 # Parser supports basic set. guess_language supports more.
                 # If parser returns None, we might want to skip or just read raw.
                 # Let's trust parser for now, or add raw read fallback.
                 pass
                 
        return docs
