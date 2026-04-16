import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bot, Loader2, MessageSquare, Send, Sparkles, Wand2 } from "lucide-react";

interface Persona {
  id: string;
  name: string;
  description: string;
}

interface PresetPrompt {
  id: string;
  title: string;
  category?: string;
  prompt: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function Chat() {
  const navigate = useNavigate();
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [personaId, setPersonaId] = useState<string>("ahk_expert");
  const [prompts, setPrompts] = useState<PresetPrompt[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [catFilter, setCatFilter] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [refineRough, setRefineRough] = useState("");
  const [refineLoading, setRefineLoading] = useState(false);
  const [refineOut, setRefineOut] = useState<string | null>(null);
  const [streamEnabled, setStreamEnabled] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/personas")
      .then((r) => r.json())
      .then((d) => setPersonas(Array.isArray(d.personas) ? d.personas : []))
      .catch(() => setPersonas([]));
  }, []);

  const loadPrompts = useCallback(() => {
    const q = catFilter ? `?category=${encodeURIComponent(catFilter)}` : "";
    fetch(`/api/prompts${q}`)
      .then((r) => r.json())
      .then((d) => {
        setPrompts(Array.isArray(d.prompts) ? d.prompts : []);
        setCategories(Array.isArray(d.categories) ? d.categories : []);
      })
      .catch(() => {
        setPrompts([]);
        setCategories([]);
      });
  }, [catFilter]);

