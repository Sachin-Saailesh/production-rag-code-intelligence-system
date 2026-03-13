import { cn } from "@/lib/utils";
import { PIPELINE_TOOLS } from "@/lib/constants";
import { ArrowRight } from "lucide-react";

export default function ToolsPipeline() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Pipeline Diagram Head */}
      <section className="bg-card border border-border rounded-xl p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-32 bg-primary/5 blur-3xl rounded-full pointer-events-none" />
        <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
          Intelligence Inference Pipeline
        </h3>
        <div className="flex flex-wrap items-center gap-2 text-sm font-mono text-muted-foreground w-full">
          {["Repository Ingestion", "AST Parsing", "Chunking & Embedding", "Qdrant Indexing", "Sparse Indexing", "Hybrid Retrieval", "Cohere Rerank", "OpenAI Synthesis", "Redis Semantic Cache"].map((step, idx, arr) => (
            <div key={idx} className="flex items-center gap-2 flex-shrink-0 mb-2">
              <span className="bg-secondary px-3 py-1.5 rounded-md border border-border shadow-sm text-foreground">{step}</span>
              {idx < arr.length - 1 && <ArrowRight className="w-4 h-4 text-primary opacity-70" />}
            </div>
          ))}
        </div>
      </section>

      {/* The 18 Tool Cards */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Active Platform Components ({PIPELINE_TOOLS.length})</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {PIPELINE_TOOLS.map((tool) => (
            <div key={tool.id} className="group relative bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all duration-300 shadow-sm hover:shadow-primary/10 flex flex-col h-full">
              
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center border border-border group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                    <tool.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground tracking-tight">{tool.name}</h4>
                    <p className="text-xs font-mono text-muted-foreground">{tool.category}</p>
                  </div>
                </div>
                <StatusBadge status={tool.status} />
              </div>

              <div className="mt-auto pt-4 border-t border-border/50">
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {tool.desc}
                </p>
              </div>

              <div className="mt-4 flex items-center gap-4 text-xs font-semibold text-primary opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                View Telemetry Metrics &rarr;
              </div>

            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    active: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    planned: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    optional: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
    degraded: "bg-amber-500/10 text-amber-500 border-amber-500/20",
  };
  return (
    <span className={cn("px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border", map[status] || map.optional)}>
      {status}
    </span>
  );
}
