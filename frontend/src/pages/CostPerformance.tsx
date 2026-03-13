import { DollarSign, Clock, Coins, TrendingDown } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

const COST_DATA = [
  { day: 'Mon', completion: 0.12, embedding: 0.04 },
  { day: 'Tue', completion: 0.45, embedding: 0.15 },
  { day: 'Wed', completion: 0.85, embedding: 0.22 },
  { day: 'Thu', completion: 0.32, embedding: 0.08 },
  { day: 'Fri', completion: 0.65, embedding: 0.18 },
  { day: 'Sat', completion: 0.10, embedding: 0.02 },
  { day: 'Sun', completion: 0.05, embedding: 0.01 },
];

export default function CostPerformance() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
         <CostCard title="Estimated Spend (Today)" value="$0.42" icon={DollarSign} alert={false} />
         <CostCard title="Total Tokens (24h)" value="142.5k" icon={Coins} alert={false} />
         <CostCard title="Semantic Cache Savings" value="~ $1.15" icon={TrendingDown} alert={false} highlight />
         <CostCard title="P99 Latency Penalty" value="1.2s" icon={Clock} alert={true} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
         {/* Chart Panel */}
         <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold mb-6">LLM Inference Spend Tracking (USD)</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={COST_DATA} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis dataKey="day" stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                  <Tooltip 
                    cursor={{ fill: '#27272a', opacity: 0.4 }}
                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                    itemStyle={{ color: '#fafafa' }}
                  />
                  <Bar dataKey="embedding" stackId="a" fill="#10b981" name="Embedding API" radius={[0, 0, 4, 4]} />
                  <Bar dataKey="completion" stackId="a" fill="#2563eb" name="Completion API" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
         </div>

         {/* Optimization List */}
         <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Optimization Strategies</h3>
            <div className="space-y-4">
               <OptCard 
                 title="Increase Cache TTL" 
                 desc="Semantic cache hits are saving $0.05 per identical query. Consider extending vector TTl." 
               />
               <OptCard 
                 title="Filter Test Directories" 
                 desc="Excluding tests/ and docs/ during ingestion saved 45k chunks and $0.12 in embedding costs." 
                 done
               />
               <OptCard 
                 title="Enable Cohere Hybrid" 
                 desc="Cohere reranking will add ~$0.001 per query but reduce hallucination token bloat." 
               />
            </div>
         </div>
      </div>
    </div>
  );
}

function CostCard({ title, value, icon: Icon, alert, highlight }: any) {
  return (
    <div className={cn("bg-card border rounded-xl p-6 transition-colors shadow-sm", highlight ? "border-emerald-500/50 bg-emerald-500/5" : "border-border")}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
        <Icon className={cn("w-4 h-4", alert ? "text-amber-500" : highlight ? "text-emerald-500" : "text-muted-foreground opacity-50")} />
      </div>
      <p className={cn("text-3xl font-bold tracking-tight", alert ? "text-amber-500" : highlight ? "text-emerald-500" : "text-foreground")}>
        {value}
      </p>
    </div>
  )
}

function OptCard({ title, desc, done }: any) {
  return (
    <div className="p-4 rounded-lg bg-background border border-border flex flex-col gap-2 relative overflow-hidden">
      {done && <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500" />}
      <h4 className="text-sm font-semibold">{title}</h4>
      <p className="text-xs text-muted-foreground leading-relaxed">{desc}</p>
    </div>
  )
}
