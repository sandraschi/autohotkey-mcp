import { useLocation } from "react-router-dom";

const LABELS: Record<string, string> = {
  "/": "Overview",
  "/help": "Help",
  "/scriptlets": "Scriptlets",
  "/status": "Status",
};

export function Topbar() {
  const location = useLocation();
  const label = LABELS[location.pathname] ?? "AutoHotkey MCP";

  return (
    <header className="flex h-14 items-center border-b border-slate-800 bg-slate-950/50 px-6">
      <h1 className="text-sm font-medium text-slate-400">
        <span className="text-slate-100">{label}</span>
      </h1>
    </header>
  );
}
