import { useEffect, useState } from "react";
import { AlertTriangle, ShieldCheck, Lock, Unlock, FileTerminal, FolderGit2, Loader2, AlertCircle } from "lucide-react";
import { fetchRepos, fetchSecurityAudit } from "@/services/api";
import { cn } from "@/lib/utils";

export default function SecurityAudit() {
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
    fetchSecurityAudit(targetRepo)
      .then(res => setData(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [targetRepo]);

  const getSeverityIcon = (type: string) => {
    if (type === 'hardcoded_secrets') return Unlock;
    if (type === 'sql_injection') return Lock;
    if (type === 'eval_usage') return FileTerminal;
    return AlertTriangle;
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 h-full flex flex-col">
      
      {/* Target Repo Selector Header */}
      <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between shadow-sm shrink-0">
         <div className="flex items-center gap-3">
            <div className="bg-destructive/10 p-2 rounded-lg border border-destructive/20">
              <ShieldCheck className="w-5 h-5 text-destructive" />
            </div>
            <div>
               <h2 className="text-lg font-bold tracking-tight">Security Audit</h2>
               <p className="text-xs text-muted-foreground">Static vulnerability & anti-pattern detection</p>
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
          <p className="font-medium text-sm">Failed to execute security audit.</p>
          <p className="text-xs opacity-80">{error}</p>
        </div>
      ) : loading ? (
        <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-border rounded-xl bg-card/20 text-muted-foreground gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-destructive" />
          <p className="text-sm font-medium animate-pulse">Scanning AST Nodes for Vulnerabilities...</p>
        </div>
      ) : data ? (
        <>
          {/* Risk Header */}
          <section className="bg-card border border-border rounded-xl p-8 flex flex-col md:flex-row items-center gap-8 shadow-sm">
             <div className="shrink-0 flex items-center justify-center h-32 w-32 rounded-full border-8 border-destructive/20 relative">
                <div 
                  className="absolute inset-0 rounded-full border-4 border-destructive border-t-transparent"
                  style={{ transform: `rotate(${(data.risk_score || 0) * 3.6}deg)` }}
                />
                <div className="flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold tracking-tighter text-destructive">{data.risk_score || 0}</span>
                  <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest mt-1">Risk Score</span>
                </div>
             </div>
             <div className="flex-1 space-y-4">
                <div>
                  <h3 className="text-2xl font-semibold flex items-center gap-2">
                    <ShieldCheck className={cn("w-6 h-6", (data.risk_score || 0) > 50 ? "text-destructive" : (data.risk_score || 0) > 20 ? "text-amber-500" : "text-emerald-500")} />
                    Aggregated Static Risk Profile
                  </h3>
                  <p className="text-muted-foreground mt-2 max-w-2xl text-sm leading-relaxed">
                    The continuous AST inspection pipeline mapped {(data.total_findings || 0)} deterministic security flags across {targetRepo}.
                  </p>
                </div>
                <div className="flex gap-4">
                   <div className="bg-secondary px-4 py-2 rounded-lg border border-border/50">
                     <span className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">High Severity</span>
                     <p className="font-bold text-xl text-destructive mt-1">{data.by_severity?.high || 0}</p>
                   </div>
                   <div className="bg-secondary px-4 py-2 rounded-lg border border-border/50">
                     <span className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Medium</span>
                     <p className="font-bold text-xl text-amber-500 mt-1">{data.by_severity?.medium || 0}</p>
                   </div>
                   <div className="bg-secondary px-4 py-2 rounded-lg border border-border/50">
                     <span className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Low Risk</span>
                     <p className="font-bold text-xl text-zinc-400 mt-1">{data.by_severity?.low || 0}</p>
                   </div>
                </div>
             </div>
          </section>

          {/* Findings Table */}
          <section className="space-y-4">
            <h3 className="text-lg font-semibold tracking-tight">Priority Trace Audit ({data.total_findings || 0} Flags)</h3>
            
            {data.total_findings === 0 ? (
              <div className="bg-card border border-border rounded-xl p-12 text-center text-muted-foreground flex flex-col items-center gap-3">
                <ShieldCheck className="w-10 h-10 text-emerald-500 opacity-50" />
                <p className="text-sm font-medium">No strict compliance or vulnerability flags discovered.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {(data.findings || []).map((finding: any, i: number) => {
                  const Icon = getSeverityIcon(finding.type);
                  return (
                    <div key={i} className="bg-card border border-border rounded-xl overflow-hidden hover:border-border/80 transition-colors">
                       <div className={cn("px-6 py-3 border-b border-border/50 flex items-center justify-between",
                          finding.severity === "high" ? "bg-destructive/10" : finding.severity === "medium" ? "bg-amber-500/10" : "bg-zinc-500/10"
                       )}>
                          <div className="flex items-center gap-3">
                             <Icon className={cn("w-4 h-4", 
                                finding.severity === "high" ? "text-destructive" : finding.severity === "medium" ? "text-amber-500" : "text-muted-foreground"
                             )} />
                             <h4 className={cn("font-semibold font-mono text-sm tracking-tight",
                                 finding.severity === "high" ? "text-destructive" : finding.severity === "medium" ? "text-amber-500" : "text-foreground"
                             )}>{finding.type}</h4>
                          </div>
                          <span className={cn("text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded border",
                              finding.severity === "high" ? "bg-destructive text-destructive-foreground border-destructive/20" : 
                              finding.severity === "medium" ? "bg-amber-500/20 text-amber-600 border-amber-500/30" : 
                              "bg-secondary text-muted-foreground border-border"
                          )}>
                            {finding.severity}
                          </span>
                       </div>
                       <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <div>
                            <h5 className="text-xs font-semibold uppercase text-muted-foreground tracking-wider mb-2">Location & Context</h5>
                            <div className="font-mono text-sm bg-background border border-border rounded-md px-3 py-2 text-primary overflow-x-auto w-full inline-block">
                              {finding.file} <span className="text-muted-foreground">Line {finding.line}</span>
                            </div>
                            <p className="text-sm text-foreground/80 leading-relaxed mt-4">
                              {finding.description}
                            </p>
                          </div>
                          <div className="bg-secondary/50 rounded-lg p-4 border border-border/50">
                            <h5 className="text-xs font-semibold uppercase text-muted-foreground tracking-wider mb-2">AST Node Capture</h5>
                            <pre className="text-xs text-muted-foreground leading-relaxed font-mono whitespace-pre-wrap overflow-x-auto">
                              {finding.snippet}
                            </pre>
                          </div>
                       </div>
                    </div>
                  );
                })}
              </div>
            )}
            
            {data.recommendations && data.recommendations.length > 0 && (
              <div className="mt-8 bg-card border border-emerald-500/20 rounded-xl p-6">
                <h3 className="text-sm font-semibold uppercase tracking-widest text-emerald-500 mb-4 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4" /> Global Mitigations
                </h3>
                <ul className="space-y-2 text-sm text-foreground/80 list-disc list-inside">
                  {data.recommendations.map((rec: string, i: number) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
            
          </section>
        </>
      ) : null}
    </div>
  );
}
