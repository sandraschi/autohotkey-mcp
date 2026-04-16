import { useCallback, useEffect, useState } from "react";
import { Layers, Loader2, RefreshCw, Skull } from "lucide-react";

interface RunningRow {
  script_id: string;
  name?: string;
  description?: string;
  hotkeys?: string;
  category?: string;
  pid: number | null;
  source: string;
}

interface RunningPayload {
  instances?: RunningRow[];
  direct_tracked?: number;
  bridge_url?: string;
}

export function Running() {
  const [data, setData] = useState<RunningPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [killing, setKilling] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    fetch("/api/running")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((j: RunningPayload) => {
        setData(j);
        setError(null);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Failed to load");
        setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    const t = window.setInterval(load, 8000);
    return () => window.clearInterval(t);
  }, [load]);

  const kill = async (row: RunningRow) => {
    const key = `${row.script_id}:${row.pid ?? "bridge"}`;
    setKilling(key);
    try {
      const body: Record<string, string | number> = { script_id: row.script_id };
      if (row.source === "direct" && row.pid != null) {
        body.pid = row.pid;
      }
      const r = await fetch("/api/stop_scriptlet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const j = (await r.json()) as { success?: boolean; error?: string };
      if (!r.ok || j.success === false) {
        setError(j.error ?? r.statusText ?? "Stop failed");
      } else {
        setError(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Stop failed");
    } finally {
      setKilling(null);
      load();
    }
  };

  const instances = data?.instances ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Layers className="h-7 w-7 text-amber-500" />
            Running
          </h1>
          <p className="text-slate-400 mt-1 text-sm max-w-3xl">
            Scriptlets reported as running by the COM bridge (if up) plus processes started via MCP{" "}
            <strong className="text-slate-300">direct run</strong> (tracked by PID). Metadata (
            <code className="text-slate-500">@hotkeys</code>, <code className="text-slate-500">@description</code>) comes
            from the depot file headers. Use <strong className="text-slate-300">Kill</strong> to stop — for direct runs
            with a PID, that instance is targeted; bridge rows stop via the bridge.
          </p>
        </div>
        <button
          type="button"
          onClick={() => load()}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          Refresh
        </button>
      </div>

      {error ? (
        <p className="text-red-400 text-sm rounded border border-red-900/50 bg-red-950/30 px-3 py-2">{error}</p>
      ) : null}

      {data && typeof data.direct_tracked === "number" ? (
        <p className="text-xs text-slate-500">
          Direct PID rows tracked: {data.direct_tracked}
          {data.bridge_url ? (
            <>
              {" "}
              · Bridge: <code className="text-slate-600">{data.bridge_url}</code>
            </>
          ) : null}
        </p>
      ) : null}

      {loading && !data ? (
        <p className="text-slate-500 flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading…
        </p>
      ) : instances.length === 0 ? (
        <p className="text-slate-500">No running scriptlets. Start one from Scriptlets or the MCP tool run_scriptlet.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-900/80 text-slate-400 text-xs uppercase tracking-wide">
              <tr>
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Script</th>
                <th className="px-3 py-2">Hotkeys</th>
                <th className="px-3 py-2">Description</th>
                <th className="px-3 py-2">PID</th>
                <th className="px-3 py-2">Source</th>
                <th className="px-3 py-2 w-28"> </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {instances.map((row, idx) => {
                const key = `${row.script_id}-${row.pid ?? "b"}-${idx}`;
                const killKey = `${row.script_id}:${row.pid ?? "bridge"}`;
                return (
                  <tr key={key} className="bg-slate-950/40 hover:bg-slate-900/60">
                    <td className="px-3 py-2 text-slate-200 font-medium">{row.name ?? "—"}</td>
                    <td className="px-3 py-2 font-mono text-amber-400/90">{row.script_id}</td>
                    <td className="px-3 py-2 text-slate-400 max-w-[12rem] whitespace-pre-wrap">
                      {row.hotkeys || "—"}
                    </td>
                    <td className="px-3 py-2 text-slate-400 max-w-xl line-clamp-3">{row.description || "—"}</td>
                    <td className="px-3 py-2 font-mono text-slate-500">{row.pid ?? "—"}</td>
                    <td className="px-3 py-2 text-slate-500">{row.source}</td>
                    <td className="px-3 py-2">
                      <button
                        type="button"
                        disabled={killing === killKey}
                        onClick={() => void kill(row)}
                        className="inline-flex items-center gap-1 rounded-md bg-red-950/80 hover:bg-red-900 border border-red-900/60 text-red-200 text-xs px-2 py-1.5 disabled:opacity-50"
                      >
                        {killing === killKey ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <Skull className="h-3 w-3" />
                        )}
                        Kill
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
