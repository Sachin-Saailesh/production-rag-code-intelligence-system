import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";

interface BaseLayoutProps {
  children: ReactNode;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function BaseLayout({ children, title, description, actions }: BaseLayoutProps) {
  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header */}
        <header className="h-20 shrink-0 border-b border-border bg-card/50 backdrop-blur pb-px">
          <div className="h-full px-8 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
              {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
            </div>
            {actions && <div className="flex items-center gap-3">{actions}</div>}
          </div>
        </header>
        
        {/* Main scrollable content area */}
        <main className="flex-1 overflow-y-auto p-8 relative">
          <div className="max-w-7xl mx-auto space-y-8 pb-8">
             {children}
          </div>
        </main>
      </div>
    </div>
  );
}
