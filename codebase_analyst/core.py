"""
Enhanced Codebase Analyst with advanced analysis capabilities.
Adds multi-hop reasoning, query expansion, and comprehensive analysis.
"""
import time
import pickle
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from .config import config
from .llm.provider import llm_engine
from .ingestion.processor import RepositoryIngester
from .ingestion.chunker import CodeChunker
from .indexing.embedding import EmbeddingEngine
from .indexing.vector_store import VectorStore
from .indexing.cache import SemanticCache
from .retrieval.sparse import SparseRetriever
from .retrieval.hybrid import HybridRetriever
from .caching.manager import CacheManager
from .monitoring.metrics import metrics
from .analysis.knowledge_graph import CodeKnowledgeGraph, ImpactAnalyzer
from .analysis.architecture import ArchitectureAnalyzer
from .analysis.security import SecurityAnalyzer
from .evaluation.rag_evaluator import RAGEvaluator
from .utils.exporter import ResultExporter

# ---------------------------
# Code Tools
# ---------------------------
class CodeTools:
    def __init__(self, repo_dir: Path, chunks: List[Dict[str, Any]]):
        self.repo_dir = Path(repo_dir)
        self.chunks = chunks

    def open_file(self, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        p = Path(file_path)
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            if start_line or end_line:
                lines = text.splitlines()
                s = (start_line or 1) - 1
                e = end_line or len(lines)
                return "\n".join(lines[s:e])
            return text
        except Exception as e:
            return f"Error reading file {file_path}: {e}"

    def grep_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        hits = []
        for ch in self.chunks:
            if symbol in ch["content"]:
                hits.append(ch)
        return hits

# ---------------------------
# Base Codebase Analyst
# ---------------------------
class CodebaseAnalyst:
    def __init__(self, hybrid_retriever: HybridRetriever,
                 code_tools: CodeTools,
                 cache_manager: SemanticCache = None, 
                 monitor=None):
        self.retriever = hybrid_retriever
        self.llm = llm_engine
        self.tools = code_tools
        self.cache = cache_manager
        self.monitor = monitor

    def _run(self, question: str, top_k: int = 8) -> Dict[str, Any]:
        t0 = time.time()
        
        # Check cache
        if self.cache:
            cached = self.cache.get(question)
            if cached:
                metrics.record_cache_hit() if metrics else None
                return cached
        
        metrics.record_cache_miss() if metrics else None

        # Retrieve
        ret_t0 = time.time()
        hits = self.retriever.search(question, top_k=top_k)
        ret_latency = time.time() - ret_t0
        metrics.record_retrieval(ret_latency, len(hits)) if metrics else None
        
        # Format context
        context = []
        for h in hits:
            context.append({
                "payload": {
                    "chunk_id": h["chunk_id"],
                    "file_path": h["file_path"],
                    "language": h["language"],
                    "content": h["content"],
                    "start_line": h["start_line"],
                    "end_line": h["end_line"],
                },
                "score": h.get("score", 0.0)
            })

        # LLM Generation
        llm_t0 = time.time()
        
        context_str = "\n\n".join([
            f"File: {c['payload']['file_path']} (Lines {c['payload']['start_line']}-{c['payload']['end_line']})\n```\n{c['payload']['content']}\n```"
            for c in context
        ])
        
        sys_msg = "You are a helpful codebase expert. Answer the user question based on the code below."
        usr_msg = f"Question: {question}\n\nContext:\n{context_str}"
        
        llm_response = self.llm.chat([
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": usr_msg}
        ])
        
        llm_latency = time.time() - llm_t0
        metrics.record_llm_latency(llm_latency) if metrics else None
        
        t1 = time.time()
        total_latency = t1 - t0
        metrics.record_query_latency(total_latency) if metrics else None
        metrics.record_query('success') if metrics else None

        result = {
            "answer": llm_response,
            "content": llm_response,
            "tool_calls": None,
            "tokens_used": 0,
            "latency": float(total_latency),
            "llm_latency": float(llm_latency),
            "context": context
        }
        
        # Cache result
        if self.cache:
            self.cache.set(question, result)
            
        return result

    def analyze(self, query: str, top_k: int = 8) -> Dict[str, Any]:
        return self._run(query, top_k=top_k)

# ---------------------------
# Enhanced Analyst with Advanced Features
# ---------------------------
class EnhancedCodebaseAnalyst(CodebaseAnalyst):
    """Extended analyst with knowledge graph, architecture, and security analysis"""
    
    def __init__(self, hybrid_retriever: HybridRetriever,
                 code_tools: CodeTools,
                 chunks: List[Dict[str, Any]],
                 cache_manager: SemanticCache = None,
                 monitor=None):
        super().__init__(hybrid_retriever, code_tools, cache_manager, monitor)
        
        # Build advanced analyzers
        self.knowledge_graph = CodeKnowledgeGraph()
        self.knowledge_graph.build_from_chunks(chunks)
        self.impact_analyzer = ImpactAnalyzer(self.knowledge_graph)
        self.arch_analyzer = ArchitectureAnalyzer(chunks)
        self.security_analyzer = SecurityAnalyzer(chunks)
    
    def analyze_with_expansion(self, query: str, expand: bool = True, top_k: int = 8) -> Dict[str, Any]:
        """Analyze with query expansion"""
        if expand:
            # Simple expansion: add related terms
            expanded_query = f"{query} (implementation details usage examples)"
            result = self._run(expanded_query, top_k=top_k*2)
            result['query_expanded'] = True
        else:
            result = self._run(query, top_k=top_k)
            result['query_expanded'] = False
        
        return result
    
    def analyze_impact(self, file_path: str) -> Dict[str, Any]:
        """Analyze impact of changes to a specific file"""
        return self.impact_analyzer.analyze_file_impact(file_path)
    
    def show_architecture(self) -> Dict[str, Any]:
        """Get architecture analysis"""
        return self.arch_analyzer.detect_patterns()
    
    def security_scan(self) -> Dict[str, Any]:
        """Run security vulnerability scan"""
        return self.security_analyzer.scan()
    
    def export_result(self, query: str, result: Dict[str, Any], format: str = 'markdown') -> Path:
        """Export result to file"""
        exporter = ResultExporter()
        
        if format == 'markdown':
            return exporter.export_to_markdown(
                query=query,
                answer=result['answer'],
                contexts=result['context'],
                metadata={'latency': result['latency']}
            )
        elif format == 'html':
            return exporter.export_to_html(
                query=query,
                answer=result['answer'],
                contexts=result['context'],
                metadata={'latency': result['latency']}
            )
        elif format == 'json':
            return exporter.export_to_json(result, 'query_result')
        else:
            raise ValueError(f"Unsupported format: {format}")

# ---------------------------
# Reindexing Logic
# ---------------------------
def reindex_repository(force_reclone: bool = False):
    """
    Reindex the repository defined in config.
    Returns dictionary with components needed to instantiate Analyst.
    """
    print("\n" + "="*80)
    print(f"REINDEXING REPOSITORY: {config.repo_name}")
    print("="*80 + "\n")

    config.ensure_dirs()
    
    # 1. Ingestion
    ingester = RepositoryIngester()
    repo_dir = config.data_dir / config.repo_name
    
    if force_reclone and repo_dir.exists():
        print(f"🗑️  Removing existing repository at {repo_dir}")
        shutil.rmtree(repo_dir)
        
    repo_dir = ingester.clone_repository(config.repo_url, repo_dir)
    code_files = ingester.scan_repository(repo_dir)
    parsed_docs = ingester.process_files(code_files)
    
    # Chunking
    chunker = CodeChunker()
    all_chunks = []
    for doc in tqdm(parsed_docs, desc="Chunking documents"):
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)
    print(f"✅ Created {len(all_chunks)} chunks from {len(parsed_docs)} files")
    
    # Cache chunks to disk
    with open(config.cache_dir / f"chunks_{config.repo_name}.pkl", "wb") as f:
        pickle.dump(all_chunks, f)

    # 2. Indexing
    embedding_engine = EmbeddingEngine()
    print("\n📊 Generating embeddings...")
    
    chunk_texts = [f"{c['file_path']}\n{c['content']}" for c in all_chunks]
    embeddings = embedding_engine.encode(
        chunk_texts,
        batch_size=config.batch_size,
        show_progress=True
    )
    
    vector_store = VectorStore(
        collection_name=f"codebase_{config.repo_name}",
        dimension=embedding_engine.dimension,
        path=config.index_dir
    )
    
    payloads = [
        {
            'chunk_id': c['chunk_id'],
            'file_path': c['file_path'],
            'language': c['language'],
            'content': c['content'],
            'start_line': c['start_line'],
            'end_line': c['end_line'],
        } for c in all_chunks
    ]
    vector_store.add_vectors(embeddings, payloads)
    vector_store.save()

    # 3. Sparse Indexing
    sparse_retriever = SparseRetriever()
    sparse_retriever.index(all_chunks)

    print("\n✅ Reindexing complete!")
    
    return {
        'repo_dir': repo_dir,
        'all_chunks': all_chunks,
        'embedding_engine': embedding_engine,
        'vector_store': vector_store,
        'sparse_retriever': sparse_retriever
    }
