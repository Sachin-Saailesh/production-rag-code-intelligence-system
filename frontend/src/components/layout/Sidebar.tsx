import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { 
  BarChart, 
  Box, 
  Code, 
  Database, 
  FolderGit2, 
  LayoutDashboard, 
  Network, 
  Settings, 
  ShieldAlert
} from "lucide-react";
import { useIngestion } from "@/contexts/IngestionContext";

const NAV_ITEMS = [
  { name: "Overview", path: "/", icon: LayoutDashboard },
  { name: "Repository Intelligence", path: "/repository", icon: FolderGit2 },
  { name: "Semantic Investigation", path: "/investigation", icon: Code },
  { name: "Topological Profiler", path: "/architecture", icon: Network },
  { name: "Security Audit", path: "/security", icon: ShieldAlert },
  { name: "Tools & Pipeline", path: "/tools", icon: Box },
  { name: "Observability", path: "/observability", icon: BarChart },
  { name: "Cost & Performance", path: "/performance", icon: Database },
];

export function Sidebar() {
  const location = useLocation();
  const { isIngestingGlobal } = useIngestion();

  const handleLinkClick = (e: React.MouseEvent) => {
    if (isIngestingGlobal) {
      e.preventDefault();
      alert("Please wait for the current indexing process to complete before navigating.");
    }
  };

  return (
    <aside className="w-64 border-r border-border bg-card flex flex-col h-screen shrink-0 relative">
      {isIngestingGlobal && (
        <div className="absolute inset-x-0 top-0 h-1 bg-primary animate-pulse" />
      )}
      
      <div className="p-6 h-20 flex items-center border-b border-border">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center text-primary-foreground font-bold shadow-md shadow-primary/20">
            CA
          </div>
          <div>
            <h1 className="font-semibold text-sm leading-none text-foreground">Codebase Analyst</h1>
            <p className="text-xs text-muted-foreground mt-1">Control Plane</p>
          </div>
        </div>
      </div>

      <div className="flex-1 py-4 overflow-y-auto px-3 flex flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={handleLinkClick}
              title={isIngestingGlobal ? "Navigation disabled during indexing" : ""}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors cursor-pointer",
                isActive 
                  ? "bg-secondary text-secondary-foreground" 
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50",
                isIngestingGlobal && !isActive ? "opacity-50 cursor-not-allowed" : ""
              )}
            >
              <item.icon className={cn("w-4 h-4", isActive ? "text-primary" : "opacity-70")} />
              {item.name}
            </Link>
          );
        })}
      </div>

      <div className="p-4 border-t border-border mt-auto">
         <Link
            to="/settings"
            onClick={handleLinkClick}
            title={isIngestingGlobal ? "Navigation disabled during indexing" : ""}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors cursor-pointer",
              location.pathname === "/settings"
                ? "bg-secondary text-secondary-foreground" 
                : "text-muted-foreground hover:text-foreground hover:bg-secondary/50",
              isIngestingGlobal && location.pathname !== "/settings" ? "opacity-50 cursor-not-allowed" : ""
            )}
          >
            <Settings className="w-4 h-4 opacity-70" />
            Integrations
          </Link>
      </div>
    </aside>
  );
}
