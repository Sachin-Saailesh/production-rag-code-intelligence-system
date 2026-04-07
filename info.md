# Project Information: LinkedIn Post and Resume Drafts

## Captured Screenshots for LinkedIn

I have captured high-quality, full-screen screenshots of your live Vercel deployment directly from the browser. You can attach these three images directly to your LinkedIn post. They are saved in `docs/assets/`.

1. **The Ingestion Progress Stream (Action Shot)**: `docs/assets/ingestion.png`
   *Why this matters:* It proves the streaming architecture and the real-time frontend/backend connection are functioning smoothly in production.

2. **A Deep Architectural Query (Results Shot)**: `docs/assets/query.png`
   *Why this matters:* It demonstrates data intuition, accurate RAG retrieval capabilities, and your clean UI design.

3. **The Overview Dashboard (System Shot)**: `docs/assets/dashboard.png`
   *Why this matters:* It highlights the multi-tenant architectural foresight and built-in observability of the system.

## LinkedIn Post Draft

**Hook:**
Most AI coding tutorials teach you how to build a simple RAG app in a local Jupyter notebook. Very few explore the engineering required to design a scalable software architecture capable of ingesting and understanding massive, enterprise-scale codebases.

**Body:**
Last spring, I built an early prototype for an AI Codebase Intelligence System. Recently, I decided to pull it out of the archives, completely overhaul the underlying architecture for production, and launch it live. You can explore it here: https://production-rag-code-intelligence-sy-ebon.vercel.app/

Taking this project from a local script to a fully deployed, multi-tenant web application was a deep dive into what I call **Systemic Engineering**. It's the challenge of building stable, infinitely scalable software around an AI model, rather than just developing the model in isolation.

Here are a few key architectural milestones from the redesign:

**Systemic Engineering:** I rewrote the core ingestion pipeline into a flat-memory streaming generator. By parsing, chunking, and embedding one file at a time, the architecture scales linearly. It can effortlessly ingest 10,000+ file repositories without locking up resources or encountering memory spikes.

**Data Intuition:** Standard NLP text splitters often destroy programming context. I implemented `tree-sitter` to parse the Abstract Syntax Tree (AST), ensuring code is chunked cleanly at logical function and class boundaries. This drastically improves LLM retrieval accuracy and context coherence.

**Architectural Foresight:** I built a production-grade Hybrid Retrieval engine that natively fuses Dense embeddings (Qdrant and OpenAI `text-embedding-3-small`) with Sparse lexical matching (BM25/TF-IDF). This ensures highly accurate results for both deep architectural concepts and exact variable name lookups.

**Resilience as a Feature:** I built a dynamic fallback priority queue where the system gracefully degrades if Redis caching or Cohere reranking API limits are ever hit. This guarantees the core chat experience remains uninterrupted for the end user, no matter the backend load.

It's one thing to build an LLM workflow; it's entirely another to engineer a resilient, scalable system around it.

If you want to test the architecture, I recommend pasting in `https://github.com/encode/httpx.git` to see the real-time vectorization pipeline in action.

#SoftwareEngineering #SystemDesign #AI #RAG #MachineLearning #WebDevelopment #BackendArchitecture

## Resume Draft (Bullet Points)

**AI Codebase Intelligence Platform (Full-Stack Engineer / AI Engineer)**
*React, FastAPI, Qdrant, Redis, OpenAI, Tree-sitter*
*   Architected and deployed a multi-tenant Production RAG application capable of ingesting remote Git repositories, parsing structural ASTs, and accurately answering complex architectural codebase queries.
*   **Systemic Engineering:** Engineered a highly-optimized, flat-memory data streaming pipeline for code ingestion that parses, chunks, and embeddings files individually, allowing the system to scale linearly and process 10,000+ file repositories without memory spikes.
*   **Data Intuition & Retrieval:** Replaced basic string chunking with `tree-sitter` AST parsing to preserve function semantics. Implemented a Hybrid Search engine combining Dense (Qdrant/OpenAI) and Sparse (BM25/TF-IDF) vector retrieval to maximize citation accuracy.
*   **Architectural Foresight:** Designed the system for graceful degradation and enterprise scaling. Implemented dynamic fallback queues for Redis caching and Cohere reranking, and established strict multi-tenant data isolation using namespaced Qdrant collections.
*   **Validation & UI Integration:** Built a responsive React/Vite frontend utilizing Server-Sent Events (SSE) to stream real-time, granular ingestion progress. This optimized the developer experience while preventing connection timeouts during massive repository scans.