  useEffect(() => {
    loadPrompts();
  }, [loadPrompts]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    const next: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setInput("");
    setLoading(true);
    try {
      const payload = {
        messages: next.map((m) => ({ role: m.role, content: m.content })),
        persona_id: personaId,
        stream: streamEnabled,
      };
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (streamEnabled && r.ok) {
        const ct = r.headers.get("content-type") || "";
        if (ct.includes("text/event-stream") && r.body) {
          const reader = r.body.getReader();
          const dec = new TextDecoder();
          let buffer = "";
          let acc = "";
          setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += dec.decode(value, { stream: true });
            for (;;) {
              const split = buffer.indexOf("\n\n");
              if (split === -1) break;
              const block = buffer.slice(0, split).trim();
              buffer = buffer.slice(split + 2);
              if (!block.startsWith("data: ")) continue;
              const raw = block.slice(6).trim();
              if (raw === "[DONE]") continue;
              try {
                const j = JSON.parse(raw) as { c?: string; error?: string };
                if (j.error) acc = `[Error] ${j.error}`;
                else if (j.c) acc += j.c;
                setMessages((prev) => [...prev.slice(0, -1), { role: "assistant", content: acc }]);
              } catch {
                /* ignore malformed chunk */
              }
            }
          }
          return;
        }
      }
      if (!r.ok) {
        const errData = (await r.json().catch(() => ({}))) as { error?: string };
        setMessages([
          ...next,
          {
            role: "assistant",
            content: `[Error] ${errData.error ?? r.statusText ?? "request failed"}`,
          },
        ]);
        setLoading(false);
        return;
      }
      const data = (await r.json()) as { success?: boolean; message?: string; error?: string };
      if (data.success && typeof data.message === "string") {
        setMessages([...next, { role: "assistant", content: data.message }]);
      } else {
        setMessages([
          ...next,
          {
            role: "assistant",
            content: `[Error] ${data.error ?? "request failed"}`,
          },
        ]);
      }
    } catch (e) {
      setMessages([
        ...next,
        {
          role: "assistant",
          content: `[Error] ${e instanceof Error ? e.message : "network"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (p: PresetPrompt) => {
    setInput((prev) => (prev ? `${prev}\n\n${p.prompt}` : p.prompt));
  };

  const runRefine = async () => {
    const rough = refineRough.trim();
    if (rough.length < 3 || refineLoading) return;
    setRefineLoading(true);
    setRefineOut(null);
    try {
      const r = await fetch("/api/refine_prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rough, persona_id: personaId }),
      });
      const data = (await r.json()) as { success?: boolean; refined_prompt?: string; error?: string };
      if (data.success && typeof data.refined_prompt === "string") {
        setRefineOut(data.refined_prompt);
      } else {
        setRefineOut(data.error ?? "Refine failed");
      }
    } catch (e) {
      setRefineOut(e instanceof Error ? e.message : "network error");
    } finally {
      setRefineLoading(false);
    }
  };

  const sendToScriptlets = () => {
    const t = refineOut?.trim() || "";
    if (t.length < 3) return;
    navigate("/scriptlets", { state: { prefilledPrompt: t } });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <MessageSquare className="h-7 w-7 text-amber-500" />
          Chat
        </h1>
        <p className="text-slate-400 mt-1 text-sm max-w-3xl">
          Local <strong className="text-slate-300">Ollama / LM Studio</strong> via{" "}
          <code className="text-slate-500">AUTOHOTKEY_LLM_*</code>. This page does not use MCP sampling (browsers
          cannot). For <strong className="text-slate-300">FastMCP sampling</strong> as the primary path, use{" "}
          <code className="text-slate-500">generate_scriptlet</code> / <code className="text-slate-500">refine_ahk_prompt</code>{" "}
          from your MCP client (e.g. Cursor).
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="flex flex-col rounded-lg border border-slate-800 bg-slate-900/40 min-h-[420px]">
          <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 px-3 py-2">
            <label className="text-xs text-slate-500">Persona</label>
            <select
              value={personaId}
              onChange={(e) => setPersonaId(e.target.value)}
              className="rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-200"
            >
              {personas.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-1.5 text-xs text-slate-400 cursor-pointer ml-2">
              <input
                type="checkbox"
                checked={streamEnabled}
                onChange={(e) => setStreamEnabled(e.target.checked)}
                className="rounded border-slate-600"
              />
              Stream (SSE)
            </label>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3 text-sm">
            {messages.length === 0 ? (
              <p className="text-slate-500 flex items-center gap-2">
                <Bot className="h-4 w-4" /> Ask about AutoHotkey v2, paste an error, or request a snippet.
              </p>
            ) : (
              messages.map((m, i) => (
                <div
                  key={`${i}-${m.role}`}
                  className={
                    m.role === "user"
                      ? "ml-8 rounded-lg bg-amber-950/40 border border-amber-900/30 px-3 py-2 text-slate-200"
                      : "mr-8 rounded-lg bg-slate-800/80 border border-slate-700 px-3 py-2 text-slate-300 whitespace-pre-wrap"
                  }
                >
                  {m.content}
                </div>
              ))
            )}
            {loading ? (
              <div className="flex items-center gap-2 text-slate-500 text-xs">
                <Loader2 className="h-4 w-4 animate-spin" /> Thinking…
              </div>
            ) : null}
            <div ref={bottomRef} />
          </div>
          <div className="border-t border-slate-800 p-3 flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void send();
                }
              }}
              rows={2}
              placeholder="Message… (Enter send, Shift+Enter newline)"
              className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200"
            />
            <button
              type="button"
              onClick={() => void send()}
              disabled={loading}
              className="shrink-0 self-end rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white px-3 py-2"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>

        <aside className="space-y-4">
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
            <h2 className="text-sm font-semibold text-amber-400/90 flex items-center gap-2 mb-2">
              <Wand2 className="h-4 w-4" /> Refine for generation
            </h2>
            <p className="text-[11px] text-slate-500 mb-2">
              Sharpen a vague idea into a prompt you can paste into Scriptlets → Generate.
            </p>
            <textarea
              value={refineRough}
              onChange={(e) => setRefineRough(e.target.value)}
              rows={4}
              placeholder="Rough idea…"
              className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-200 mb-2"
            />
            <button
              type="button"
              onClick={() => void runRefine()}
              disabled={refineLoading}
              className="w-full rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs py-2 flex items-center justify-center gap-2"
            >
              {refineLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
              Refine
            </button>
            {refineOut ? (
              <div className="mt-2 rounded border border-emerald-900/40 bg-emerald-950/20 p-2 text-xs text-emerald-100/90 whitespace-pre-wrap">
                {refineOut}
                <button
                  type="button"
                  onClick={sendToScriptlets}
                  className="mt-2 w-full rounded bg-emerald-800/80 hover:bg-emerald-700 text-white py-1.5 text-[11px]"
                >
                  Use in Scriptlets → Generate
                </button>
              </div>
            ) : null}
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
            <h2 className="text-sm font-semibold text-amber-400/90 mb-2">Preset prompts</h2>
            <select
              value={catFilter}
              onChange={(e) => setCatFilter(e.target.value)}
              className="w-full rounded border border-slate-700 bg-slate-950 text-xs text-slate-200 px-2 py-1 mb-2"
            >
              <option value="">All categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <ul className="max-h-52 overflow-y-auto space-y-1 text-xs">
              {prompts.map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    onClick={() => applyPreset(p)}
                    className="w-full text-left rounded px-2 py-1.5 text-slate-300 hover:bg-slate-800 border border-transparent hover:border-slate-700"
                  >
                    <span className="text-amber-500/90">{p.title}</span>
                    {p.category ? (
                      <span className="text-slate-600 ml-1">· {p.category}</span>
                    ) : null}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}
