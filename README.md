# autohotkey-mcp

**Run and manage AutoHotkey v2 scriptlets from your AI assistant** — list what’s installed, launch or stop scripts, peek at source, and (optionally) draft new snippets in a safe sandbox. A small web app gives you help, a chat-style generator, and a live view of what’s running.

| | |
|--:|--|
| **You might use this if…** | You already keep scriptlets in a depot (e.g. [autohotkey-test](https://github.com/sandraschi/autohotkey-test)), use Cursor or another MCP client, and want one place to drive hotkey utilities from conversation without juggling files by hand. |
| **What it connects to** | Your script folder on disk and, when you want it, **ScriptletCOMBridge** on port **10744** for the same list/run/stop behavior as your dashboard. |

**Repo:** [github.com/sandraschi/autohotkey-mcp](https://github.com/sandraschi/autohotkey-mcp) · standalone (not under RoboFang `hands/`). **Glama:** [`glama.json`](glama.json) at repo root for marketplace metadata.

## Prerequisites

- **Script depot:** clone of autohotkey-test (default `d:/dev/repos/autohotkey-test` or set `AUTOHOTKEY_SCRIPT_DEPOT`).
- **AutoHotkey v2** installed (for direct run when bridge is not used). Set `AUTOHOTKEY_EXE` if not in default install path.
- **Optional:** ScriptletCOMBridge (autohotkey-test) on `http://127.0.0.1:10744` — when running, list/run/stop use the bridge; when not, MCP scans the depot and runs AHK directly.

## Config

| Env | Default | Description |
|-----|--------|-------------|
| `AUTOHOTKEY_BRIDGE_URL` | `http://127.0.0.1:10744` | ScriptletCOMBridge base URL (optional; fallback: direct depot + AHK run) |
| `AUTOHOTKEY_SCRIPT_DEPOT` | `d:/dev/repos/autohotkey-test` | Path to repo containing `scriptlets/` |
| `AUTOHOTKEY_EXE` | (auto-detect) | Path to AutoHotkey v2 exe when using direct run (no bridge) |
| `AUTOHOTKEY_MCP_HTTP` | (auto) | Set to `0` to force stdio-only. When unset, stdio-only if stdin is a pipe (Cursor/IDE). |
| `PORT` | `10746` | Backend port (fleet 10700–10800) |
| `AUTOHOTKEY_LLM_BASE_URL` | `http://127.0.0.1:11434/v1` | OpenAI-compatible chat URL (localhost only — SSRF-safe). Use Ollama or LM Studio. |
| `AUTOHOTKEY_LLM_MODEL` | `llama3.2` | Model id for `/chat/completions`. |
| `AUTOHOTKEY_LLM_API_KEY` | (unset) | Optional Bearer token for local servers that require it. `OPENAI_API_KEY` is also read. |
| `AUTOHOTKEY_LLM_TIMEOUT` | `120` | HTTP completion timeout (seconds). |

**LLM architecture:** **FastMCP 3.1 sampling** (`Context.sample`) is the **primary** path for `generate_scriptlet` / `refine_ahk_prompt` inside MCP hosts (e.g. Cursor). **Local HTTP** (`AUTOHOTKEY_LLM_*`, Ollama/LM Studio) is the **fallback** when sampling is unavailable, and powers the **web SPA** Chat + generate form (browsers have no MCP context). No file is written if both paths fail or validation fails.

**MCP resources (agents):** Preset prompt catalog is exposed as read-only resources: `ahk://prompts/catalog` (full JSON list), `ahk://prompts/categories`, `ahk://prompts/{prompt_id}` (one entry; JSON error if id unknown).

**Chat streaming (web):** `POST /api/chat` with `"stream": true` returns **SSE** (`text/event-stream`) with OpenAI-style chunked deltas from Ollama/LM Studio. The SPA Chat page enables this by default (toggle “Stream”).

## Tools

- **list_generation_prompts** – Preset prompt library (categories, tags) for ideation.
- **refine_ahk_prompt** – Refine a vague idea into a clear prompt (sampling-first, same as generate).
- **list_running_scriptlets** – Running instances with depot metadata (`@hotkeys`, `@description`); PIDs for MCP direct runs.
- **stop_scriptlet** – Stop by id; optional `pid` to stop one instance when several copies of the same script are running (direct).
- **list_scriptlets** – List scriptlets (from bridge `/scriptlets`); id, name, description, category, running.
- **run_scriptlet** – Run a scriptlet by id (e.g. `quick_notes` → bridge `/run/quick_notes.ahk`).
- **stop_scriptlet** – Stop a scriptlet by id.
- **get_scriptlet_source** – Read full source from depot `scriptlets/<id>.ahk`.
- **get_scriptlet_metadata** – Read header metadata (@description, @version, etc.) from depot.
- **generate_scriptlet** – *(Sandbox)* Generate AHK v2 from a natural-language prompt via **MCP sampling** (when the client supports it) or **localhost OpenAI-compatible HTTP** (`AUTOHOTKEY_LLM_*`). Writes only to `scriptlets/ai_generated/` after validation; **no file on failure**. Review before promoting out of `ai_generated/`.
- **ahk_help(level?, topic?)** – Multilevel help (markdown). level: `quick` | `reference` | `language` | `usage` | `tools` | `mcp_server`.
- **show_help** – Returns URLs for mini-help (`/help`) and full webapp (10747). Use so the user can open the page in a browser.

## Webapp (fleet-standard SPA)

- **Frontend:** Vite + React on **10747** — Overview, Help, **Chat** (personas, presets, refine), **Scriptlets**, **Running** (live list: hotkeys, description, kill), Status.
- **Backend:** FastAPI on **10746** — `/health`, `/api/help`, `/api/scriptlets`, **`GET /api/running`**, **`POST /api/stop_scriptlet`**, `/api/personas`, `/api/prompts`, `POST /api/chat`, `POST /api/refine_prompt`, `POST /api/generate_scriptlet`, `/status`, `POST /tool`.
- **Launch:** `.\web_sota\start.ps1` — starts backend, then frontend, opens `http://127.0.0.1:10747/`.
- **Mini-help:** Backend-only alternative: run the server and open `http://127.0.0.1:10746/help` — single server-rendered HTML page (no SPA, no npm). See [docs/MINI_HELP_PATTERN.md](docs/MINI_HELP_PATTERN.md).

## Install

```powershell
git clone https://github.com/sandraschi/autohotkey-mcp.git
Set-Location autohotkey-mcp
uv sync
```

Commands below assume the **repository root** unless noted.

## Run

**Single process (FastMCP 3.1 dual transport):** stdio for Cursor/Claude and HTTP on 10746.
```powershell
uv sync
uv run autohotkey-mcp
```
Or: `just run` / `just server`.

**Cursor:** When stdin is a pipe (Cursor, Claude Desktop, etc.), the server runs **stdio-only** automatically (no HTTP, no port bind). So you don't need to set any env. If 10746 is already in use, Cursor's process won't try to bind it. To force stdio-only when running from a terminal, set `AUTOHOTKEY_MCP_HTTP=0`.

**Full webapp:** `.\web_sota\start.ps1` or `just web`.

**Tasks:** `just --list` — lint, format, install, clean, health.

## Fleet

- **Ports:** Backend 10746, frontend 10747 (user-facing). Register in robofang `docs/standards/WEBAPP_PORTS.md` if using the Hub.
- **Health:** `GET http://127.0.0.1:10746/health` (frontend proxies `/health` to backend).
- **Tool invoke:** `POST /tool` with `{"name": "...", "arguments": {...}}` (RoboFang bridge style).
