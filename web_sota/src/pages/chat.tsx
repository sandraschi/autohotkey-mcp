import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  Bot, Loader2, MessageSquare, Send, Sparkles, Wand2,
  Settings2, ChevronDown, Trash2, Copy, Check,
} from "lucide-react";
import { cn } from "@/common/utils";

// ── Types ──────────────────────────────────────────────────────────────────────

interface Persona { id: string; name: string; description: string; }
interface PresetPrompt { id: string; title: string; category?: string; prompt: string; }
interface ChatMessage { role: "user" | "assistant"; content: string; }
interface LLMSettings { base_url: string; model: string; provider: string; api_key_set: boolean; }

// ── CopyButton ─────────────────────────────────────────────────────────────────

function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      onClick={async () => { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
      className="p-1 rounded text-slate-600 hover:text-slate-300 transition-colors"
      title="Copy"
    >
      {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
    </button>
  );
}

// ── Message bubble ─────────────────────────────────────────────────────────────

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={cn("flex gap-2 group", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="h-7 w-7 rounded-full bg-amber-600/20 border border-amber-700/40 flex items-center justify-center shrink-0 mt-0.5">
          <Bot className="h-3.5 w-3.5 text-amber-400" />
        </div>
      )}
      <div className={cn(
        "relative max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-wrap",
        isUser
          ? "bg-amber-700/30 border border-amber-700/40 text-slate-100"
          : "bg-slate-800/80 border border-slate-700/60 text-slate-300"
      )}>
        {msg.content}
        <span className="absolute top-1.5 right-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <CopyBtn text={msg.content} />
        </span>
      </div>
    </div>
  );
}

// ── Model badge ────────────────────────────────────────────────────────────────

