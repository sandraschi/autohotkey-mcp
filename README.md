# autohotkey-mcp

MCP server for AutoHotkey scriptlets. Uses the [autohotkey-test](https://github.com/sandraschi/autohotkey-test) repo as the script depot and talks to **ScriptletCOMBridge** (HTTP on port 10744) for run/stop/list.

**Repo:** [github.com/sandraschi/autohotkey-mcp](https://github.com/sandraschi/autohotkey-mcp). Standalone (not under RoboFang `hands/`).

## Prerequisites

- **ScriptletCOMBridge** running (e.g. `autohotkey-test/start_dashboard.bat` or `ScriptletCOMBridge.ahk`) on `http://127.0.0.1:10744`.
- **Script depot:** clone of autohotkey-test (default `d:/dev/repos/autohotkey-test` or set `AUTOHOTKEY_SCRIPT_DEPOT`).

## Config

| Env | Default | Description |
|-----|--------|-------------|
| `AUTOHOTKEY_BRIDGE_URL` | `http://127.0.0.1:10744` | ScriptletCOMBridge base URL |
| `AUTOHOTKEY_SCRIPT_DEPOT` | `d:/dev/repos/autohotkey-test` | Path to repo containing `scriptlets/` |
| `PORT` | `10746` | Backend port (fleet 10700–10800) |

## Tools

- **list_scriptlets** – List scriptlets (from bridge `/scriptlets`); id, name, description, category, running.
- **run_scriptlet** – Run a scriptlet by id (e.g. `quick_notes` → bridge `/run/quick_notes.ahk`).
- **stop_scriptlet** – Stop a scriptlet by id.
- **get_scriptlet_source** – Read full source from depot `scriptlets/<id>.ahk`.
- **get_scriptlet_metadata** – Read header metadata (@description, @version, etc.) from depot.
- **generate_scriptlet** – *(Sandbox only)* Generate a new .ahk script from a prompt; writes to `scriptlets/ai_generated/`. Review before moving to main depot.
- **ahk_help(level?, topic?)** – Multilevel help (markdown). level: `quick` | `reference` | `language` | `usage` | `tools` | `mcp_server`.
- **show_help** – Returns URLs for mini-help (`/help`) and full webapp (10747). Use so the user can open the page in a browser.

## Webapp (fleet-standard SPA)

- **Frontend:** Vite + React on **10747** — retractable sidebar, pages: Overview, Help, Scriptlets, Status.
- **Backend:** FastAPI on **10746** — `/health`, `/api/help`, `/api/scriptlets`, `/status`, `POST /tool`.
- **Launch:** `.\web_sota\start.ps1` — starts backend, then frontend, opens `http://127.0.0.1:10747/`.
- **Mini-help:** Backend-only alternative: run the server and open `http://127.0.0.1:10746/help` — single server-rendered HTML page (no SPA, no npm). See [docs/MINI_HELP_PATTERN.md](docs/MINI_HELP_PATTERN.md).

## Run

**Single process (FastMCP 3.1 dual transport):** stdio for Cursor/Claude and HTTP on 10746.
```powershell
uv sync
uv run autohotkey-mcp
```
Or: `just run` / `just server`.

**Full webapp:** `.\web_sota\start.ps1` or `just web`.

**Tasks:** `just --list` — lint, format, install, clean, health.

## Fleet

- **Ports:** Backend 10746, frontend 10747 (user-facing). Register in robofang `docs/standards/WEBAPP_PORTS.md` if using the Hub.
- **Health:** `GET http://127.0.0.1:10746/health` (frontend proxies `/health` to backend).
- **Tool invoke:** `POST /tool` with `{"name": "...", "arguments": {...}}` (RoboFang bridge style).
