// Fallback to localhost if the VITE_API_URL environment variable isn't set
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
// Fallback Mock Data
const MOCKS = {
  health: { 
    status: "ok", 
    version: "1.0.0", 
    services: { redis: "healthy", qdrant: "healthy", llm: "configured" } 
  },
  query: {
    answer: "This is a mock response because the backend API could not be reached. Ensure uvicorn is running on port 8000.",
    citations: [{ file: "mock/file.py", line: 42, snippet: "def mock_function(): pass", score: 0.95 }],
    query_type: "general",
    latency_ms: 450,
    llm_latency_ms: 300,
    retrieval_latency_ms: 100,
    rerank_latency_ms: 50,
    chunks_retrieved: 5,
    cache_hit: false
  }
};

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("Backend offline");
    return await res.json();
  } catch (err) {
    console.warn("Using mock health data:", err);
    return MOCKS.health;
  }
}

export async function fetchRepos() {
  try {
    const res = await fetch(`${API_BASE}/api/repos`);
    if (!res.ok) throw new Error("Backend offline");
    return await res.json();
  } catch (err) {
    console.warn("Using mock repos data:", err);
    return { repos: [] };
  }
}

export async function executeQuery(query: string, topK: number = 7, repoName?: string) {
  try {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK, repo_name: repoName })
    });
    if (!res.ok) throw new Error("Query Failed");
    return await res.json();
  } catch (err) {
    console.warn("Using mock query data:", err);
    return MOCKS.query;
  }
}

export async function deleteRepository(repoName: string) {
  const res = await fetch(`${API_BASE}/api/repos/${encodeURIComponent(repoName)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Deletion Failed");
  return await res.json();
}

export async function fetchSecurityAudit(repoName: string) {
  const res = await fetch(`${API_BASE}/api/analyze/security?repo_name=${encodeURIComponent(repoName)}`);
  if (!res.ok) throw new Error("Security Analysis Failed");
  return await res.json();
}

export async function fetchArchitecture(repoName: string) {
  const res = await fetch(`${API_BASE}/api/analyze/architecture?repo_name=${encodeURIComponent(repoName)}`);
  if (!res.ok) throw new Error("Architecture Analysis Failed");
  return await res.json();
}

export async function ingestRepository(
  repoUrl: string, 
  repoName: string, 
  forceReindex: boolean = false,
  onProgress?: (data: any) => void
) {
  const res = await fetch(`${API_BASE}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl, repo_name: repoName, force_reindex: forceReindex })
  });

  if (!res.ok) throw new Error("Ingestion Failed");
  if (!res.body) throw new Error("No response body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let result = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const dataStr = line.slice(6);
        if (!dataStr) continue;
        
        try {
          const parsed = JSON.parse(dataStr);
          if (onProgress) onProgress(parsed);
          if (parsed.status === "complete" || parsed.status === "error") {
            result = parsed;
          }
        } catch (e) {
          console.warn("Failed to parse SSE JSON:", dataStr);
        }
      }
    }
  }
  return result;
}
