import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  FileCode,
  Loader2,
  Play,
  Skull,
  Copy,
  Check,
} from "lucide-react";
import { cn } from "@/common/utils";

// ── Types ─────────────────────────────────────────────────────────────────────

interface ScriptletDetail {
  found: boolean;
  script_id: string;
  path?: string;
  metadata?: Record<string, string>;
  source?: string;
}

// ── Category colour map ───────────────────────────────────────────────────────

const CAT_COLORS: Record<string, string> = {
  hotkeys: "bg-slate-800 text-slate-200 border-slate-700",
  gui: "bg-blue-900/50 text-blue-300 border-blue-800",
  clipboard: "bg-indigo-900/50 text-indigo-300 border-indigo-800",
  files: "bg-amber-900/50 text-amber-300 border-amber-800",
  windows: "bg-slate-800 text-slate-300 border-slate-700",
  strings: "bg-indigo-900/50 text-indigo-300 border-indigo-800",
  system: "bg-red-900/50 text-red-300 border-red-800",
  productivity: "bg-emerald-900/50 text-emerald-300 border-emerald-800",
  games: "bg-blue-900/50 text-blue-300 border-blue-800",
  testing: "bg-amber-900/50 text-amber-300 border-amber-800",
  network: "bg-slate-800 text-slate-300 border-slate-700",
  ai_generated: "bg-fuchsia-900/50 text-fuchsia-300 border-fuchsia-800",
  general: "bg-slate-800 text-slate-400 border-slate-700",
};

function catClass(cat?: string): string {
  return CAT_COLORS[(cat ?? "general").toLowerCase()] ?? CAT_COLORS.general;
}

// ── Syntax highlight: very minimal AHK coloring ───────────────────────────────

function highlightAhk(source: string): string {
  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const lines = source.split("\n").map((raw) => {
    const line = escape(raw);
    // Comments
    if (/^&lt;!--/.test(line.trimStart()) || /^;/.test(line.trimStart())) {
      return `<span class="text-slate-500 italic">${line}</span>`;
    }
    // Directives (#Requires, #SingleInstance…)
    if (/^#\w/.test(line.trimStart())) {
      return `<span class="text-violet-400">${line}</span>`;
    }
    // Metadata comments: ; @key: value
    if (/^;\s*@/.test(line.trimStart())) {
      return `<span class="text-amber-400/80">${line}</span>`;
    }
    // Keywords
    return line
      .replace(
        /\b(if|else|loop|while|for|return|break|continue|class|static|global|local|throw|try|catch|finally|new|extends)\b/g,
        '<span class="text-violet-300">$1</span>'
      )
      .replace(
        /\b(MsgBox|TrayTip|SetTimer|Hotkey|OnError|OnExit|Send|Run|Sleep|Random|StrUpper|StrLower|StrLen|StrReplace|InStr|SubStr|FileRead|FileOpen|DirSelect|FileSelect|Gui|WinActivate|WinExist|WinGetTitle|A_Now|A_Index|A_ScriptDir|A_AppData|A_Clipboard)\b/g,
        '<span class="text-amber-300">$1</span>'
      )
      .replace(
        /"([^"]*)"/g,
        '<span class="text-emerald-300">"$1"</span>'
      );
  });
  return lines.join("\n");
}

// ── CopyButton ────────────────────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };
  return (
    <button
      type="button"
      onClick={copy}
      title="Copy source"
      className="inline-flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-800/80 px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-700 transition-colors"
    >
      {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

// ── MetaRow ───────────────────────────────────────────────────────────────────

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-3 text-sm">
      <span className="w-28 shrink-0 text-slate-500">{label}</span>
      <span className="text-slate-300 break-all">{value}</span>
    </div>
  );
}

// ── KbdChip ───────────────────────────────────────────────────────────────────

