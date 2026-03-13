"""
CLI command: ingest a repository.
Usage: python -m codebase_analyst.cli.ingest --repo-url <url>
       python -m codebase_analyst.cli.ingest --repo-path /local/path
"""
import argparse
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="Ingest and index a code repository")
    parser.add_argument("--repo-url", type=str, help="Git URL to clone and ingest")
    parser.add_argument("--repo-path", type=str, help="Local path to ingest")
    parser.add_argument("--repo-name", type=str, help="Repository identifier")
    parser.add_argument("--force", action="store_true", help="Force full re-index")
    args = parser.parse_args()

    if not args.repo_url and not args.repo_path:
        print("Using default repository from settings...")

    from codebase_analyst.core import run_ingestion

    t0 = time.time()
    try:
        result = run_ingestion(
            repo_url=args.repo_url,
            repo_path=args.repo_path,
            repo_name=args.repo_name,
            force_reindex=args.force,
        )
        elapsed = time.time() - t0
        print(f"\n{'='*60}")
        print(f"✅ Ingestion Complete")
        print(f"   Repository: {result['repo_name']}")
        print(f"   Files processed: {result['files_processed']}")
        print(f"   Chunks created: {result['chunks_created']}")
        print(f"   Files skipped (unchanged): {result['files_skipped']}")
        print(f"   Duration: {elapsed:.1f}s")
        print(f"{'='*60}")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
