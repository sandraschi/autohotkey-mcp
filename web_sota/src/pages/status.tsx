import { useState, useEffect } from "react";
import { Activity } from "lucide-react";

interface StatusData {
  ok?: boolean;
  service?: string;
  port?: number;
  scriptlets?: unknown[];
}

export function Status() {
  const [data, setData] = useState<StatusData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/health")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("Health failed"))))
      .then((health) => {
        setData({
          ok: health.ok,
          service: health.service,
          port: health.port,
        });
        setError(null);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Backend unreachable");
        setData(null);
      });
  }, []);

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Activity className="h-7 w-7 text-amber-500" />
          Status
        </h1>
        <p className="text-amber-400">Backend unreachable. Run web_sota/start.ps1.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <Activity className="h-7 w-7 text-amber-500" />
        Status
      </h1>
      <p className="text-slate-400">Backend health (autohotkey-mcp on port 10746).</p>

      {data && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            <span className="text-emerald-400 font-medium">Online</span>
          </div>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
            <dt className="text-slate-500">Service</dt>
            <dd className="text-slate-300">{data.service ?? "autohotkey-mcp"}</dd>
            <dt className="text-slate-500">Port</dt>
            <dd className="text-slate-300">{data.port ?? 10746}</dd>
          </dl>
        </div>
      )}
    </div>
  );
}