function KbdChip({ label }: { label: string }) {
  return (
    <kbd className="inline-flex items-center rounded border border-slate-600 bg-slate-800 px-2 py-0.5 text-xs font-mono text-slate-200">
      {label}
    </kbd>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export function Detail() {
  const { id } = useParams<{ id: string }>();
  const scriptId = id ?? "";

  const [detail, setDetail] = useState<ScriptletDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [actionMsg, setActionMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(() => {
    if (!scriptId) return;
    setLoading(true);
    fetch(`/api/scriptlet/${encodeURIComponent(scriptId)}`)
      .then((r) => r.json() as Promise<ScriptletDetail>)
      .then((d) => {
        setDetail(d);
        setError(null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [scriptId]);

  useEffect(() => { load(); }, [load]);

  const runScript = async () => {
    setRunning(true);
    setActionMsg(null);
    try {
      const r = await fetch("/api/run_scriptlet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script_id: scriptId }),
      });
      const d = await r.json() as Record<string, unknown>;
      setActionMsg({
        ok: d.success === true,
        text: d.success === true
          ? `Started${d.pid ? ` (PID ${d.pid})` : ""}`
          : String(d.error ?? "Failed to start"),
      });
    } catch (e) {
      setActionMsg({ ok: false, text: e instanceof Error ? e.message : "Error" });
    } finally {
      setRunning(false);
    }
  };

  const stopScript = async () => {
    setStopping(true);
    setActionMsg(null);
    try {
      const r = await fetch("/api/stop_scriptlet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script_id: scriptId }),
      });
      const d = await r.json() as Record<string, unknown>;
      setActionMsg({
        ok: d.success === true,
        text: d.success === true
          ? String(d.message ?? "Stopped")
          : String(d.error ?? "Failed to stop"),
      });
    } catch (e) {
      setActionMsg({ ok: false, text: e instanceof Error ? e.message : "Error" });
    } finally {
      setStopping(false);
    }
  };

  // ── Loading / error states ────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-slate-400 py-8">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading {scriptId}…
      </div>
    );
  }

  if (error || !detail?.found) {
    return (
      <div className="space-y-4">
        <Link to="/scriptlets" className="inline-flex items-center gap-1 text-sm text-slate-400 hover:text-slate-200">
          <ArrowLeft className="h-4 w-4" /> Back to Scriptlets
        </Link>
        <p className="text-amber-400 text-sm">
          {error ?? `Scriptlet '${scriptId}' not found in depot.`}
        </p>
      </div>
    );
  }

  const meta = detail.metadata ?? {};
  const name = meta.name || scriptId;
  const desc = meta.description || "";
  const version = meta.version || "";
  const category = (meta.category || "general").toLowerCase();
  const hotkeysRaw = meta.hotkeys || meta.hotkey || "";
  const hotkeys = hotkeysRaw.replace(/,/g, " ").split(/\s+/).filter(Boolean);
  const extraMeta = Object.entries(meta).filter(
    ([k]) => !["name", "description", "version", "category", "hotkeys", "hotkey"].includes(k)
  );
  const source = detail.source ?? "";

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Breadcrumb */}
      <Link
        to="/scriptlets"
        className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Scriptlets
      </Link>

      {/* Title row */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <FileCode className="h-6 w-6 text-amber-500 shrink-0" />
            <h1 className="text-2xl font-bold text-white">{name}</h1>
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded border font-medium",
                catClass(category)
              )}
            >
              {category}
            </span>
            {version && (
              <span className="text-xs px-2 py-0.5 rounded border border-slate-700 bg-slate-800 text-slate-400">
                v{version}
              </span>
            )}
          </div>
          {desc && <p className="text-slate-400 text-sm max-w-2xl">{desc}</p>}
          {detail.path && (
            <p className="text-xs text-slate-600 font-mono">{detail.path}</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={runScript}
            disabled={running}
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-white px-3 py-2 text-sm font-medium transition-colors"
          >
            {running ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            Run
          </button>
          <button
            type="button"
            onClick={stopScript}
            disabled={stopping}
            className="inline-flex items-center gap-2 rounded-lg bg-red-900/80 hover:bg-red-800 border border-red-800 disabled:opacity-50 text-red-200 px-3 py-2 text-sm font-medium transition-colors"
          >
            {stopping ? <Loader2 className="h-4 w-4 animate-spin" /> : <Skull className="h-4 w-4" />}
            Stop
          </button>
        </div>
      </div>

      {/* Action feedback */}
      {actionMsg && (
        <div
          className={cn(
            "text-sm rounded-lg border px-4 py-2",
            actionMsg.ok
              ? "border-emerald-800 bg-emerald-950/40 text-emerald-300"
              : "border-red-800 bg-red-950/30 text-red-300"
          )}
        >
          {actionMsg.text}
        </div>
      )}

      {/* Metadata card */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">Metadata</h2>
        <div className="space-y-1.5">
          {name !== scriptId && <MetaRow label="Name" value={name} />}
          {desc && <MetaRow label="Description" value={desc} />}
          {version && <MetaRow label="Version" value={version} />}
          <MetaRow label="Category" value={category} />
          {hotkeysRaw && (
            <div className="flex gap-3 text-sm items-start">
              <span className="w-28 shrink-0 text-slate-500">Hotkeys</span>
              <div className="flex flex-wrap gap-1.5">
                {hotkeys.map((h) => (
                  <KbdChip key={h} label={h} />
                ))}
              </div>
            </div>
          )}
          {extraMeta.map(([k, v]) => (
            <MetaRow key={k} label={k} value={String(v)} />
          ))}
        </div>
      </div>

      {/* Source card */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/50 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-300">Source</span>
            <span className="text-xs text-slate-500">
              {source.split("\n").length} lines ·{" "}
              {(source.length / 1024).toFixed(1)} KB
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-slate-600">{scriptId}.ahk</span>
            <CopyButton text={source} />
          </div>
        </div>
        <div className="overflow-x-auto">
          <pre
            className="text-xs font-mono leading-relaxed p-4 max-h-[70vh] overflow-y-auto text-slate-300"
            /* biome-ignore lint/security/noDangerouslySetInnerHtml: intentional syntax highlighting */
            dangerouslySetInnerHTML={{ __html: highlightAhk(source) }}
          />
        </div>
      </div>
    </div>
  );
}
