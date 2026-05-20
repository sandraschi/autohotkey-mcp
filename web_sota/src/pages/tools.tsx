import { useState, useCallback } from "react";
import { Wand2, Loader2, ChevronDown, ChevronUp, Play, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/common/utils";

// ── Types ─────────────────────────────────────────────────────────────────────

interface ToolDef {
  id: string;
  label: string;
  description: string;
  args?: ArgDef[];
  defaultArgs?: Record<string, string>;
  badge?: string;
  badgeColor?: string;
}

interface ArgDef {
  name: string;
  label: string;
  placeholder?: string;
  defaultValue?: string;
}

interface ToolResult {
  ok: boolean;
  data?: unknown;
  plain?: string;
  error?: string;
  ms?: number;
}

// ── Tool catalogue ─────────────────────────────────────────────────────────────

const TOOLS: ToolDef[] = [
  {
    id: "show_server_status_card",
    label: "Server Status",
    description:
      "Dashboard KPIs: scriptlet count, running count, bridge UP/DOWN, AHK exe found/missing. Config table with all env settings.",
    badge: "status",
    badgeColor: "bg-emerald-900/60 text-emerald-300 border-emerald-800",
  },
  {
    id: "show_scriptlets_card",
    label: "All Scriptlets",
    description:
      "DataTable of every scriptlet in the depot with Dot running indicator, Badge category (colour-coded), sortable ID column, search, pagination.",
    badge: "list",
    badgeColor: "bg-amber-900/60 text-amber-300 border-amber-800",
  },
  {
    id: "show_running_scriptlets_card",
    label: "Running Scriptlets",
    description:
      "Dashboard with 3 Metric KPI tiles (Running / Direct / Bridge) plus a live DataTable of active instances with PID, source badge, hotkeys.",
    badge: "live",
    badgeColor: "bg-red-900/60 text-red-300 border-red-800",
  },
  {
    id: "show_ahk_help_card",
    label: "AHK v2 Help",
    description:
      "Six-tab help card (quick / reference / language / usage / tools / mcp_server), each tab rendered as Markdown. Click a tab to switch.",
    badge: "docs",
    badgeColor: "bg-blue-900/60 text-blue-300 border-blue-800",
    args: [{ name: "level", label: "Level", placeholder: "quick", defaultValue: "quick" }],
  },
  {
    id: "show_scriptlet_detail_card",
    label: "Scriptlet Detail",
    description:
      "Single scriptlet: full AHK source in a Code block with syntax highlighting, metadata Badges, Kbd hotkey chips. Enter a scriptlet id below.",
    badge: "detail",
    badgeColor: "bg-violet-900/60 text-violet-300 border-violet-800",
    args: [{ name: "script_id", label: "Script ID", placeholder: "e.g. quick_notes" }],
  },
  {
    id: "show_generation_result_card",
    label: "Generation Result",
    description:
      "Render a freshly-generated script from ai_generated/ as a Code card with safety warning banner. Use after generate_scriptlet.",
    badge: "ai",
    badgeColor: "bg-fuchsia-900/60 text-fuchsia-300 border-fuchsia-800",
    args: [{ name: "script_id", label: "Script ID (stem)", placeholder: "e.g. my_generated_script" }],
  },
];

// ── API helper ────────────────────────────────────────────────────────────────

async function callTool(toolId: string, args: Record<string, string>): Promise<ToolResult> {
  const t0 = Date.now();
  try {
    const r = await fetch("/tool", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: toolId, arguments: args }),
    });
    const data = await r.json() as Record<string, unknown>;
    const ms = Date.now() - t0;
    if (!r.ok || data.success === false) {
      return { ok: false, error: String(data.error ?? data.detail ?? `HTTP ${r.status}`), ms };
    }
    const result = data.result ?? data;
    // Extract plain text from content array if present
    const plain =
      typeof result === "object" && result !== null && "content" in result
        ? (result as { content?: { text?: string }[] }).content?.[0]?.text
        : undefined;
    return { ok: true, data: result, plain, ms };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Request failed", ms: Date.now() - t0 };
  }
}

// ── ToolCard component ─────────────────────────────────────────────────────────

interface ToolCardProps {
  tool: ToolDef;
}

