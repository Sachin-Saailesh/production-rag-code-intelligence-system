import { useEffect, useState } from "react";
import { Network, Database, Layers, FolderGit2, Loader2, AlertCircle } from "lucide-react";
import { fetchRepos, fetchArchitecture } from "@/services/api";

export default function TopologicalProfiler() {
  const [repos, setRepos] = useState<any[]>([]);
  const [targetRepo, setTargetRepo] = useState("");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRepos().then(res => {
      if (res.repos && res.repos.length > 0) {
        setRepos(res.repos);
        setTargetRepo(res.repos[res.repos.length - 1].name);
      }
    });
  }, []);

  useEffect(() => {
    if (!targetRepo) return;
    setLoading(true);
    setError(null);
    fetchArchitecture(targetRepo)
      .then(res => setData(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [targetRepo]);

  const getPrimaryIcon = (pattern: string) => {
    if (pattern === 'layered') return Layers;
    if (pattern === 'microservices') return Network;
    return Database;
  };

  const PrimaryIcon = data ? getPrimaryIcon(data.primary_pattern) : Network;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 h-full flex flex-col">
      
      {/* Target Repo Selector Header */}
      <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between shadow-sm shrink-0">
         <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-2 rounded-lg border border-primary/20">
              <Network className="w-5 h-5 text-primary" />
            </div>
            <div>
               <h2 className="text-lg font-bold tracking-tight">Topological Profiler</h2>
               <p className="text-xs text-muted-foreground">Architectural abstraction & dependency mapping</p>
            </div>
         </div>
         
         <div className="w-64">
          <div className="relative">
            <FolderGit2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <select
              disabled={loading || repos.length === 0}
              className="w-full bg-background border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 appearance-none font-medium"
              value={targetRepo}
              onChange={e => setTargetRepo(e.target.value)}
            >
              {repos.length === 0 ? (
                <option value="">No Repositories Indexed</option>
              ) : (
                repos.map((r, i) => <option key={i} value={r.name}>{r.name}</option>)
              )}
            </select>
          </div>
         </div>
      </div>

      {error ? (
        <div className="flex-1 flex flex-col items-center justify-center border border-destructive/20 rounded-xl bg-destructive/5 text-destructive gap-4 p-8 text-center">
          <AlertCircle className="w-8 h-8 opacity-50" />
          <p className="font-medium text-sm">Failed to generate topological profile.</p>
          <p className="text-xs opacity-80">{error}</p>
        </div>
      ) : loading ? (
        <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-border rounded-xl bg-card/20 text-muted-foreground gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-sm font-medium animate-pulse">Computing Abstract Syntax Tree Graph...</p>
        </div>
      ) : data ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 shrink-0">
            <div className="p-6 rounded-xl border border-primary/20 bg-primary/5 text-card-foreground shadow-sm relative overflow-hidden">
              <div className="absolute top-0 right-0 p-16 bg-primary/10 blur-2xl rounded-full" />
              <h3 className="text-sm font-semibold uppercase tracking-widest text-primary mb-2">Dominant Archetype</h3>
              <p className="text-3xl font-bold tracking-tight flex items-center gap-3 mt-4">
                 <PrimaryIcon className="w-8 h-8 text-primary" />
                 {String(data.primary_pattern).toUpperCase()}
              </p>
              <div className="mt-6 pt-4 border-t border-primary/10 flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Confidence Metric</span>
                <span className="font-mono font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  {((data.detected_patterns?.[data.primary_pattern]?.confidence || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-4">Structural Integrity</h3>
              <p className="text-sm leading-relaxed text-foreground/80">
                {data.summary}
              </p>
              <div className="mt-8 pt-4 border-t border-border/50 flex justify-between items-center text-sm">
                <span className="text-muted-foreground">AST Trace Nodes</span>
                <span className="font-mono font-bold text-foreground bg-secondary px-2 py-0.5 rounded border border-border">
                  {data.file_count || 0} Modules
                </span>
              </div>
            </div>

            <div className="p-6 rounded-xl border bg-card text-card-foreground shadow-sm xl:col-span-1 md:col-span-2">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-4">Language Distribution</h3>
              <div className="space-y-3">
                {Object.entries(data.component_analysis?.file_types || {}).map(([ext, count]: any) => (
                   <div key={ext} className="flex items-center justify-between text-sm">
                      <span className="font-mono text-muted-foreground truncate">{ext === 'no_extension' ? '(No Extension)' : `.${ext}`}</span>
                      <div className="flex items-center gap-3">
                         <div className="w-24 h-2 bg-secondary rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-primary/60 rounded-full" 
                              style={{ width: `${Math.min((count / data.component_analysis.total_files) * 100, 100)}%` }} 
                            />
                         </div>
                         <span className="font-mono text-xs w-8 text-right">{count}</span>
                      </div>
                   </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="bg-card border border-border rounded-xl p-6 flex-1 flex items-center justify-center relative shadow-sm overflow-hidden min-h-[300px]">
             <div className="absolute inset-0 pattern-grid-lg opacity-5 pointer-events-none" />
             <div className="text-center space-y-4 relative z-10 p-8 rounded-2xl bg-background/80 backdrop-blur border border-border/50 shadow-2xl">
                <Network className="w-12 h-12 text-muted-foreground/50 mx-auto" />
                <h3 className="text-lg font-semibold text-foreground/80">Graph Telemetry Ready</h3>
                <p className="text-sm text-muted-foreground max-w-sm mx-auto leading-relaxed">
                  The Live Component Dependency Graph block is currently processing {data.file_count || 0} modular artifacts...
                </p>
             </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
