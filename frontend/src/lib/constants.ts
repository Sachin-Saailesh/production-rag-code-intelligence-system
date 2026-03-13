import { 
  Server, Box, Settings, Cpu, Database, Network, 
  Search, ShieldCheck, Fingerprint, Activity, LineChart 
} from "lucide-react";

export const PIPELINE_TOOLS = [
  { id: "python", name: "Python 3.10+", category: "Runtime", icon: Server, status: "active", desc: "Core backend runtime powering ingestion, retrieval, orchestration, and analysis workflows." },
  { id: "fastapi", name: "FastAPI", category: "API Layer", icon: Box, status: "active", desc: "API layer for health, ingest, query, readiness, and service orchestration endpoints." },
  { id: "uvicorn", name: "Uvicorn", category: "Server", icon: Settings, status: "active", desc: "ASGI application server running the backend API efficiently in production." },
  { id: "gradio", name: "Gradio", category: "Prototyping", icon: Box, status: "optional", desc: "Existing lightweight interaction surface for quick internal analysis workflows." },
  { id: "openai", name: "OpenAI API", category: "Inference", icon: Cpu, status: "active", desc: "Final answer synthesis and semantic understanding for grounded code intelligence." },
  { id: "cohere", name: "Cohere Rerank", category: "Inference", icon: Search, status: "planned", desc: "Neural reranking stage that improves precision after dense/sparse candidate retrieval." },
  { id: "qdrant", name: "Qdrant", category: "Vector DB", icon: Database, status: "active", desc: "Vector database used to store and search dense semantic representations of code chunks." },
  { id: "bm25", name: "BM25 Search", category: "Algorithm", icon: Search, status: "active", desc: "Keyword/statistical retrieval path that complements semantic vector search." },
  { id: "treesitter", name: "Tree-sitter", category: "Parser", icon: Network, status: "active", desc: "AST-based parsing engine used to extract symbols, structure, imports, and code relationships." },
  { id: "networkx", name: "NetworkX", category: "Analytics", icon: Network, status: "active", desc: "Graph computation layer for dependency tracing, module relationships, and architectural profiling." },
  { id: "redis", name: "Redis", category: "Cache", icon: Database, status: "active", desc: "Semantic caching and fast state access layer to reduce repeat query cost and latency." },
  { id: "prometheus", name: "Prometheus", category: "Telemetry", icon: Activity, status: "active", desc: "Metrics collection system for API latency, retrieval timings, cache metrics, and ingestion telemetry." },
  { id: "grafana", name: "Grafana", category: "Dashboard", icon: LineChart, status: "optional", desc: "Visualization layer for monitoring infrastructure, query health, and platform performance." },
  { id: "opentelemetry", name: "OpenTelemetry", category: "Tracing", icon: Activity, status: "planned", desc: "Distributed tracing for following requests across ingestion, retrieval, and answering pipelines." },
  { id: "docker", name: "Docker", category: "Orchestration", icon: Server, status: "active", desc: "Local and deployment orchestration for the app and supporting context caching services." },
  { id: "sentence-transformers", name: "Sentence-Transformers", category: "Models", icon: Fingerprint, status: "active", desc: "Local embedding alternative mapped for semantic indexing within the codebase chunks." },
  { id: "hybrid-retriever", name: "Hybrid Retriever", category: "Orchestration", icon: ShieldCheck, status: "active", desc: "Internal retrieval strategy combining dense vector search, sparse keyword search, and graph expansion." },
  { id: "semantic-cache", name: "Semantic Cache", category: "Optimizations", icon: Fingerprint, status: "active", desc: "Internal layer for reusing prior grounded responses across matching AST states to save tokens." }
];
