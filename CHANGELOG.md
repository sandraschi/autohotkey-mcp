# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Fleet-standard webapp: Vite + React SPA (port 10747) with retractable sidebar and multiple pages (Overview, Help, Scriptlets, Status).
- Backend API for SPA: `GET /api/help` (all levels or `?level=...`), `GET /api/scriptlets`.
- `web_sota/start.ps1` starts backend (10746) and frontend (10747), opens SPA in browser.
- Vite proxy of `/api` and `/health` to backend.
- **justfile** at repo root: `run`, `lint`/`format`, `install`, `install-web`, `web`, `clean`, `health`.

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
