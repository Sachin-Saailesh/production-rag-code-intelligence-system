import sys
import argparse

try:
    from codebase_analyst.ui import create_ui
    from codebase_analyst.core import reindex_repository, EnhancedCodebaseAnalyst, CodeTools
    from codebase_analyst.retrieval.hybrid import HybridRetriever
    from codebase_analyst.indexing.cache import SemanticCache
except ImportError as e:
    print(f"❌ Error importing dependencies: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


def start_web_ui(share: bool = False):
    print("🚀 Starting Web UI...")
    demo = create_ui()
    demo.launch(share=share)

def run_cli_query(query: str):
    print("🚀 Starting CLI Query...")
    
    print("Loading system components...")
    components = reindex_repository(force_reclone=False)
    
    hybrid_retriever = HybridRetriever(
        vector_store=components['vector_store'],
        sparse_retriever=components['sparse_retriever'],
        embedding_engine=components['embedding_engine']
    )
    
    tools = CodeTools(components['repo_dir'], components['all_chunks'])
    cache = SemanticCache(components['embedding_engine'])
    
    # Use EnhancedCodebaseAnalyst for full features
    analyst = EnhancedCodebaseAnalyst(
        hybrid_retriever, 
        tools, 
        components['all_chunks'],
        cache
    )
    result = analyst.analyze(query)
    
    print("\n" + "="*80)
    print(f"QUESTION: {query}")
    print("-" * 80)
    print(f"ANSWER: {result['answer']}")
    print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Codebase Analyst CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Web UI
    web_parser = subparsers.add_parser("web", help="Start Gradio Web UI")
    web_parser.add_argument("--share", action="store_true", help="Create a public Gradio link")
    
    # CLI Query
    query_parser = subparsers.add_parser("query", help="Run a query against the codebase")
    query_parser.add_argument("text", type=str, help="Question to ask")
    
    args = parser.parse_args()
    
    if args.command == "web":
        start_web_ui(args.share)
    elif args.command == "query":
        run_cli_query(args.text)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
