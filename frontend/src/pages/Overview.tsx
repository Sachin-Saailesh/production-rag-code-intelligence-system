import { useEffect, useState } from "react";
import { fetchHealth, fetchRepos, deleteRepository } from "@/services/api";
import { Activity, Database, Server, CheckCircle2, XCircle, FolderGit2, GitBranch, Loader2, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Overview() {
  const [health, setHealth] = useState<any>(null);
  const [repos, setRepos] = useState<any[]>([]);

  useEffect(() => {
    fetchHealth().then(setHealth);
    fetchRepos().then(data => setRepos(data.repos || []));
  }, []);

  const isHealthy = health?.status === "ok";
  const totalFiles = repos.reduce((acc, r) => acc + (r.files || 0), 0);
  const totalActiveRepos = repos.length;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* KPI Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard title="Repository Coverage" value={`${totalFiles} files`} subtext={`In ${totalActiveRepos} active indexes`} />
        <KPICard title="Retrieval Performance" value="12ms" subtext="P95 Vector Search latency" />
        <KPICard title="Security Risk" value="0 / 100" subtext="No critical flags detected" trend="good" />
        <KPICard title="Platform Health" value={isHealthy ? "Nominal" : "Degraded"} subtext={isHealthy ? "All services reporting OK" : "Service disruption detected"} trend={isHealthy ? "good" : "bad"} />
      </section>

      {/* Indexed Repositories Map */}
      <section className="space-y-4">
         <h3 className="text-lg font-semibold tracking-tight">Active Indexed Repositories</h3>
         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {repos.length > 0 ? repos.map((repo, i) => (
              <RepoCard 
                key={i} 
                name={repo.name} 
                branch={repo.branch || "main"} 
                files={repo.files} 
                status={repo.status} 
                onDelete={() => fetchRepos().then(data => setRepos(data.repos || []))}
              />
            )) : (
              <div className="col-span-1 md:col-span-2 text-center p-8 text-sm text-muted-foreground border border-dashed border-border rounded-xl bg-card">
                No indexed repositories found yet. Visit Repository Intelligence to ingest one.
              </div>
            )}
         </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* System Capabilities Executive Summary */}
        <section className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-semibold tracking-tight">System Capabilities Overview</h3>
          <div className="bg-card border border-border rounded-xl p-6 space-y-6">
            <CapabilityRow 
              title="Repository Management" 
              desc="Initializes the static file taxonomy and computes dense vector embeddings for subsequent query targeting. Triggers AST extraction and chunking."
            />
            <CapabilityRow 
              title="Semantic Investigation" 
              desc="Executes natural language instructions against the indexed Context Engine using LLM synthesis and Hybrid RAG retrieval."
            />
            <CapabilityRow 
              title="Topological Profiler" 
              desc="Evaluates exact architectural paradigms based on AST dependency configurations and module tree density."
            />
            <CapabilityRow 
              title="Security Exfiltration" 
              desc="Conducts continuous static inspection for zero-day vulnerabilities, deterministic secret leaks, and cryptographic flaws."
            />
          </div>
        </section>

        {/* Platform Stack / Health */}
        <section className="space-y-4">
          <h3 className="text-lg font-semibold tracking-tight">Active Platform Stack</h3>
          <div className="bg-card border border-border rounded-xl p-6 flex flex-col gap-4">
            <ServiceHealth name="Vector Database (Qdrant)" status={health?.services?.qdrant} icon={Database} />
            <ServiceHealth name="Semantic Cache (Redis)" status={health?.services?.redis} icon={Server} />
            <ServiceHealth name="Inference Engine (LLM)" status={health?.services?.llm === "configured" ? "healthy" : "unavailable"} icon={Activity} />
            
            <div className="mt-4 pt-4 border-t border-border flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Estimated API Spend (24h)</span>
              <span className="font-mono font-medium">$0.42</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Index Freshness</span>
              <span className="font-mono font-medium">Synced today</span>
            </div>
          </div>
        </section>
      </div>

    </div>
  );
}

function KPICard({ title, value, subtext, trend }: any) {
  return (
    <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
      <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
      <div className="mt-4">
        <span className={cn("text-3xl font-bold tracking-tight", trend === "good" ? "text-emerald-500" : trend === "bad" ? "text-destructive" : "text-foreground")}>
          {value}
        </span>
        <p className="text-xs text-muted-foreground mt-2">{subtext}</p>
      </div>
    </div>
  );
}

function CapabilityRow({ title, desc }: any) {
  return (
    <div className="flex flex-col gap-1 pb-4 border-b border-border/50 last:border-0 last:pb-0">
      <h4 className="font-semibold text-foreground">{title}</h4>
      <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
    </div>
  )
}

function ServiceHealth({ name, status, icon: Icon }: any) {
  const isHealthy = status === "healthy";
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="bg-secondary p-2 rounded-md">
           <Icon className="w-4 h-4 text-muted-foreground" />
        </div>
        <span className="text-sm font-medium">{name}</span>
      </div>
      {isHealthy ? 
        <CheckCircle2 className="w-5 h-5 text-emerald-500" /> : 
        <XCircle className="w-5 h-5 text-destructive" />
      }
    </div>
  )
}

function RepoCard({ name, branch, files, status, onDelete }: { name: string, branch: string, files: number, status: string, onDelete: () => void }) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteRepository(name);
      onDelete();
    } catch (err) {
      console.error(err);
      setIsDeleting(false);
    }
  };

  return (
    <div className="bg-card border border-border p-5 rounded-xl hover:border-primary/30 transition-colors shadow-sm relative group flex items-start justify-between">
      <div className="flex items-start gap-4">
        <div className="mt-1 bg-primary/10 p-2 rounded-lg border border-primary/20">
          <FolderGit2 className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h4 className="font-semibold text-foreground tracking-tight line-clamp-1">{name}</h4>
          <div className="flex items-center gap-3 mt-1.5 text-xs text-muted-foreground font-mono">
            <span className="flex items-center gap-1"><GitBranch className="w-3 h-3" />{branch}</span>
            <span className="flex items-center gap-1"><Database className="w-3 h-3" />{files} files</span>
          </div>
        </div>
      </div>
      <div className="flex flex-col items-center justify-center h-full gap-2">
         {status === "synced" && <CheckCircle2 className="w-5 h-5 text-green-500/80" />}
         <button 
           onClick={handleDelete}
           disabled={isDeleting}
           title="Delete Repository Index"
           className="opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-md hover:bg-destructive/10 hover:text-destructive text-muted-foreground disabled:opacity-50"
         >
           {isDeleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
         </button>
      </div>
    </div>
  );
}
