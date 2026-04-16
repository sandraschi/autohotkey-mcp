import { useMemo, useState, useEffect, type FormEvent } from "react";
import { useLocation } from "react-router-dom";
import { FileCode, Loader2, Search, Sparkles } from "lucide-react";

interface ScriptletInfo {
  name?: string;
  id?: string;
  description?: string;
  category?: string;
  running?: boolean;
  [key: string]: unknown;
}

function normalizeCategory(s: ScriptletInfo): string {
  const c = typeof s.category === "string" ? s.category.trim() : "";
  return c || "general";
}

function sortCategories(a: string, b: string): number {
  const order = (x: string) => {
    const low = x.toLowerCase();
    if (low === "general") return "\u0100";
    if (low === "uncategorized") return "\u0101";
    return low;
  };
  return order(a).localeCompare(order(b));
}

type GenResult =
  | { ok: true; path?: string; scriptId?: string; source?: string; warning?: string }
  | { ok: false; message: string };

export function Scriptlets() {
  const location = useLocation();
  const [scriptlets, setScriptlets] = useState<ScriptletInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [genPrompt, setGenPrompt] = useState("");
  const [genFilename, setGenFilename] = useState("");
  const [genLoading, setGenLoading] = useState(false);
  const [genResult, setGenResult] = useState<GenResult | null>(null);

  const loadScriptlets = () => {
    fetch("/api/scriptlets")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("Failed to load scriptlets"))))
      .then((data) => setScriptlets(Array.isArray(data.scriptlets) ? data.scriptlets : []))
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Unknown error");
        setScriptlets([]);
      });
  };

  useEffect(() => {
    loadScriptlets();
  }, []);

  useEffect(() => {
    const st = location.state as { prefilledPrompt?: string } | undefined;
    if (st?.prefilledPrompt && typeof st.prefilledPrompt === "string") {
      setGenPrompt(st.prefilledPrompt);
      setGenResult(null);
    }
  }, [location.state]);

  const handleGenerate = async (e: FormEvent) => {
    e.preventDefault();
    const prompt = genPrompt.trim();
    if (prompt.length < 3) {
      setGenResult({ ok: false, message: "Describe the script in at least a few characters." });
      return;
    }
    setGenLoading(true);
    setGenResult(null);
    try {
      const body: Record<string, string> = { prompt };
      const fn = genFilename.trim();
      if (fn) body.filename = fn;
      const r = await fetch("/api/generate_scriptlet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = (await r.json()) as Record<string, unknown>;
      if (data.success === true) {
        setGenResult({
          ok: true,
          path: typeof data.path === "string" ? data.path : undefined,
          scriptId: typeof data.script_id === "string" ? data.script_id : undefined,
          source: typeof data.generation_source === "string" ? data.generation_source : undefined,
          warning: typeof data.warning === "string" ? data.warning : undefined,
        });
        setGenPrompt("");
        loadScriptlets();
      } else {
        const err = typeof data.error === "string" ? data.error : "Generation failed";
        const hint = typeof data.hint === "string" ? data.hint : "";
        setGenResult({ ok: false, message: hint ? `${err} — ${hint}` : err });
      }
    } catch (err) {
      setGenResult({
        ok: false,
        message: err instanceof Error ? err.message : "Request failed",
      });
    } finally {
      setGenLoading(false);
    }
  };

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return scriptlets;
    return scriptlets.filter((s) => {
      const id = String(s.id ?? s.name ?? "").toLowerCase();
      const name = String(s.name ?? "").toLowerCase();
      const desc = String(s.description ?? "").toLowerCase();
      const cat = normalizeCategory(s).toLowerCase();
      return id.includes(q) || name.includes(q) || desc.includes(q) || cat.includes(q);
    });
  }, [scriptlets, query]);

  const grouped = useMemo(() => {
    const map = new Map<string, ScriptletInfo[]>();
    for (const s of filtered) {
      const cat = normalizeCategory(s);
      if (!map.has(cat)) map.set(cat, []);
      map.get(cat)!.push(s);
    }
    for (const [, arr] of map) {
      arr.sort((a, b) => String(a.id ?? a.name ?? "").localeCompare(String(b.id ?? b.name ?? "")));
    }
    return [...map.entries()].sort(([ca], [cb]) => sortCategories(ca, cb));
  }, [filtered]);

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileCode className="h-7 w-7 text-amber-500" />
          Scriptlets
        </h1>
        <p className="text-amber-400">
          Backend unreachable or no scriptlets. Ensure bridge (10744) and backend are running.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileCode className="h-7 w-7 text-amber-500" />
          Scriptlets
        </h1>
        <p className="text-slate-400 mt-1">
          Grouped by <code className="text-slate-500">@category</code> in each script header (depot scan). Bridge
          listings without a category show as <strong className="text-slate-300">general</strong>.
        </p>
      </div>

      <form
        onSubmit={handleGenerate}
        className="rounded-lg border border-amber-900/40 bg-slate-900/60 p-4 space-y-3 max-w-2xl"
      >
        <div className="flex items-center gap-2 text-amber-200/90">
          <Sparkles className="h-5 w-5 text-amber-500 shrink-0" />
          <span className="font-medium">Generate AHK v2 (sandbox)</span>
        </div>
        <p className="text-slate-400 text-xs leading-relaxed">
          This form uses <strong className="text-slate-300">localhost HTTP only</strong> (
          <code className="text-slate-500">AUTOHOTKEY_LLM_*</code>, Ollama/LM Studio). From an MCP client, prefer{" "}
          <code className="text-slate-500">generate_scriptlet</code> — <strong className="text-slate-300">FastMCP
          sampling</strong> is tried first there. Writes only under{" "}
          <code className="text-slate-500">scriptlets/ai_generated/</code> after validation. Review before running.
        </p>
        <textarea
          value={genPrompt}
          onChange={(e) => setGenPrompt(e.target.value)}
          rows={3}
          placeholder="Describe what the script should do (e.g. hotkey to paste clipboard as plain text)…"
          className="w-full rounded-lg border border-slate-700 bg-slate-950/80 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
        />
        <div className="flex flex-col sm:flex-row gap-2 sm:items-end">
          <div className="flex-1">
            <label className="block text-[10px] uppercase tracking-wide text-slate-500 mb-1">Optional filename stem</label>
            <input
              type="text"
              value={genFilename}
              onChange={(e) => setGenFilename(e.target.value)}
              placeholder="my_hotkey (saved as my_hotkey.ahk)"
              className="w-full rounded-lg border border-slate-700 bg-slate-950/80 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
            />
          </div>
          <button
            type="submit"
            disabled={genLoading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white px-4 py-2 text-sm font-medium shrink-0"
          >
            {genLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            Generate
          </button>
        </div>
        {genResult ? (
          genResult.ok ? (
            <div className="rounded border border-emerald-900/50 bg-emerald-950/30 px-3 py-2 text-xs text-emerald-200/90 space-y-1">
              <p>Saved{genResult.scriptId ? ` as ${genResult.scriptId}.ahk` : ""}.</p>
              {genResult.path ? (
                <p className="font-mono text-emerald-300/80 break-all">{genResult.path}</p>
              ) : null}
              {genResult.source ? <p className="text-slate-400">Source: {genResult.source}</p> : null}
              {genResult.warning ? <p className="text-amber-200/80">{genResult.warning}</p> : null}
            </div>
          ) : (
            <div className="rounded border border-red-900/50 bg-red-950/30 px-3 py-2 text-xs text-red-200/90">
              {genResult.message}
            </div>
          )
        ) : null}
      </form>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter by name, description, category…"
          className="w-full rounded-lg border border-slate-700 bg-slate-900/80 pl-10 pr-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
        />
      </div>

      {scriptlets.length === 0 ? (
        <p className="text-slate-500">No scriptlets listed. Start the bridge and ensure the depot is configured.</p>
      ) : grouped.length === 0 ? (
        <p className="text-slate-500">No matches for this filter.</p>
      ) : (
        <div className="space-y-8">
          {grouped.map(([category, items]) => (
            <section key={category} className="space-y-3">
              <div className="flex items-baseline gap-3 border-b border-slate-800 pb-2">
                <h2 className="text-lg font-semibold text-amber-400 capitalize">{category}</h2>
                <span className="text-xs text-slate-500">{items.length} scriptlet{items.length === 1 ? "" : "s"}</span>
              </div>
              <ul className="grid gap-2 sm:grid-cols-1 lg:grid-cols-2">
                {items.map((s, i) => (
                  <li
                    key={`${s.id ?? s.name ?? i}`}
                    className="rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-slate-300"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-amber-400">{s.name ?? s.id ?? "—"}</span>
                      {s.running ? (
                        <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                          running
                        </span>
                      ) : null}
                    </div>
                    {s.description ? (
                      <p className="mt-1 text-sm text-slate-400 line-clamp-3">{String(s.description)}</p>
                    ) : null}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
