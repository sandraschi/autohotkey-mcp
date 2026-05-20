import { useState, useEffect } from "react";
import { HelpCircle, ChevronDown, ChevronUp } from "lucide-react";

const LEVEL_ORDER = ["quick", "reference", "language", "usage", "tools", "mcp_server"];
const LEVEL_LABELS: Record<string, string> = {
  quick: "Quick Start",
  reference: "Reference",
  language: "Language",
  usage: "Authoring Guide",
  tools: "Tools",
  mcp_server: "Server Config",
};

// ── Markdown renderer ──────────────────────────────────────────────────────────
// Handles: fenced code blocks, tables, h1/h2/h3, bold, inline code, hr, lists

function mdToHtml(md: string): string {
  const esc = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  // 1. Extract fenced code blocks, replace with placeholders
  const blocks: string[] = [];
  let out = md.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const idx = blocks.length;
    const langLabel = lang ? `<span class="text-xs text-slate-500 font-mono float-right">${esc(lang)}</span>` : "";
    blocks.push(
      `<div class="relative my-4">${langLabel}<pre class="bg-slate-950 border border-slate-800 rounded-lg p-4 overflow-x-auto text-sm font-mono text-slate-300 clear-both"><code>${esc(code.trimEnd())}</code></pre></div>`
    );
    return `\x00BLOCK${idx}\x00`;
  });

  // 2. Split into lines and process non-code content
  const lines = out.split("\n");
  const result: string[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Restore code block placeholder
    if (/^\x00BLOCK\d+\x00$/.test(line.trim())) {
      const idx = parseInt(line.trim().replace(/\x00BLOCK(\d+)\x00/, "$1"));
      result.push(blocks[idx]);
      i++;
      continue;
    }

    // Table: detect header row (| ... |)
    if (/^\|.+\|$/.test(line.trim()) && i + 1 < lines.length && /^\|[\s:-]+\|$/.test(lines[i + 1]?.trim() ?? "")) {
      const tableLines: string[] = [];
      while (i < lines.length && /^\|.+\|$/.test(lines[i].trim())) {
        tableLines.push(lines[i]);
        i++;
      }
      const [headerRow, , ...bodyRows] = tableLines;
      const headers = headerRow.split("|").slice(1, -1).map((c) => c.trim());
      const body = bodyRows.map((r) => r.split("|").slice(1, -1).map((c) => c.trim()));
      const thCells = headers.map((h) => `<th class="px-4 py-2 text-left text-slate-300 font-semibold border-b border-slate-700 whitespace-nowrap">${inlineFormat(esc(h))}</th>`).join("");
      const trs = body.map((row) =>
        `<tr class="border-b border-slate-800 hover:bg-slate-800/40">${row.map((c) => `<td class="px-4 py-2 text-slate-400 align-top">${inlineFormat(esc(c))}</td>`).join("")}</tr>`
      ).join("");
      result.push(`<div class="overflow-x-auto my-4"><table class="w-full text-sm border-collapse border border-slate-800 rounded-lg overflow-hidden"><thead class="bg-slate-900"><tr>${thCells}</tr></thead><tbody>${trs}</tbody></table></div>`);
      continue;
    }

    // HR
    if (/^---+$/.test(line.trim())) {
      result.push(`<hr class="border-slate-800 my-6" />`);
      i++;
      continue;
    }

    // Headings
    const h1 = line.match(/^# (.+)/);
    if (h1) { result.push(`<h1 class="text-2xl font-bold text-white mt-8 mb-3">${inlineFormat(esc(h1[1]))}</h1>`); i++; continue; }
    const h2 = line.match(/^## (.+)/);
    if (h2) { result.push(`<h2 class="text-xl font-semibold text-slate-100 mt-6 mb-2 pb-1 border-b border-slate-800">${inlineFormat(esc(h2[1]))}</h2>`); i++; continue; }
    const h3 = line.match(/^### (.+)/);
    if (h3) { result.push(`<h3 class="text-base font-semibold text-amber-400 mt-4 mb-1">${inlineFormat(esc(h3[1]))}</h3>`); i++; continue; }

    // Unordered list item
    const li = line.match(/^[-*] (.+)/);
    if (li) {
      const items: string[] = [];
      let j = i;
      while (j < lines.length && /^[-*] /.test(lines[j])) {
        const m = lines[j].match(/^[-*] (.+)/);
        if (m) items.push(`<li class="ml-4 text-slate-400 text-sm leading-relaxed">${inlineFormat(esc(m[1]))}</li>`);
        j++;
      }
      result.push(`<ul class="list-disc list-inside space-y-1 my-2">${items.join("")}</ul>`);
      i = j;
      continue;
    }

    // Blank line
    if (line.trim() === "") {
      result.push(`<div class="h-2"></div>`);
      i++;
      continue;
    }

    // Regular paragraph line
    result.push(`<p class="text-slate-400 text-sm leading-relaxed">${inlineFormat(esc(line))}</p>`);
    i++;
  }

  return result.join("\n");
}

function inlineFormat(s: string): string {
  return s
    .replace(/`([^`]+)`/g, `<code class="bg-slate-800 text-amber-300 px-1.5 py-0.5 rounded text-xs font-mono">$1</code>`)
    .replace(/\*\*(.+?)\*\*/g, `<strong class="text-slate-200 font-semibold">$1</strong>`)
    .replace(/\*(.+?)\*/g, `<em class="text-slate-300">$1</em>`);
}

// ── Section collapse ───────────────────────────────────────────────────────────

function CollapsibleSection({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden mb-3">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-left text-sm font-semibold text-slate-200 transition-colors"
      >
        {title}
        {open ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
      </button>
      {open && <div className="px-4 py-3 bg-slate-950/40">{children}</div>}
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export function Help() {
  const [levels, setLevels] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState("quick");

  useEffect(() => {
    fetch("/api/help")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((data) => {
        setLevels(data.levels ?? {});
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, []);

  if (error) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <HelpCircle className="h-7 w-7 text-amber-500" />
          Help
        </h1>
        <div className="rounded-lg border border-amber-900/40 bg-amber-950/20 px-4 py-3 text-sm text-amber-300">
          Backend unreachable: {error}. Start the server with{" "}
          <code className="text-amber-200 font-mono text-xs">web_sota\\start.ps1</code>
        </div>
      </div>
    );
  }

  if (!levels) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <HelpCircle className="h-7 w-7 text-amber-500" />
          Help
        </h1>
        <p className="text-slate-500 text-sm animate-pulse">Loading documentation…</p>
      </div>
    );
  }

  const tabs = LEVEL_ORDER.filter((k) => k in levels);
  const content = levels[active] ?? "";

  return (
    <div className="space-y-4 max-w-5xl">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <HelpCircle className="h-7 w-7 text-amber-500" />
            Help &amp; Documentation
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            AutoHotkey v2 reference · MCP tool docs · Server configuration
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-600">
          <span>{tabs.length} sections</span>
          <span>·</span>
          <span>{content.split("\n").length} lines</span>
          <span>·</span>
          <span>{(content.length / 1024).toFixed(0)} KB</span>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex flex-wrap gap-1.5 border-b border-slate-800 pb-3">
        {tabs.map((key) => (
          <button
            key={key}
            type="button"
            onClick={() => setActive(key)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              active === key
                ? "bg-amber-600 text-white"
                : "text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-800"
            }`}
          >
            {LEVEL_LABELS[key] ?? key.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Content */}
      <div
        className="text-slate-300 leading-relaxed"
        /* biome-ignore lint/security/noDangerouslySetInnerHtml: intentional markdown rendering */
        dangerouslySetInnerHTML={{ __html: mdToHtml(content) }}
      />
    </div>
  );
}
