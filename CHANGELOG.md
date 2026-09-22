# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **`CuaHUD` overlay** — "CUA at work" blinking red HUD + e-stop button shown while any scriptlet is running via `run_scriptlet`. Automatically hidden when last scriptlet stops.
- **Cross-connection docs** — README table comparing autohotkey-mcp vs pywinauto-mcp with "when to use" guidance. Help content (`help_content.py`) updated with decision matrix.
- **`cua_hud.py`** — shared module (same implementation as pywinauto-mcp) for always-on-top automation indicator.

- **generate_scriptlet:** Real AHK v2 generation — **FastMCP sampling primary**, localhost HTTP fallback; validation + one repair pass; no file on failure.
- **list_generation_prompts** / **refine_ahk_prompt** MCP tools; preset prompt library (`prompt_catalog`).
- **Web SPA:** **Chat** page (personas, preset prompts, refine → Scriptlets), **Running** page (`GET /api/running`, `POST /api/stop_scriptlet`) — hotkeys, description, kill; multi-instance direct PIDs tracked.
- **MCP resources:** `ahk://prompts/catalog`, `ahk://prompts/categories`, `ahk://prompts/{prompt_id}` for agent access to the prompt library.
- **Chat:** `POST /api/chat` with `stream: true` — SSE streaming for Ollama-compatible backends.
- **Cursor skill:** `.cursor/skills/autohotkey-v2-authoring/SKILL.md`.
- Fleet-standard webapp: Vite + React SPA (port 10747) with retractable sidebar and multiple pages (Overview, Help, Scriptlets, Status).
- Backend API for SPA: `GET /api/help` (all levels or `?level=...`), `GET /api/scriptlets`.
- `web_sota/start.ps1` starts backend (10746) and frontend (10747), opens SPA in browser.
- Vite proxy of `/api` and `/health` to backend.
- **justfile** at repo root: `run`/`server`, `lint`/`check`, `format`/`fmt`, `install`, `install-web`, `web`/`start`, `clean`, `health`, `test`.
- **glama.json** at repo root for Glama marketplace metadata (name, version, description).

### Changed

- Webapp entry is the SPA at `http://127.0.0.1:10747/`.
- Fleet manifest: user-facing port 10747, health via backend 10746 (frontend proxies `/health`).
- `.gitignore`: added `web_sota/node_modules/`, `web_sota/dist/`, `*.local`.

### Added (pattern)

- **Mini-help:** `GET /help` — single server-rendered HTML page (same content as SPA Help, no npm). Lightweight alternative when running backend only. Documented as [MINI_HELP_PATTERN.md](docs/MINI_HELP_PATTERN.md) for reuse by other MCPs.
- **`lhm.plugin.json`** at repo root for LobeHub MCP marketplace listing (analog to `glama.json`), describing all 9 tools with real input schemas.

### Changed (2026-09-22 portmanteau refactor)

- **9 MCP tools total, down from 23** (fleet TOOL_DESIGN_STANDARDS.md §1 mandates portmanteau above ~20 tools):
  - `scriptlet_ops(operation="list"|"run"|"stop"|"list_running"|"get_source"|"get_metadata"|"promote")` replaces the 6 individually-decorated tools of the same names, plus adds **`promote`** (new — moves a script from `ai_generated/` into the live depot, auto-fixes the silent-exit persistence bug, blocks on hotkey collision or lint error, `force=True` overrides).
  - `ahk_dev_ops(operation="generate"|"list_prompts"|"refine_prompt"|"help"|"show_help")` replaces `generate_scriptlet`, `list_generation_prompts`, `refine_ahk_prompt`, `ahk_help`, `show_help`.
  - `macro_ops(operation="list"|"get"|"upsert"|"delete")` replaces the 4 individual macro tools.
- **`AUTOHOTKEY_SCRIPT_DEPOT` is no longer required** for the common case: `depot.py` auto-detects a sibling `../autohotkey-tools` checkout. The env var still wins when set (portability fix — the old default silently assumed `D:\Dev\repos\...`, which only worked on one machine).
- AI-generated scriptlets now get their silent-exit persistence bug (missing `Persistent()`/`SetTimer()`/shown `Gui` — process exits ~51s after load with no error) auto-fixed before being written.

### Fixed

- **Scriptlets webapp page showed 404 / blank.** Two independent bugs, both introduced by the portmanteau refactor above and only caught later:
  - Backend: `GET /api/scriptlets`, `POST /api/run_scriptlet`, `POST /api/stop_scriptlet`, and `GET /status` still called the deleted tool names (`list_scriptlets`, `run_scriptlet`, `stop_scriptlet`) via `mcp.call_tool(...)` instead of `scriptlet_ops(operation=...)`. Every call threw, was caught, and returned an empty/error response.
  - Frontend: `scriptlets.tsx` used `<Link>` (react-router-dom) without importing it, crashing the whole page with `ReferenceError: Link is not defined` and no error boundary.
- **Backend crashed mid-session (`Tcl_AsyncDelete: async handler deleted by the wrong thread`, exit code 3) while scriptlets were running.** `CuaHUD` had two Tkinter cross-thread violations: `stop()` called `root.quit()`/`root.destroy()` from the caller's thread instead of the HUD's own thread, and the blink loop ran on a separate `threading.Thread` calling `.configure()` directly. Both now route through `root.after()` polling on the Tk-owning thread only.

### Removed

- Legacy single-page HTML at `GET /` and `GET /help` was removed; mini-help restores `GET /help` only. `GET /` stays minimal JSON.

## [0.1.0] – initial

- MCP server for AutoHotkey scriptlets (list, run, stop, get source/metadata, optional generate in sandbox).
- Tools: list_scriptlets, run_scriptlet, stop_scriptlet, get_scriptlet_source, get_scriptlet_metadata, generate_scriptlet, ahk_help.
- FastAPI backend: `/health`, `/status`, `POST /tool`, single-page `/help` and `/`.
- ScriptletCOMBridge (10744) and script depot (autohotkey-test) integration.
