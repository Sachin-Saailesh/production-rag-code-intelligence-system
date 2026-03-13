"""
CLI command: ask a question about the indexed codebase.
Usage: python -m codebase_analyst.cli.ask "How does authentication work?"
"""
import argparse
import json
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="Ask a question about the indexed codebase")
    parser.add_argument("question", type=str, help="Your question")
    parser.add_argument("--repo-name", type=str, help="Repository to query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    parser.add_argument("--json-output", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    from codebase_analyst.core import get_system_components
    from codebase_analyst.services.retrieval import run_retrieval
    from codebase_analyst.services.answering import generate_answer

    t0 = time.time()
    try:
        components = get_system_components(repo_name=args.repo_name)
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # Retrieve
    retrieval_result = run_retrieval(
        query=args.question,
        hybrid_retriever=components["hybrid_retriever"],
        chunks=components["all_chunks"],
        knowledge_graph=components.get("knowledge_graph"),
        top_k=args.top_k,
    )

    candidates = retrieval_result["candidates"]
    if not candidates:
        print("No relevant code found. Ensure the repository is indexed.")
        sys.exit(0)

    # Generate answer
    answer_result = generate_answer(
        query=args.question,
        candidates=candidates,
        query_type=retrieval_result["query_type"],
    )

    total_ms = (time.time() - t0) * 1000

    if args.json_output:
        output = {
            "question": args.question,
            "answer": answer_result["answer"],
            "query_type": retrieval_result["query_type"],
            "latency_ms": round(total_ms, 2),
            "citations": [
                {"file": c.file_path, "lines": f"{c.start_line}-{c.end_line}"}
                for c in answer_result["citations"]
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*80}")
        print(f"QUESTION: {args.question}")
        print(f"TYPE: {retrieval_result['query_type']}")
        print(f"{'-'*80}")
        print(f"\nANSWER:\n{answer_result['answer']}")
        print(f"\n{'─'*80}")
        print(f"Citations:")
        for c in answer_result["citations"]:
            print(f"  • {c.file_path} (L{c.start_line}-{c.end_line})")
        print(f"\nLatency: {total_ms:.0f}ms")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
