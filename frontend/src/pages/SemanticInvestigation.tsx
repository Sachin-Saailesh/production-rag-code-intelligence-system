import { useEffect, useState } from "react";
import { executeQuery, fetchRepos } from "@/services/api";
import { Search, Loader2, Code, Zap, FileText, FolderGit2 } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from "@/lib/utils";

export default function SemanticInvestigation() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(7);
  const [targetRepo, setTargetRepo] = useState("");
  const [repos, setRepos] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    fetchRepos().then(data => {
      if (data.repos && data.repos.length > 0) {
        setRepos(data.repos);
        setTargetRepo(data.repos[data.repos.length - 1].name);
      }
    });
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    try {
      const data = await executeQuery(query, topK, targetRepo);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 h-full flex flex-col">
      
      {/* Query Bar */}
      <form onSubmit={handleSearch} className="bg-card border border-border rounded-xl p-4 flex flex-col lg:flex-row gap-4 items-end shrink-0 shadow-sm">
        <div className="flex-1 w-full space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground ml-1">Investigation Query</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input 
              autoFocus
              disabled={isSearching}
              className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-shadow disabled:opacity-50 font-medium"
              placeholder="e.g. Explain how the authentication flow and JWT tokens are validated..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className="w-full lg:w-56 space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground ml-1">Target Repository</label>
          <div className="relative">
            <FolderGit2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <select
              disabled={isSearching || repos.length === 0}
              className="w-full bg-background border border-border rounded-lg pl-9 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 appearance-none"
              value={targetRepo}
              onChange={e => setTargetRepo(e.target.value)}
            >
              {repos.length === 0 ? (
                <option value="">No Repos Indexed</option>
              ) : (
                repos.map((r, i) => <option key={i} value={r.name}>{r.name}</option>)
              )}
            </select>
          </div>
        </div>

        <div className="w-full lg:w-40 space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground ml-1">Context Vol (K)</label>
          <input 
            type="number" 
            disabled={isSearching}
            className="w-full bg-background border border-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
            value={topK}
            min={1} max={20}
            onChange={e => setTopK(parseInt(e.target.value) || 7)}
          />
        </div>

        <button 
          disabled={isSearching || !query.trim()}
          type="submit"
          className="w-full lg:w-auto bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-lg font-semibold text-sm transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 fill-primary-foreground/20" />}
          Execute RAG
        </button>
      </form>

      {/* Results Area */}
      {result ? (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-300">
          
          {/* Main Answer Panel */}
          <div className="lg:col-span-2 flex flex-col border border-border bg-card rounded-xl overflow-hidden shadow-sm">
            <div className="bg-secondary/50 px-6 py-4 border-b border-border flex items-center justify-between">
              <h3 className="font-semibold flex items-center gap-2"><Code className="w-4 h-4 text-primary" /> Generated Analysis</h3>
              {result.cache_hit && <span className="bg-emerald-500/10 text-emerald-500 text-[10px] px-2 py-1 rounded-full uppercase tracking-widest font-bold">Cache Hit</span>}
            </div>
            <div className="p-6 overflow-y-auto w-full flex-1 prose prose-invert prose-sm max-w-none prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-border prose-code:text-primary prose-a:text-blue-400 prose-p:leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result.answer}
              </ReactMarkdown>
            </div>
          </div>

          {/* Telemetry & Evidence Panel */}
          <div className="flex flex-col gap-6">
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Pipeline Telemetry</h3>
              <div className="space-y-3 font-mono text-sm">
                <TelemetryRow label="Total Request Time" value={`${(result.latency_ms || 0).toFixed(0)} ms`} highlight={(result.latency_ms || 0) < 1000} />
                <TelemetryRow label="LLM Synthesis Time" value={`${(result.llm_latency_ms || 0).toFixed(0)} ms`} />
                <TelemetryRow label="Vector Retrieval" value={`${(result.retrieval_latency_ms || 0).toFixed(0)} ms`} />
                <TelemetryRow label="Cohere Rerank" value={`${(result.rerank_latency_ms || 0).toFixed(0)} ms`} />
                <TelemetryRow label="Strategy" value={String(result.query_type || "unknown").toUpperCase()} />
                <TelemetryRow label="Candidate Chunks" value={result.chunks_retrieved || 0} />
              </div>
            </div>

            {result.citations && Array.isArray(result.citations) && result.citations.length > 0 && (
              <div className="bg-card border border-border rounded-xl p-6 flex-1 overflow-y-auto">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Evidence Citations</h3>
                <div className="space-y-4">
                  {result.citations.map((c: any, i: number) => (
                    <div key={i} className="flex flex-col gap-1 p-3 bg-secondary/30 rounded-lg border border-border/50">
                      <div className="flex items-center gap-2 text-xs font-mono text-primary truncate">
                        <FileText className="w-3 h-3 shrink-0" />
                        <span className="truncate" title={c.file_path || "unknown"}>{(c.file_path || "unknown").split("/").pop()}</span>
                        <span className="text-muted-foreground ml-auto bg-background px-1.5 py-0.5 rounded border border-border">:L{c.start_line || 0}</span>
                      </div>
                      <span className="text-[10px] text-muted-foreground/70 uppercase tracking-widest mt-1">Confidence Score: {((c.score || 0) * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-border rounded-xl bg-card/20 text-muted-foreground gap-4">
          <Search className="w-8 h-8 opacity-20" />
          <p className="text-sm">Enter a query above to execute hybrid codebase retrieval.</p>
        </div>
      )}
    </div>
  );
}

function TelemetryRow({ label, value, highlight }: any) {
  return (
    <div className="flex justify-between items-center py-1 border-b border-border/40 last:border-0">
      <span className="text-muted-foreground">{label}</span>
      <span className={cn("font-medium", highlight ? "text-emerald-500" : "text-foreground")}>{value}</span>
    </div>
  );
}
