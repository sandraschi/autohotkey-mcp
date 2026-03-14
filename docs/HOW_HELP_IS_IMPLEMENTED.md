# How the help is implemented

- **Content:** `src/autohotkey_mcp/help_content.py` holds markdown strings per level (`quick`, `reference`, `language`, `usage`, `tools`, `mcp_server`). `get_help(level, topic)` and `get_all_levels()` return raw text.
- **Tool:** `ahk_help(level=..., topic=...)` in `tools/scriptlets.py` calls `help_content.get_help()`, returns `{ level, topic, content, available_levels }` for MCP clients.
- **Backend HTTP:**
  - `GET /api/help` — JSON for the SPA (`levels` or `?level=...`).
  - `GET /help` — **mini-help:** single server-rendered HTML page (`_md_to_html` + `_mini_help_html`). No SPA, no npm; lightweight alternative when running backend only. See [MINI_HELP_PATTERN.md](MINI_HELP_PATTERN.md).
- **SPA (web_sota):** The React app (port 10747) fetches `/api/help`, renders level tabs and content. Full fleet-standard webapp.

Two ways to read help: full webapp (SPA on 10747) or mini-help (`/help` on 10746). Backend `GET /` returns minimal JSON with a `help` link.
