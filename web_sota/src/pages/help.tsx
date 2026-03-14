import { useState, useEffect } from "react";
import { HelpCircle } from "lucide-react";

const LEVEL_ORDER = ["quick", "reference", "language", "usage", "tools", "mcp_server"];

function mdToHtml(md: string): string {
  const escape = (s: string) =>
    s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  let out = md;
  out = out.replace(/```[\s\S]*?```/g, (m) => `<pre class="bg-slate-800 p-3 rounded overflow-x-auto my-2"><code>${escape(m.replace(/^```\w*\n?|```$/g, ""))}</code></pre>`);
  out = escape(out);
  out = out.replace(/^### (.+)$/gm, "<h3 class='text-lg font-semibold text-slate-200 mt-4'>$1</h3>");
  out = out.replace(/^## (.+)$/gm, "<h2 class='text-xl font-semibold text-slate-100 mt-6'>$1</h2>");
  out = out.replace(/\*\*(.+?)\*\*/g, "<strong class='text-slate-200'>$1</strong>");
  out = out.replace(/\n/g, "<br/>");
  return out;
}

export function Help() {
  const [levels, setLevels] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState("quick");

  useEffect(() => {
    fetch("/api/help")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("Failed to load help"))))
      .then((data) => {
        setLevels(data.levels ?? {});
        if (Object.keys(data.levels ?? {}).length) setActive(Object.keys(data.levels)[0]);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, []);

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <HelpCircle className="h-7 w-7 text-amber-500" />
          Help
        </h1>
        <p className="text-amber-400">Backend unreachable. Start the server with web_sota/start.ps1.</p>
      </div>
    );
  }

  if (!levels) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white">Help</h1>
        <p className="text-slate-400">Loading…</p>
      </div>
    );
  }

  const tabs = LEVEL_ORDER.filter((k) => k in levels);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <HelpCircle className="h-7 w-7 text-amber-500" />
        Help &amp; Documentation
      </h1>
      <p className="text-slate-400">Multilevel AHK and MCP server docs.</p>

      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {tabs.map((key) => (
          <button
            key={key}
            type="button"
            onClick={() => setActive(key)}
            className={`rounded px-3 py-1.5 text-sm font-medium transition-colors ${
              active === key ? "bg-slate-700 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            }`}
          >
            {key.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      <div
        className="prose prose-invert max-w-none text-slate-300 text-sm"
        dangerouslySetInnerHTML={{ __html: mdToHtml(levels[active] ?? "") }}
      />
    </div>
  );
}
