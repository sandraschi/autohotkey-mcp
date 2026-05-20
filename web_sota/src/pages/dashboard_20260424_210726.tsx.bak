import { Link } from "react-router-dom";
import { HelpCircle, FileCode, Activity, MessageSquare, Layers } from "lucide-react";

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">AutoHotkey MCP</h1>
        <p className="text-slate-400 mt-1">
          Scriptlet depot and ScriptletCOMBridge. Browse Help, Chat, Scriptlets, Running processes, and Status from the
          sidebar.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          to="/help"
          className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50 transition-colors"
        >
          <HelpCircle className="h-8 w-8 text-amber-500 mb-2" />
          <h2 className="font-semibold text-white">Help</h2>
          <p className="text-sm">AHK quick reference, language, tools, MCP server docs.</p>
        </Link>
        <Link
          to="/chat"
          className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50 transition-colors"
        >
          <MessageSquare className="h-8 w-8 text-amber-500 mb-2" />
          <h2 className="font-semibold text-white">Chat</h2>
          <p className="text-sm">Local LLM personas, preset prompts, refine ideas for generation.</p>
        </Link>
        <Link
          to="/scriptlets"
          className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50 transition-colors"
        >
          <FileCode className="h-8 w-8 text-amber-500 mb-2" />
          <h2 className="font-semibold text-white">Scriptlets</h2>
          <p className="text-sm">List and inspect scriptlets from the depot.</p>
        </Link>
        <Link
          to="/running"
          className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50 transition-colors"
        >
          <Layers className="h-8 w-8 text-amber-500 mb-2" />
          <h2 className="font-semibold text-white">Running</h2>
          <p className="text-sm">Hotkeys, descriptions, PIDs — kill bridge or direct-run instances.</p>
        </Link>
        <Link
          to="/status"
          className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50 transition-colors"
        >
          <Activity className="h-8 w-8 text-amber-500 mb-2" />
          <h2 className="font-semibold text-white">Status</h2>
          <p className="text-sm">Backend health and service info.</p>
        </Link>
      </div>
    </div>
  );
}
