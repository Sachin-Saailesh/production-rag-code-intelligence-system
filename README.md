# Production RAG Code Intelligence System

AI-powered codebase analysis platform with hybrid RAG retrieval, reranking, and grounded answering.

## Architecture

```
┌─────────────┐     ┌────────────────┐     ┌──────────────┐
│  FastAPI     │────▶│  Retrieval     │────▶│  Qdrant      │
│  /api/query  │     │  Pipeline      │     │  (vectors)   │
│  /api/ingest │     │  classify →    │     └──────────────┘
│  /health     │     │  dense+sparse  │     ┌──────────────┐
│  /metrics    │     │  → fuse →      │────▶│  Redis       │
└─────────────┘     │  rerank(Cohere)│     │  (cache)     │
                    │  → answer(LLM) │     └──────────────┘
                    └────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   ┌──────────┐   ┌────────────┐   ┌──────────────┐
   │ Prometheus│   │  Grafana   │   │  OpenAI /    │
   │ /metrics  │   │  Dashboard │   │  Azure LLM   │
   └──────────┘   └────────────┘   └──────────────┘
```

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env with your API keys:
#   OPENAI_API_KEY=sk-...
#   COHERE_API_KEY=...  (optional, for reranking)
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
# Start the API server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --port 8000
```

### 4. Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts all 5 services:
| Service    | Port  | Description            |
|------------|-------|------------------------|
| **app**    | 8000  | FastAPI API server     |
| **qdrant** | 6333  | Vector database        |
| **redis**  | 6379  | Semantic cache         |
| **prometheus** | 9090 | Metrics collection  |
| **grafana**| 3000  | Monitoring dashboards  |

## CLI Usage

### Ingest a Repository
```bash
# From Git URL
python -m codebase_analyst.cli.ingest --repo-url https://github.com/owner/repo.git --repo-name myrepo

# From local path
python -m codebase_analyst.cli.ingest --repo-path /path/to/code --repo-name myrepo

# Force full re-index
python -m codebase_analyst.cli.ingest --repo-url https://github.com/owner/repo.git --force
```

### Ask Questions
```bash
python -m codebase_analyst.cli.ask "How does authentication work?" --repo-name myrepo
python -m codebase_analyst.cli.ask "Where is UserModel defined?" --top-k 3
python -m codebase_analyst.cli.ask "What are the dependencies of main.py?" --json-output
```

## API Endpoints

### `POST /api/ingest`
```json
{
  "repo_url": "https://github.com/owner/repo.git",
  "repo_name": "myrepo",
  "force_reindex": false
}
```

### `POST /api/query`
```json
{
  "query": "How does error handling work?",
  "repo_name": "myrepo",
  "top_k": 5
}
```

**Response includes:**
- Grounded answer with code citations
- Query type classification (symbol_lookup, semantic, architecture, dependency, config)
- Latency breakdown (retrieval, rerank, LLM)
- Cache hit status

### `GET /health`
Returns service status for Qdrant, Redis, and LLM configuration.

### `GET /metrics`
Prometheus metrics endpoint.

## Configuration

All settings are loaded from environment variables or a `.env` file. See [.env.example](.env.example) for all options.

Key settings:
| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required for LLM |
| `COHERE_API_KEY` | — | Optional, enables reranking |
| `LLM_PROVIDER` | `openai` | `openai` or `azure` |
| `QDRANT_URL` | `http://localhost:6333` | Vector DB endpoint |
| `REDIS_URL` | `redis://localhost:6379/0` | Cache endpoint |
| `RERANK_ENABLED` | `true` | Toggle Cohere reranking |
| `DENSE_WEIGHT` | `0.6` | Dense vs sparse balance |

## Project Structure

```
├── main.py                         # FastAPI application entry point
├── docker-compose.yml              # Full stack deployment
├── Dockerfile                      # Application container
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── codebase_analyst/
│   ├── config.py                   # Pydantic Settings (from .env)
│   ├── core.py                     # System orchestrator
│   ├── api/routes/                 # FastAPI endpoints
│   │   ├── query.py                # POST /api/query
│   │   ├── ingest.py               # POST /api/ingest
│   │   └── health.py               # GET /health, /ready
│   ├── cli/                        # Command-line entrypoints
│   │   ├── ingest.py               # python -m codebase_analyst.cli.ingest
│   │   └── ask.py                  # python -m codebase_analyst.cli.ask
│   ├── services/                   # Business logic layer
│   │   ├── retrieval.py            # Full retrieval pipeline
│   │   ├── answering.py            # Grounded answer generation
│   │   ├── rerank.py               # Cohere Rerank integration
│   │   └── cache.py                # Redis semantic cache
│   ├── ingestion/                  # Code ingestion
│   │   ├── processor.py            # Repo cloning, scanning, hashing
│   │   ├── parser.py               # Tree-sitter + AST parsing
│   │   └── chunker.py              # Structure-aware chunking
│   ├── indexing/                   # Embedding & storage
│   │   ├── embedding.py            # SentenceTransformer embeddings
│   │   ├── vector_store.py         # Qdrant vector store
│   │   └── cache.py                # Legacy semantic cache
│   ├── retrieval/                  # Search components
│   │   ├── hybrid.py               # Dense + sparse fusion
│   │   └── sparse.py               # TF-IDF retriever
│   ├── models/                     # Data models
│   │   ├── schemas.py              # API request/response schemas
│   │   └── domain.py               # Internal domain models
│   ├── analysis/                   # Code analysis tools
│   │   ├── knowledge_graph.py      # Dependency graph (NetworkX)
│   │   ├── architecture.py         # Pattern detection
│   │   └── security.py             # Vulnerability scanning
│   ├── monitoring/                 # Observability
│   │   └── metrics.py              # Prometheus metrics
│   ├── evaluation/                 # RAG quality
│   │   └── rag_evaluator.py        # RAGAS integration
│   ├── ui/                         # Web interface
│   │   └── gradio_app.py           # Gradio UI
│   └── utils/                      # Utilities
│       └── exporter.py             # JSON/MD/HTML export
├── monitoring/                     # Monitoring configs
│   ├── prometheus.yml              # Prometheus scrape config
│   └── grafana/                    # Grafana provisioning
│       ├── dashboards/             # Dashboard JSON
│       └── provisioning/           # Datasource + provider configs
└── tests/                          # Unit tests
    ├── test_config.py
    ├── test_chunker.py
    ├── test_retrieval.py
    └── test_cache.py
```

## Testing

```bash
python -m pytest tests/ -v
```

## Monitoring

Access Grafana at `http://localhost:3000` (admin/admin) to view the pre-configured dashboard with:
- Query rate and latency (P50/P95)
- LLM, retrieval, and rerank latency
- Cache hit rate
- System CPU/memory
- Indexing stats

## Key Design Decisions

1. **Graceful degradation**: All external services (Qdrant, Redis, Cohere) fall back silently. The system works with just an OpenAI key.
2. **Incremental indexing**: File content hashing avoids re-processing unchanged files.
3. **Query classification**: Routes queries intelligently (symbol lookup vs semantic vs architecture).
4. **Version-aware caching**: Cache keys include repo name and commit SHA to avoid stale results.
