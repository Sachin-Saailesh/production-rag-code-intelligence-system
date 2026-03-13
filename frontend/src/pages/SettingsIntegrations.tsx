import { Key, Database, Activity, CheckCircle2 } from "lucide-react";

export default function SettingsIntegrations() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-4xl mx-auto">
      
      <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
           <Activity className="w-5 h-5 text-primary" /> System Readiness Integrations
        </h3>
        
        <div className="space-y-4">
           {/* LLM Check */}
           <div className="flex items-center justify-between p-4 bg-background border border-border rounded-lg">
             <div className="flex items-center gap-4">
               <div className="bg-secondary p-3 rounded-lg"><Key className="w-5 h-5 text-muted-foreground" /></div>
               <div>
                 <h4 className="font-semibold text-sm">Azure OpenAI Engine</h4>
                 <p className="text-xs text-muted-foreground mt-1">Configured for gpt-4o inference generation.</p>
               </div>
             </div>
             <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-500 rounded-full border border-emerald-500/20 text-xs font-bold uppercase tracking-wider">
               <CheckCircle2 className="w-3.5 h-3.5" /> Configured
             </div>
           </div>

           {/* Vector DB Check */}
           <div className="flex items-center justify-between p-4 bg-background border border-border rounded-lg">
             <div className="flex items-center gap-4">
               <div className="bg-secondary p-3 rounded-lg"><Database className="w-5 h-5 text-muted-foreground" /></div>
               <div>
                 <h4 className="font-semibold text-sm">Qdrant Vector Database</h4>
                 <p className="text-xs text-muted-foreground mt-1">FastAPI bound vector indexing storage layer.</p>
               </div>
             </div>
             <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-500 rounded-full border border-emerald-500/20 text-xs font-bold uppercase tracking-wider">
               <CheckCircle2 className="w-3.5 h-3.5" /> Reachable
             </div>
           </div>

           {/* Cache DB Check */}
           <div className="flex items-center justify-between p-4 bg-background border border-border rounded-lg">
             <div className="flex items-center gap-4">
               <div className="bg-secondary p-3 rounded-lg"><Database className="w-5 h-5 text-muted-foreground" /></div>
               <div>
                 <h4 className="font-semibold text-sm">Redis Semantic Cache</h4>
                 <p className="text-xs text-muted-foreground mt-1">KV store caching identical AST responses.</p>
               </div>
             </div>
             <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-500 rounded-full border border-emerald-500/20 text-xs font-bold uppercase tracking-wider">
               <CheckCircle2 className="w-3.5 h-3.5" /> Reachable
             </div>
           </div>
        </div>
      </div>

    </div>
  );
}
