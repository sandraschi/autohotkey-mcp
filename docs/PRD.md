# Product Requirements: autohotkey-mcp

## Overview

**autohotkey-mcp** is an MCP (Model Context Protocol) server that exposes AutoHotkey v2 scriptlets to AI clients (e.g. Cursor, Claude Desktop). It uses a local **ScriptletCOMBridge** (HTTP) and a **script depot** (autohotkey-test repo) to list, run, stop, and inspect scriptlets, and optionally generate new scripts in a sandbox. **FastMCP 3.1** sampling is the primary path for AI-assisted generation; localhost OpenAI-compatible HTTP backs the web UI and fallback.

## Goals

- Expose scriptlet operations as MCP tools for use from IDEs and chat clients.
- Provide a fleet-standard webapp (retractable sidebar, multiple pages) for help, scriptlets, **Chat** (personas, presets, refine), **Running** (live instances, kill), and status.
- Keep a single backend (FastAPI) for MCP-over-HTTP, bridge-style `POST /tool`, and webapp APIs; Vite SPA as the primary web UI on **10747**.
- Integrate with autohotkey-test depot and ScriptletCOMBridge (port **10744**) without duplicating bridge logic.
- Expose the preset prompt library as **MCP resources** (`ahk://prompts/...`) for agents.

## Scope

### In scope

- **MCP tools:** `list_scriptlets`, `run_scriptlet`, `stop_scriptlet` (optional `pid` for multi-instance), `get_scriptlet_source`, `get_scriptlet_metadata`, `list_running_scriptlets`, `generate_scriptlet`, `list_generation_prompts`, `refine_ahk_prompt`, `ahk_help`, `show_help`.
- **MCP resources:** `ahk://prompts/catalog`, `ahk://prompts/categories`, `ahk://prompts/{prompt_id}`.
- **Generation:** Sandbox writes under `scriptlets/ai_generated/` only after validation; **sampling-first**, localhost LLM fallback; no file on failure.
- **HTTP:** `/health`, `/status`, `POST /tool`; `/api/help`, `/api/scriptlets`, `/api/running`, `POST /api/stop_scriptlet`, `/api/personas`, `/api/prompts`, `POST /api/chat` (SSE when `stream: true`), `POST /api/refine_prompt`, `POST /api/generate_scriptlet`; `GET /` minimal JSON; `GET /help` mini-help (server-rendered HTML, no SPA).
- **Fleet web_sota:** SPA on **10747**, backend on **10746**; `web_sota/start.ps1` launches both and opens the browser; Vite proxies `/api` and `/health`.
- **Developer UX:** **justfile** (`run`/`server`, `lint`/`check`, `format`/`fmt`, `test`, `install`, `install-web`, `web`/`start`, `clean`, `health`); **glama.json** for Glama listing metadata.
- **Documentation:** README, CHANGELOG, HOW_HELP_IS_IMPLEMENTED, PRD, MINI_HELP_PATTERN, Cursor skill under `.cursor/skills/`.

### Out of scope

- Running or hosting ScriptletCOMBridge (handled by autohotkey-test / user).
- Editing scriptlet source in the webapp (view/list/generate sandbox only).
- Multi-user or auth (local/single-user only).
- Packaging as a system service (user runs via uv/just/start.ps1).

## Non-goals

- Replacing autohotkey-test or ScriptletCOMBridge; this server is a client of both.
- Full IDE inside the webapp; the webapp is for help, scriptlets, chat-assisted generation, and runtime visibility.

## Success criteria

- MCP clients can list, run, stop, inspect, and generate (sandbox) scriptlets via tools; agents can read prompt resources.
- Users can open the SPA and use Overview, Help, Chat, Scriptlets, Running, Status; Chat can stream SSE to compatible backends.
- Fleet manifest and ports (**10746**/**10747**) align with RoboFang `WEBAPP_PORTS` and hub expectations.
- Ruff passes; justfile recipes work on Windows; `glama.json` matches `pyproject.toml` version.