function ModelBadge({ model, provider }: { model: string; provider: string }) {
  const label = model.length > 24 ? `…${model.slice(-22)}` : model;
  return (
    <Link
      to="/settings"
      className="inline-flex items-center gap-1 rounded border border-slate-700 bg-slate-900 px-2 py-0.5 text-[11px] text-slate-400 hover:text-amber-300 hover:border-amber-700/40 transition-colors"
      title={`${provider}: ${model} — click to change in Settings`}
    >
      <span className="text-slate-600">{provider}</span>
      <span>/</span>
      <span className="font-mono">{label}</span>
      <Settings2 className="h-3 w-3 ml-0.5" />
    </Link>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export function Chat() {
  const navigate = useNavigate();

  // LLM settings
  const [llmSettings, setLlmSettings] = useState<LLMSettings | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [showModelPicker, setShowModelPicker] = useState(false);
  const [switchingModel, setSwitchingModel] = useState(false);

  // Chat state
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [personaId, setPersonaId] = useState<string>("ahk_expert");
  const [prompts, setPrompts] = useState<PresetPrompt[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [catFilter, setCatFilter] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamEnabled, setStreamEnabled] = useState(true);
  const [llmError, setLlmError] = useState<string | null>(null);

  // Refine state
  const [refineRough, setRefineRough] = useState("");
  const [refineLoading, setRefineLoading] = useState(false);
  const [refineOut, setRefineOut] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ── Load on mount ────────────────────────────────────────────────────────────

  useEffect(() => {
    fetch("/api/llm/settings")
      .then((r) => r.json() as Promise<LLMSettings>)
      .then(setLlmSettings)
      .catch(() => null);

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
      .catch(() => { setPrompts([]); setCategories([]); });
  }, [catFilter]);

  useEffect(() => { loadPrompts(); }, [loadPrompts]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  // ── Fetch available models for inline picker ────────────────────────────────

  const fetchModels = async () => {
    try {
      const r = await fetch("/api/llm/models");
      const d = await r.json() as { models: string[] };
      setAvailableModels(d.models ?? []);
    } catch { setAvailableModels([]); }
  };

  const openModelPicker = () => {
    if (availableModels.length === 0) void fetchModels();
    setShowModelPicker((v) => !v);
  };

  // ── Switch model without navigating away ────────────────────────────────────

  const switchModel = async (m: string) => {
    setSwitchingModel(true);
    try {
      await fetch("/api/llm/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: m }),
      });
      setLlmSettings((s) => s ? { ...s, model: m } : s);
    } finally {
      setSwitchingModel(false);
      setShowModelPicker(false);
    }
  };

  // ── Send ─────────────────────────────────────────────────────────────────────

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    const next: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setInput("");
    setLlmError(null);
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
      // Handle 503 LLM not configured
      if (r.status === 503) {
        const d = await r.json() as { error?: string };
        setLlmError(d.error ?? "LLM not configured");
        setMessages(next);
        return;
      }
      if (streamEnabled && r.ok && r.headers.get("content-type")?.includes("text/event-stream") && r.body) {
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
              if (j.error) { acc = `[Error] ${j.error}`; setLlmError(j.error); }
              else if (j.c) acc += j.c;
              setMessages((prev) => [...prev.slice(0, -1), { role: "assistant", content: acc }]);
            } catch { /* ignore malformed chunk */ }
          }
        }
        return;
      }
      if (!r.ok) {
        const errData = await r.json().catch(() => ({})) as { error?: string };
        const msg = errData.error ?? r.statusText ?? "request failed";
        setLlmError(msg);
        setMessages([...next, { role: "assistant", content: `[Error] ${msg}` }]);
        return;
      }
      const data = await r.json() as { success?: boolean; message?: string; error?: string };
      if (data.success && typeof data.message === "string") {
        setMessages([...next, { role: "assistant", content: data.message }]);
      } else {
        const msg = data.error ?? "request failed";
        setLlmError(msg);
        setMessages([...next, { role: "assistant", content: `[Error] ${msg}` }]);
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "network error";
      setLlmError(msg);
      setMessages([...next, { role: "assistant", content: `[Error] ${msg}` }]);
    } finally {
      setLoading(false);
    }
  };

  // ── Refine ───────────────────────────────────────────────────────────────────

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
      const data = await r.json() as { success?: boolean; refined_prompt?: string; error?: string };
      setRefineOut(data.success && typeof data.refined_prompt === "string"
        ? data.refined_prompt
        : (data.error ?? "Refine failed"));
    } catch (e) {
      setRefineOut(e instanceof Error ? e.message : "network error");
    } finally {
      setRefineLoading(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <MessageSquare className="h-7 w-7 text-amber-500" />
            Chat
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Local LLM via Ollama / LM Studio.{" "}
            <Link to="/settings" className="text-amber-500/80 hover:text-amber-400">Configure in Settings →</Link>
          </p>
        </div>
        {llmSettings && (
          <div className="relative">
            <button
              type="button"
              onClick={openModelPicker}
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
            >
              {switchingModel
                ? <Loader2 className="h-4 w-4 animate-spin" />
                : <span className="text-slate-500 text-xs">{llmSettings.provider}/</span>}
              <span className="font-mono text-sm max-w-[180px] truncate">{llmSettings.model}</span>
              <ChevronDown className="h-4 w-4 text-slate-500" />
            </button>
            {showModelPicker && (
              <div className="absolute right-0 top-full mt-1 z-50 w-72 rounded-lg border border-slate-700 bg-slate-900 shadow-xl">
                <div className="px-3 py-2 border-b border-slate-800 text-xs text-slate-500 flex items-center justify-between">
                  <span>Switch model</span>
                  <Link to="/settings" className="text-amber-500/80 hover:text-amber-400 flex items-center gap-1">
                    <Settings2 className="h-3 w-3" /> Full settings
                  </Link>
                </div>
                {availableModels.length > 0 ? (
                  <ul className="max-h-60 overflow-y-auto py-1">
                    {availableModels.map((m) => (
                      <li key={m}>
                        <button
                          type="button"
                          onClick={() => void switchModel(m)}
                          className={cn(
                            "w-full text-left px-3 py-2 text-sm font-mono hover:bg-slate-800 transition-colors",
                            m === llmSettings.model ? "text-amber-300" : "text-slate-300"
                          )}
                        >
                          {m === llmSettings.model && <span className="mr-2 text-amber-400">✓</span>}
                          {m}
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="px-3 py-3 text-xs text-slate-500">
                    <Loader2 className="h-3.5 w-3.5 animate-spin inline mr-1.5" />
                    Fetching models from {llmSettings.base_url}…
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* LLM error banner */}
      {llmError && (
        <div className="rounded-lg border border-red-900/40 bg-red-950/20 px-4 py-3 text-sm text-red-300 flex items-start justify-between gap-3">
          <span>{llmError}</span>
          <Link to="/settings" className="shrink-0 text-red-400 hover:text-red-200 flex items-center gap-1 text-xs">
            <Settings2 className="h-3.5 w-3.5" /> Configure LLM
          </Link>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_272px]">
        {/* ── Chat panel ─────────────────────────────────────────────────── */}
        <div className="flex flex-col rounded-xl border border-slate-800 bg-slate-900/40 min-h-[500px]">
          {/* Toolbar */}
          <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 px-3 py-2">
            <select
              value={personaId}
              onChange={(e) => setPersonaId(e.target.value)}
              className="rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200"
            >
              {personas.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <label className="flex items-center gap-1.5 text-xs text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={streamEnabled}
                onChange={(e) => setStreamEnabled(e.target.checked)}
                className="rounded border-slate-600"
              />
              Stream
            </label>
            <div className="flex-1" />
            {llmSettings && (
              <ModelBadge model={llmSettings.model} provider={llmSettings.provider} />
            )}
            {messages.length > 0 && (
              <button
                type="button"
                onClick={() => { setMessages([]); setLlmError(null); }}
                className="p-1 rounded text-slate-600 hover:text-red-400 transition-colors"
                title="Clear conversation"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full py-12 text-center space-y-3">
                <Bot className="h-10 w-10 text-slate-700" />
                <p className="text-slate-500 text-sm max-w-xs">
                  Ask about AutoHotkey v2, paste an error, or request a snippet.
                </p>
                {llmSettings && (
                  <p className="text-xs text-slate-600">
                    Using <span className="font-mono text-slate-500">{llmSettings.model}</span>
                    {" "}via <span className="text-slate-500">{llmSettings.base_url}</span>
                  </p>
                )}
              </div>
            ) : (
              messages.map((m, i) => <MessageBubble key={`${i}-${m.role}`} msg={m} />)
            )}
            {loading && !messages[messages.length - 1]?.content && (
              <div className="flex items-center gap-2 text-slate-500 text-xs pl-9">
                <Loader2 className="h-4 w-4 animate-spin" /> Thinking…
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-800 p-3 flex gap-2 items-end">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void send(); }
              }}
              rows={2}
              placeholder="Message… (Enter to send, Shift+Enter for newline)"
              className="flex-1 resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/30"
            />
            <button
              type="button"
              onClick={() => void send()}
              disabled={loading || !input.trim()}
              className="shrink-0 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white p-2.5 transition-colors"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* ── Sidebar ────────────────────────────────────────────────────── */}
        <aside className="space-y-3">
          {/* Refine */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-3 space-y-2">
            <h2 className="text-sm font-semibold text-amber-400/90 flex items-center gap-2">
              <Wand2 className="h-4 w-4" /> Refine idea
            </h2>
            <p className="text-[11px] text-slate-500">
              Turn a vague idea into a precise AHK prompt for generation.
            </p>
            <textarea
              value={refineRough}
              onChange={(e) => setRefineRough(e.target.value)}
              rows={3}
              placeholder="e.g. make a thing that keeps screen awake…"
              className="w-full resize-none rounded border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-amber-500/30"
            />
            <button
              type="button"
              onClick={() => void runRefine()}
              disabled={refineLoading || refineRough.trim().length < 3}
              className="w-full rounded-md bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 text-xs py-2 flex items-center justify-center gap-2 transition-colors"
            >
              {refineLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
              Refine
            </button>
            {refineOut && (
              <div className="rounded border border-emerald-900/40 bg-emerald-950/20 p-2 text-xs text-emerald-100/90 whitespace-pre-wrap space-y-2">
                <div className="flex items-start justify-between gap-1">
                  <span className="leading-relaxed">{refineOut}</span>
                  <CopyBtn text={refineOut} />
                </div>
                <button
                  type="button"
                  onClick={() => navigate("/scriptlets", { state: { prefilledPrompt: refineOut } })}
                  className="w-full rounded bg-emerald-800/80 hover:bg-emerald-700 text-white py-1.5 text-[11px] transition-colors"
                >
                  Use in Scriptlets → Generate
                </button>
              </div>
            )}
          </div>

          {/* Preset prompts */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-3 space-y-2">
            <h2 className="text-sm font-semibold text-amber-400/90">Preset prompts</h2>
            <select
              value={catFilter}
              onChange={(e) => setCatFilter(e.target.value)}
              className="w-full rounded border border-slate-700 bg-slate-950 text-xs text-slate-200 px-2 py-1"
            >
              <option value="">All categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            <ul className="max-h-56 overflow-y-auto space-y-0.5 text-xs">
              {prompts.map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    onClick={() => setInput((prev) => prev ? `${prev}\n\n${p.prompt}` : p.prompt)}
                    className="w-full text-left rounded px-2 py-1.5 text-slate-300 hover:bg-slate-800 border border-transparent hover:border-slate-700 transition-colors"
                  >
                    <span className="text-amber-500/90">{p.title}</span>
                    {p.category && <span className="text-slate-600 ml-1">· {p.category}</span>}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Settings shortcut */}
          <Link
            to="/settings"
            className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/40 px-3 py-3 text-sm text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <Settings2 className="h-4 w-4 text-amber-500/70" />
            LLM Settings
            <span className="ml-auto text-xs text-slate-600">
              {llmSettings?.provider ?? "…"}
            </span>
          </Link>
        </aside>
      </div>
    </div>
  );
}
