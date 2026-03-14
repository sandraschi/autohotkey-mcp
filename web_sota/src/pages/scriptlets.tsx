import { useState, useEffect } from "react";
import { FileCode } from "lucide-react";

interface ScriptletInfo {
  name?: string;
  id?: string;
  description?: string;
  [key: string]: unknown;
}

export function Scriptlets() {
  const [scriptlets, setScriptlets] = useState<ScriptletInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/scriptlets")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("Failed to load scriptlets"))))
      .then((data) => setScriptlets(Array.isArray(data.scriptlets) ? data.scriptlets : []))
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Unknown error");
        setScriptlets([]);
      });
  }, []);

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileCode className="h-7 w-7 text-amber-500" />
          Scriptlets
        </h1>
        <p className="text-amber-400">Backend unreachable or no scriptlets. Ensure bridge (10744) and backend are running.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <FileCode className="h-7 w-7 text-amber-500" />
        Scriptlets
      </h1>
      <p className="text-slate-400">Scriptlets available from the depot (ScriptletCOMBridge).</p>

      {scriptlets.length === 0 ? (
        <p className="text-slate-500">No scriptlets listed. Start the bridge and ensure the depot is configured.</p>
      ) : (
        <ul className="space-y-2">
          {scriptlets.map((s, i) => (
            <li
              key={s.id ?? s.name ?? i}
              className="rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-slate-300"
            >
              <span className="font-mono text-amber-400">{s.name ?? s.id ?? "—"}</span>
              {s.description && <span className="ml-2 text-slate-400">{s.description}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
