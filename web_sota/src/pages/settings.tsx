import { useState, useEffect, useCallback } from "react";
import { Settings2, RefreshCw, Check, AlertCircle, Loader2, Eye, EyeOff, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/common/utils";

// ── Types ──────────────────────────────────────────────────────────────────────

interface LLMSettings {
  base_url: string;
  model: string;
  provider: "ollama" | "lmstudio" | "openai" | string;
  timeout: number;
  api_key_set: boolean;
}

interface ModelsResult {
  success: boolean;
  models: string[];
  base_url: string;
  errors: string[];
}

// ── Provider presets ───────────────────────────────────────────────────────────

const PROVIDERS = [
  {
    id: "ollama",
    label: "Ollama",
    url: "http://127.0.0.1:11434/v1",
    note: "Local models via Ollama. Default port 11434.",
    needsKey: false,
  },
  {
    id: "lmstudio",
    label: "LM Studio",
    url: "http://127.0.0.1:1234/v1",
    note: "LM Studio local server. Default port 1234.",
    needsKey: false,
  },
  {
    id: "openai",
    label: "OpenAI-compatible",
    url: "http://127.0.0.1:11434/v1",
    note: "Any OpenAI-compatible endpoint (localhost only for security).",
    needsKey: true,
  },
] as const;

type ProviderId = (typeof PROVIDERS)[number]["id"];

// ── StatusDot ──────────────────────────────────────────────────────────────────

function StatusDot({ ok, label }: { ok: boolean | null; label: string }) {
  return (
    <span className="flex items-center gap-1.5 text-xs">
      {ok === null ? (
        <span className="h-2 w-2 rounded-full bg-slate-600 animate-pulse" />
      ) : ok ? (
        <span className="h-2 w-2 rounded-full bg-emerald-400" />
      ) : (
        <span className="h-2 w-2 rounded-full bg-red-400" />
      )}
      <span className={ok === null ? "text-slate-500" : ok ? "text-emerald-400" : "text-red-400"}>
        {label}
      </span>
    </span>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export function LLMSettings() {
  const [settings, setSettings] = useState<LLMSettings | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);

  // Edit state
  const [provider, setProvider] = useState<ProviderId>("ollama");
  const [baseUrl, setBaseUrl] = useState("http://127.0.0.1:11434/v1");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [timeout, setTimeout_] = useState(120);

  // Model list
  const [models, setModels] = useState<string[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [modelsErr, setModelsErr] = useState<string | null>(null);

  // Save state
  const [saving, setSaving] = useState(false);
  const [saveResult, setSaveResult] = useState<{ ok: boolean; msg: string } | null>(null);

  // Connection test
  const [testState, setTestState] = useState<boolean | null>(null);

  // ── Load current settings ──────────────────────────────────────────────────

  const loadSettings = useCallback(() => {
    setLoadErr(null);
    fetch("/api/llm/settings")
      .then((r) => r.json() as Promise<LLMSettings>)
      .then((s) => {
        setSettings(s);
        setBaseUrl(s.base_url);
        setModel(s.model);
        setTimeout_(s.timeout ?? 120);
        const p = PROVIDERS.find((pr) => pr.id === s.provider)?.id ?? "ollama";
        setProvider(p as ProviderId);
      })
      .catch((e) => setLoadErr(e instanceof Error ? e.message : "Failed to load settings"));
  }, []);

  useEffect(() => { loadSettings(); }, [loadSettings]);

  // ── Fetch models ───────────────────────────────────────────────────────────

  const fetchModels = useCallback(async () => {
    setModelsLoading(true);
    setModelsErr(null);
    setTestState(null);
    try {
      const r = await fetch("/api/llm/models");
      const d = await r.json() as ModelsResult;
      if (d.models.length > 0) {
        setModels(d.models);
        setTestState(true);
        // Auto-select first model if current model not in list
        if (d.models.length && !d.models.includes(model)) {
          setModel(d.models[0]);
        }
      } else {
        setModels([]);
        setTestState(false);
        setModelsErr(d.errors.join("; ") || "No models returned — is the server running?");
      }
    } catch (e) {
      setModels([]);
      setTestState(false);
      setModelsErr(e instanceof Error ? e.message : "Request failed");
    } finally {
      setModelsLoading(false);
    }
  }, [model]);

  // ── Apply provider preset ──────────────────────────────────────────────────

  const applyProvider = (p: ProviderId) => {
    setProvider(p);
    const preset = PROVIDERS.find((pr) => pr.id === p);
    if (preset) setBaseUrl(preset.url);
    setModels([]);
    setTestState(null);
    setModelsErr(null);
    setSaveResult(null);
  };

  // ── Save ───────────────────────────────────────────────────────────────────

  const save = async () => {
    setSaving(true);
    setSaveResult(null);
    try {
      const body: Record<string, unknown> = {
        base_url: baseUrl.trim(),
        model: model.trim(),
        timeout,
      };
      if (apiKey.trim()) body.api_key = apiKey.trim();
      const r = await fetch("/api/llm/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const d = await r.json() as { success: boolean; updated?: Record<string, unknown>; error?: string };
      if (d.success) {
        setSaveResult({ ok: true, msg: "Settings applied to this session." });
        loadSettings();
      } else {
        setSaveResult({ ok: false, msg: d.error ?? "Failed to save" });
      }
    } catch (e) {
      setSaveResult({ ok: false, msg: e instanceof Error ? e.message : "Request failed" });
    } finally {
      setSaving(false);
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  if (loadErr) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Settings2 className="h-7 w-7 text-amber-500" /> LLM Settings
        </h1>
        <p className="text-amber-400 text-sm">Backend unreachable: {loadErr}</p>
      </div>
    );
  }

  const selectedPreset = PROVIDERS.find((p) => p.id === provider);

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Settings2 className="h-7 w-7 text-amber-500" />
          LLM Settings
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Configure the local LLM used by Chat and script generation.
          Settings apply to this server session only — restart to revert to env defaults.
        </p>
      </div>

      {/* Current effective settings */}
      {settings && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 px-4 py-3 text-sm space-y-1">
          <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">Current effective config</p>
          <div className="grid grid-cols-[120px_1fr] gap-x-3 gap-y-1 text-slate-400">
            <span className="text-slate-500">Provider</span>
            <span className="text-slate-300">{settings.provider}</span>
            <span className="text-slate-500">Base URL</span>
            <code className="text-amber-300 text-xs">{settings.base_url}</code>
            <span className="text-slate-500">Model</span>
            <code className="text-amber-300 text-xs">{settings.model}</code>
            <span className="text-slate-500">Timeout</span>
            <span className="text-slate-300">{settings.timeout}s</span>
            <span className="text-slate-500">API key</span>
            <span className={settings.api_key_set ? "text-emerald-400" : "text-slate-600"}>
              {settings.api_key_set ? "set" : "not set"}
            </span>
          </div>
        </div>
      )}

      {/* Provider selector */}
      <div className="space-y-2">
        <label className="text-sm font-semibold text-slate-300">Provider</label>
        <div className="flex flex-wrap gap-2">
          {PROVIDERS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => applyProvider(p.id)}
              className={cn(
                "rounded-lg border px-4 py-2 text-sm font-medium transition-colors",
                provider === p.id
                  ? "border-amber-600 bg-amber-600/20 text-amber-300"
                  : "border-slate-700 bg-slate-900 text-slate-400 hover:bg-slate-800"
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
        {selectedPreset && (
          <p className="text-xs text-slate-500">{selectedPreset.note}</p>
        )}
      </div>

      {/* Base URL */}
      <div className="space-y-1.5">
        <label className="text-sm font-semibold text-slate-300">Base URL</label>
        <input
          type="text"
          value={baseUrl}
          onChange={(e) => { setBaseUrl(e.target.value); setTestState(null); setModels([]); }}
          placeholder="http://127.0.0.1:11434/v1"
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm font-mono text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
        />
        <p className="text-xs text-slate-600">Must be localhost / 127.0.0.1 / ::1 (SSRF protection).</p>
      </div>

      {/* Model selector */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <label className="text-sm font-semibold text-slate-300">Model</label>
          <button
            type="button"
            onClick={fetchModels}
            disabled={modelsLoading}
            className="inline-flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            {modelsLoading
              ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
              : <RefreshCw className="h-3.5 w-3.5" />}
            {modelsLoading ? "Fetching…" : "Fetch models"}
          </button>
        </div>

        {/* Connection status */}
        <div className="flex items-center gap-3">
          <StatusDot
            ok={testState}
            label={testState === null ? "not tested" : testState ? `${models.length} models found` : "unreachable"}
          />
          {testState ? (
            <span className="flex items-center gap-1 text-xs text-emerald-400">
              <Wifi className="h-3.5 w-3.5" /> connected
            </span>
          ) : testState === false ? (
            <span className="flex items-center gap-1 text-xs text-red-400">
              <WifiOff className="h-3.5 w-3.5" /> no connection
            </span>
          ) : null}
        </div>

        {modelsErr && (
          <p className="text-xs text-red-400 flex items-start gap-1.5">
            <AlertCircle className="h-3.5 w-3.5 mt-0.5 shrink-0" />
            {modelsErr}
          </p>
        )}

        {models.length > 0 ? (
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
          >
            {models.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        ) : (
          <input
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="e.g. qwen2.5-coder:14b"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm font-mono text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
          />
        )}
        <p className="text-xs text-slate-600">
          Hit "Fetch models" to pull the list from your running server, or type a model name manually.
        </p>
      </div>

      {/* API key (shown when provider needs it or already set) */}
      {(selectedPreset?.needsKey || settings?.api_key_set) && (
        <div className="space-y-1.5">
          <label className="text-sm font-semibold text-slate-300">
            API Key {settings?.api_key_set && <span className="text-emerald-400 text-xs">(already set)</span>}
          </label>
          <div className="relative">
            <input
              type={showKey ? "text" : "password"}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={settings?.api_key_set ? "leave blank to keep existing" : "sk-…"}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 pr-10 text-sm font-mono text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
            />
            <button
              type="button"
              onClick={() => setShowKey((v) => !v)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
            >
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>
      )}

      {/* Timeout */}
      <div className="space-y-1.5">
        <label className="text-sm font-semibold text-slate-300">
          Timeout — <span className="text-amber-300 font-mono">{timeout}s</span>
        </label>
        <input
          type="range"
          min={10}
          max={300}
          step={10}
          value={timeout}
          onChange={(e) => setTimeout_(Number(e.target.value))}
          className="w-full accent-amber-500"
        />
        <div className="flex justify-between text-xs text-slate-600">
          <span>10s (fast models)</span>
          <span>300s (large models)</span>
        </div>
      </div>

      {/* Save button + result */}
      <div className="flex items-center gap-3 pt-2">
        <button
          type="button"
          onClick={save}
          disabled={saving}
          className="inline-flex items-center gap-2 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white px-5 py-2.5 text-sm font-medium transition-colors"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
          Apply Settings
        </button>
        <button
          type="button"
          onClick={loadSettings}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 text-slate-400 hover:bg-slate-800 px-3 py-2.5 text-sm transition-colors"
        >
          <RefreshCw className="h-4 w-4" /> Reset
        </button>
        {saveResult && (
          <span className={cn("text-sm flex items-center gap-1.5", saveResult.ok ? "text-emerald-400" : "text-red-400")}>
            {saveResult.ok
              ? <Check className="h-4 w-4" />
              : <AlertCircle className="h-4 w-4" />}
            {saveResult.msg}
          </span>
        )}
      </div>

      {/* Note about persistence */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/30 px-4 py-3 text-xs text-slate-500">
        <strong className="text-slate-400">Session-only:</strong> These settings are applied to the running
        server process and reset on restart. To persist them, set{" "}
        <code className="text-slate-400">AUTOHOTKEY_LLM_BASE_URL</code>,{" "}
        <code className="text-slate-400">AUTOHOTKEY_LLM_MODEL</code>, and optionally{" "}
        <code className="text-slate-400">AUTOHOTKEY_LLM_API_KEY</code> in your environment before starting the server.
      </div>
    </div>
  );
}
