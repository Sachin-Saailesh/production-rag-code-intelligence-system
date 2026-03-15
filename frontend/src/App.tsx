import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { BaseLayout } from '@/components/layout/BaseLayout';

// Lazy load pages for better performance
const Overview = React.lazy(() => import('@/pages/Overview'));
const RepositoryIntelligence = React.lazy(() => import('@/pages/RepositoryIntelligence'));
const SemanticInvestigation = React.lazy(() => import('@/pages/SemanticInvestigation'));
const TopologicalProfiler = React.lazy(() => import('@/pages/TopologicalProfiler'));
const SecurityAudit = React.lazy(() => import('@/pages/SecurityAudit'));
const ToolsPipeline = React.lazy(() => import('@/pages/ToolsPipeline'));
const Observability = React.lazy(() => import('@/pages/Observability'));
const CostPerformance = React.lazy(() => import('@/pages/CostPerformance'));
const SettingsIntegrations = React.lazy(() => import('@/pages/SettingsIntegrations'));

import { IngestionProvider } from '@/contexts/IngestionContext';

export default function App() {
  return (
    <React.Suspense fallback={<div className="h-screen w-screen flex items-center justify-center bg-background text-foreground tracking-tight font-medium">Initializing Workspace...</div>}>
      <IngestionProvider>
        <Routes>
          <Route path="/" element={<BaseLayout title="Overview" description="Executive summary of repository intelligence and platform health."><Overview /></BaseLayout>} />
          <Route path="/repository" element={<BaseLayout title="Repository Intelligence" description="Manage indexed files, embedded chunks, and taxonomy status."><RepositoryIntelligence /></BaseLayout>} />
          <Route path="/investigation" element={<BaseLayout title="Semantic Investigation" description="Natural language querying powered by Graph-Aware BM25 + Dense RAG."><SemanticInvestigation /></BaseLayout>} />
          <Route path="/architecture" element={<BaseLayout title="Topological Profiler" description="Evaluate exact architectural paradigms via AST dependency configurations."><TopologicalProfiler /></BaseLayout>} />
          <Route path="/security" element={<BaseLayout title="Security Audit" description="Review deterministic secret leaks and static vulnerability findings."><SecurityAudit /></BaseLayout>} />
          <Route path="/tools" element={<BaseLayout title="Tools & Pipeline" description="Current active platform services and inference orchestrators."><ToolsPipeline /></BaseLayout>} />
          <Route path="/observability" element={<BaseLayout title="Platform Observability" description="Live telemetry from the retrieval and LLM pipelines."><Observability /></BaseLayout>} />
          <Route path="/performance" element={<BaseLayout title="Cost & Performance" description="Track LLM token spend, caching efficiency, and inference latencies."><CostPerformance /></BaseLayout>} />
          <Route path="/settings" element={<BaseLayout title="Control Integrations" description="Manage database connections, telemetry endpoints, and LLM keys."><SettingsIntegrations /></BaseLayout>} />
        </Routes>
      </IngestionProvider>
    </React.Suspense>
  );
}
