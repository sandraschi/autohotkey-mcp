# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

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

### Removed

- Legacy single-page HTML at `GET /` and `GET /help` was removed; mini-help restores `GET /help` only. `GET /` stays minimal JSON.

## [0.1.0] – initial

- MCP server for AutoHotkey scriptlets (list, run, stop, get source/metadata, optional generate in sandbox).
- Tools: list_scriptlets, run_scriptlet, stop_scriptlet, get_scriptlet_source, get_scriptlet_metadata, generate_scriptlet, ahk_help.
- FastAPI backend: `/health`, `/status`, `POST /tool`, single-page `/help` and `/`.
- ScriptletCOMBridge (10744) and script depot (autohotkey-test) integration.
