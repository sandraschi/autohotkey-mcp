# Product Requirements: autohotkey-mcp

## Overview

**autohotkey-mcp** is an MCP (Model Context Protocol) server that exposes AutoHotkey scriptlets to AI clients (e.g. Cursor, Claude Desktop). It uses a local **ScriptletCOMBridge** (HTTP) and a **script depot** (autohotkey-test repo) to list, run, stop, and inspect scriptlets, and optionally generate new scripts in a sandbox.

## Goals

- Expose scriptlet operations as MCP tools for use from IDEs and chat clients.
- Provide a fleet-standard webapp (retractable sidebar, multiple pages) for help, scriptlet list, and status.
- Keep a single backend (FastAPI) for both MCP-over-HTTP (e.g. RoboFang bridge) and webapp API; optional Vite SPA as the primary web UI.
- Integrate with existing autohotkey-test depot and ScriptletCOMBridge (port 10744) without duplicating logic.

## Scope

### In scope

- MCP tools: list_scriptlets, run_scriptlet, stop_scriptlet, get_scriptlet_source, get_scriptlet_metadata, ahk_help.
- Optional sandbox-only generate_scriptlet (writes to `scriptlets/ai_generated/`).
- HTTP server: `/health`, `/status`, `POST /tool` (bridge-style), `/api/help`, `/api/scriptlets` for SPA; `GET /` returns minimal JSON; `GET /help` = mini-help (server-rendered single page, no SPA).
- Fleet web_sota: SPA on 10747, backend on 10746; start.ps1 launches both and opens browser.
- Justfile for run, lint, format, install, web, clean, health.
- Documentation: README, CHANGELOG, HOW_HELP_IS_IMPLEMENTED, PRD.

### Out of scope

- Running or hosting ScriptletCOMBridge (handled by autohotkey-test / user).
- Editing scriptlet source in the webapp (view/list only; generation is sandbox + review).
- Multi-user or auth (local/single-user only).
- Packaging as a system service (user runs via uv/just/start.ps1).

## Non-goals

- Replacing autohotkey-test or ScriptletCOMBridge; this server is a client of both.
- Full IDE inside the webapp; the webapp is for help, scriptlet list, and status.

## Success criteria

- MCP clients can list, run, stop, and read scriptlets via tools.
- Users can open the SPA, use the sidebar to switch between Overview, Help, Scriptlets, Status.
- Fleet manifest and ports (10746/10747) align with robofang WEBAPP_PORTS and hub expectations.
- Ruff passes; justfile recipes work on Windows (PowerShell-friendly).
