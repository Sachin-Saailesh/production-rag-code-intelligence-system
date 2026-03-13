import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const TIMELINE_DATA = [
  { time: '10:00', requests: 120, p95: 140 },
  { time: '10:15', requests: 180, p95: 155 },
  { time: '10:30', requests: 250, p95: 220 },
  { time: '10:45', requests: 400, p95: 350 },
  { time: '11:00', requests: 310, p95: 190 },
  { time: '11:15', requests: 150, p95: 145 },
  { time: '11:30', requests: 450, p95: 410 },
];

const STAGE_LATENCY = [
  { stage: 'AST Parse', ms: 12 },
  { stage: 'Embed', ms: 45 },
  { stage: 'Vector Search', ms: 14 },
  { stage: 'Cohere Rerank', ms: 85 },
  { stage: 'OpenAI Gen', ms: 450 },
];

export default function Observability() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Latency Timeline Panel */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col min-h-[300px]">
          <h3 className="text-lg font-semibold mb-6">P95 Inference Latency</h3>
          <div className="flex-1 w-full min-h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={TIMELINE_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis dataKey="time" stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}ms`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                  itemStyle={{ color: '#fafafa' }}
                />
                <Line type="monotone" dataKey="p95" stroke="#2563eb" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Throughput Timeline Panel */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col min-h-[300px]">
          <h3 className="text-lg font-semibold mb-6">System Query Throughput</h3>
          <div className="flex-1 w-full min-h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={TIMELINE_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis dataKey="time" stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{ fill: '#27272a', opacity: 0.4 }}
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                />
                <Bar dataKey="requests" fill="#a1a1aa" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Stage Latency Breakdown */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col min-h-[300px]">
          <h3 className="text-lg font-semibold mb-6">Pipeline Stage Decomposition (ms)</h3>
          <div className="flex-1 w-full min-h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={STAGE_LATENCY} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
                <XAxis type="number" stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="stage" type="category" stroke="#fafafa" fontSize={12} tickLine={false} axisLine={false} width={100} />
                <Tooltip 
                  cursor={{ fill: '#27272a', opacity: 0.4 }}
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                />
                <Bar dataKey="ms" fill="#2563eb" radius={[0, 4, 4, 0]} maxBarSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
