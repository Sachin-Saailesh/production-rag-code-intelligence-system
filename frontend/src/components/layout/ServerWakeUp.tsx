import React, { useState, useEffect } from 'react';
import { Loader2, ServerOff, DatabaseZap } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function ServerWakeUp({ children }: { children: React.ReactNode }) {
  const [isAwake, setIsAwake] = useState<boolean>(false);
  const [error, setError] = useState<boolean>(false);
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;

    const checkHealth = async () => {
      try {
        // Raw fetch to bypass api.ts mock fallbacks
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error("Not 200");
        setIsAwake(true);
      } catch (err) {
        // If it fails, increment attempt and try again in 3 seconds
        setAttempts((prev) => prev + 1);
        if (attempts > 30) {
          // If it takes more than 90 seconds, something is actually broken
          setError(true);
        } else {
          timeoutId = setTimeout(checkHealth, 3000);
        }
      }
    };

    checkHealth();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [attempts]);

  if (isAwake) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full border border-border bg-card/50 backdrop-blur-sm rounded-xl p-8 flex flex-col items-center text-center space-y-6 shadow-2xl">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
          <div className="h-20 w-20 bg-background border border-border rounded-full flex items-center justify-center relative z-10">
            {error ? (
              <ServerOff className="h-10 w-10 text-destructive" />
            ) : (
              <DatabaseZap className="h-10 w-10 text-primary animate-pulse" />
            )}
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-2xl font-semibold tracking-tight">
            {error ? "Backend Unreachable" : "Waking up AI Engine"}
          </h2>
          <p className="text-muted-foreground text-sm leading-relaxed">
            {error ? (
              "The API failed to boot after 90 seconds. Please check Render logs or try again later."
            ) : (
              "The FastAPI backend is currently spinning up from a cold start on Render's free tier. This typically takes about 30 to 50 seconds."
            )}
          </p>
        </div>

        {!error && (
          <div className="w-full space-y-3">
            <div className="flex items-center justify-center space-x-2 text-sm font-medium text-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              <span>Ping attempt {attempts}...</span>
            </div>
            <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary transition-all duration-300 ease-in-out" 
                style={{ width: `${Math.min((attempts / 20) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