function ToolCard({ tool }: ToolCardProps) {
  const [argValues, setArgValues] = useState<Record<string, string>>(
    Object.fromEntries((tool.args ?? []).map((a) => [a.name, a.defaultValue ?? ""]))
  );
  const [result, setResult] = useState<ToolResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const invoke = useCallback(async () => {
    setLoading(true);
    setResult(null);
    const r = await callTool(tool.id, argValues);
    setResult(r);
    setExpanded(true);
    setLoading(false);
  }, [tool.id, argValues]);

  const hasArgs = (tool.args ?? []).length > 0;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
      {/* Header */}
      <div className="px-5 pt-5 pb-3 space-y-2">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-base font-semibold text-white">{tool.label}</h2>
            {tool.badge && (
              <span
                className={cn(
                  "text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded border",
                  tool.badgeColor
                )}
              >
                {tool.badge}
              </span>
            )}
          </div>
          <code className="text-[11px] font-mono text-slate-500 shrink-0">{tool.id}()</code>
        </div>
        <p className="text-sm text-slate-400 leading-relaxed">{tool.description}</p>
      </div>

      {/* Args */}
      {hasArgs && (
        <div className="px-5 pb-3 flex flex-wrap gap-3">
          {(tool.args ?? []).map((arg) => (
            <div key={arg.name} className="flex-1 min-w-[180px]">
              <label className="block text-[10px] uppercase tracking-wide text-slate-500 mb-1">
                {arg.label}
              </label>
              <input
                type="text"
                value={argValues[arg.name] ?? ""}
                onChange={(e) =>
                  setArgValues((prev) => ({ ...prev, [arg.name]: e.target.value }))
                }
                placeholder={arg.placeholder}
                className="w-full rounded-lg border border-slate-700 bg-slate-950/80 px-3 py-1.5 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
              />
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="px-5 pb-4 flex items-center gap-2">
        <button
          type="button"
          onClick={invoke}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white px-4 py-2 text-sm font-medium transition-colors"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          Invoke
        </button>
        {result && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="inline-flex items-center gap-1 rounded-lg border border-slate-700 text-slate-400 hover:bg-slate-800 px-3 py-2 text-sm transition-colors"
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {expanded ? "Hide" : "Show"} result
          </button>
        )}
        {result?.ms !== undefined && (
          <span className="text-xs text-slate-600">{result.ms}ms</span>
        )}
        {result?.ok === true && (
          <span className="text-xs text-emerald-400">✓ ok</span>
        )}
        {result?.ok === false && (
          <span className="text-xs text-red-400">✗ error</span>
        )}
      </div>

      {/* Result */}
      {result && expanded && (
        <div className="border-t border-slate-800">
          {result.ok ? (
            <div className="p-4 space-y-3">
              {/* Plain text summary */}
              {result.plain && (
                <pre className="text-xs text-slate-400 whitespace-pre-wrap leading-relaxed bg-slate-950/60 rounded-lg p-3 max-h-40 overflow-y-auto">
                  {result.plain}
                </pre>
              )}
              {/* JSON data */}
              <details className="group">
                <summary className="cursor-pointer text-xs text-slate-500 hover:text-slate-300 select-none">
                  Raw JSON response
                </summary>
                <pre className="mt-2 text-[11px] font-mono text-slate-400 bg-slate-950/80 rounded-lg p-3 max-h-64 overflow-auto">
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              </details>
            </div>
          ) : (
            <div className="p-4">
              <p className="text-sm text-red-300 bg-red-950/30 rounded-lg border border-red-900/40 px-3 py-2">
                {result.error}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export function Tools() {
  const [invokeAll, setInvokeAll] = useState(false);

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Wand2 className="h-7 w-7 text-amber-500" />
            Prefab Tools
          </h1>
          <p className="text-slate-400 mt-1 text-sm max-w-2xl">
            The six{" "}
            <code className="text-slate-500">@mcp.tool(app=True)</code> Prefab UI tools exposed by
            this server. Each returns a{" "}
            <code className="text-slate-500">ToolResult</code> with rich{" "}
            <strong className="text-slate-300">prefab-ui 0.19.1</strong> structured content (
            DataTable, Dashboard, Tabs, Code, Badge, Metric, Kbd…) when called from an MCP host
            like Claude Desktop. Hit <strong className="text-slate-300">Invoke</strong> to call any
            tool directly against the running server via{" "}
            <code className="text-slate-500">POST /tool</code> and inspect the plain-text fallback
            and raw JSON payload.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/scriptlets"
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Scriptlets
          </Link>
        </div>
      </div>

      {/* Notice */}
      <div className="rounded-lg border border-amber-900/40 bg-amber-950/20 px-4 py-3 text-sm text-amber-200/80 leading-relaxed">
        <strong className="text-amber-300">MCP host vs webapp:</strong> When called from Claude
        Desktop or Cursor, these tools render as interactive Prefab UI cards inline in the
        conversation. From this webapp the plain-text fallback and raw JSON are shown instead —
        the structured content is there, just not rendered by a React prefab runtime here.
      </div>

      {/* Tool cards */}
      <div className="space-y-4">
        {TOOLS.map((t) => (
          <ToolCard key={t.id} tool={t} />
        ))}
      </div>
    </div>
  );
}
