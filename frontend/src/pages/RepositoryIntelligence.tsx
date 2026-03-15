import { useEffect, useState } from "react";
import { FolderGit2, HardDrive, Files, GitCommit, Search, RefreshCw, BarChart4, Loader2, CheckCircle2, GitBranch } from "lucide-react";
import { cn } from "@/lib/utils";
import { ingestRepository, fetchRepos } from "@/services/api";

export default function RepositoryIntelligence() {
  const [repoUrl, setRepoUrl] = useState("");
  const [repoName, setRepoName] = useState("");
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestProgress, setIngestProgress] = useState<any>(null);
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [repos, setRepos] = useState<any[]>([]);

  useEffect(() => {
    fetchRepos().then(data => setRepos(data.repos || []));
  }, []);

  const activeRepo = repos.length > 0 ? repos[repos.length - 1] : null;

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl || !repoName) return;
    setIsIngesting(true);
    setIngestProgress(null);
    setIngestResult(null);
    try {
      const res = await ingestRepository(repoUrl, repoName, false, (data: any) => {
        setIngestProgress(data);
      });
      setIngestResult(res);
      setRepoUrl("");
      setRepoName("");
    } catch (err) {
      console.error(err);
      setIsIngesting(false);
      fetchRepos().then(data => setRepos(data.repos || []));
    }
  };

  const handleReindex = async () => {
    if (!activeRepo) return;
    setIsIngesting(true);
    setIngestProgress(null);
    setIngestResult(null);
    try {
      const res = await ingestRepository("", activeRepo.name, true, (data) => {
        setIngestProgress(data);
      });
      setIngestResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsIngesting(false);
      fetchRepos().then(data => setRepos(data.repos || []));
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Active Target Header */}
      <section className="bg-card border border-border rounded-xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm">
        <div className="flex items-center gap-4">
           <div className="bg-primary/10 p-4 rounded-full border border-primary/20">
              <FolderGit2 className="w-8 h-8 text-primary" />
           </div>
           <div>
              <h2 className="text-xl font-semibold tracking-tight">{activeRepo ? activeRepo.name : "No Repository Indexed Yet"}</h2>
              {activeRepo && (
                <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground font-mono">
                   <span className="flex items-center gap-1"><GitCommit className="w-3 h-3" /> {activeRepo.branch}</span>
                   <span className="flex items-center gap-1"><RefreshCw className="w-3 h-3" /> Synced locally</span>
                </div>
              )}
           </div>
        </div>
        <button 
          onClick={handleReindex}
          disabled={!activeRepo || isIngesting}
          className="bg-secondary text-foreground hover:bg-secondary/80 px-6 py-2.5 rounded-lg text-sm font-semibold transition-colors border border-border flex items-center gap-2 disabled:opacity-50"
        >
           {isIngesting ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />} 
           Re-Index Source
        </button>
      </section>

      {/* Grid Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         <StatCard title="Target Files" value={activeRepo ? activeRepo.files.toString() : "0"} icon={Files} />
         <StatCard title="Vector Chunks" value={ingestResult ? ingestResult.chunks_created : "—"} icon={HardDrive} />
         <StatCard title="Embedding Model" value="text-embedding-3-small" icon={Search} isText />
         <StatCard title="Status" value={activeRepo ? activeRepo.status.toUpperCase() : "PENDING"} icon={BarChart4} />
      </div>

      {/* Dynamic Ingestion Form */}
      <section className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col lg:flex-row gap-8">
         <div className="flex-1">
           <h3 className="text-lg font-semibold mb-2">Index External Repository</h3>
           <p className="text-sm text-muted-foreground mb-6">Connect a public Git repository to compute graph-aware AST embeddings and semantic context.</p>
           
           <form onSubmit={handleIngest} className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground ml-1">Git Clone URL</label>
                <div className="relative">
                  <GitBranch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input 
                    required
                    disabled={isIngesting}
                    type="url"
                    placeholder="https://github.com/tiangolo/fastapi.git"
                    className="w-full bg-background border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground ml-1">Project Name Target</label>
                <input 
                  required
                  disabled={isIngesting}
                  type="text"
                  placeholder="fastapi"
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                  value={repoName}
                  onChange={(e) => setRepoName(e.target.value)}
                />
              </div>

              <button 
                disabled={isIngesting || !repoUrl || !repoName}
                type="submit"
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2.5 rounded-lg font-semibold text-sm transition-colors disabled:opacity-50 flex items-center justify-center gap-2 mt-4"
              >
                {isIngesting ? <Loader2 className="w-4 h-4 animate-spin" /> : <HardDrive className="w-4 h-4" />}
                {isIngesting ? "Extracting AST & Embedding..." : "Start Ingestion Pipeline"}
              </button>
           </form>
         </div>

         {/* Ingestion Results Panel */}
         <div className="flex-1 bg-background border border-border/50 rounded-lg p-6 flex flex-col justify-center min-h-[300px]">
            {isIngesting && ingestProgress ? (
              <div className="space-y-6 animate-in fade-in duration-300 w-full max-w-sm mx-auto">
                <div className="flex flex-col items-center justify-center text-center gap-4">
                  <div className="relative">
                     <Loader2 className="w-12 h-12 text-primary animate-spin" />
                     <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
                  </div>
                  <div>
                    <h4 className="font-bold text-lg text-primary tracking-tight capitalize">
                      {ingestProgress.status}... {ingestProgress.progress !== undefined && <span className="text-muted-foreground ml-1">{ingestProgress.progress}%</span>}
                    </h4>
                    <p className="text-sm text-muted-foreground mt-1 max-w-[280px] leading-relaxed">{ingestProgress.message}</p>
                  </div>
                </div>
                
                <div className="w-full bg-secondary rounded-full h-1.5 overflow-hidden">
                   <div 
                     className={cn("bg-primary h-full rounded-full transition-all duration-300", 
                       ingestProgress.progress === undefined ? "animate-pulse w-full" : ""
                     )} 
                     style={{ width: ingestProgress.progress !== undefined ? `${ingestProgress.progress}%` : '100%' }}
                   />
                </div>
              </div>
            ) : ingestResult ? (
              <div className="space-y-4 animate-in fade-in zoom-in-95 duration-300">
                <div className="flex items-center gap-2 text-emerald-500 mb-4">
                  <CheckCircle2 className="w-6 h-6" />
                  <h4 className="font-semibold text-lg">Ingestion Complete</h4>
                </div>
                <div className="space-y-2 text-sm font-mono bg-card rounded-md p-4 border border-border">
                  <div className="flex justify-between"><span className="text-muted-foreground">Target:</span> <span>{ingestResult.repo_name}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Files Parsed:</span> <span>{ingestResult.files_processed}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Total Vector Chunks:</span> <span>{ingestResult.chunks_created}</span></div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-muted-foreground gap-4 opacity-40">
                <FolderGit2 className="w-12 h-12" />
                <p className="text-sm text-center max-w-[250px]">Pipeline telemetry will appear here once indexing completes.</p>
              </div>
            )}
         </div>
      </section>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, isText }: any) {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
        <Icon className="w-4 h-4 text-muted-foreground opacity-50" />
      </div>
      <p className={cn("tracking-tight text-foreground", isText ? "text-lg font-mono truncate" : "text-3xl font-bold")}>
        {value}
      </p>
    </div>
  )
}
