# Mini-help pattern

**Idea:** The backend serves a **single server-rendered HTML help page** (markdown→HTML, no JS framework) as a lightweight alternative to the full fleet webapp (Vite SPA). One process, one port, no npm.

## When it’s useful

- **Backend-only runs:** User runs `uv run autohotkey-mcp` and opens `http://127.0.0.1:10746/help` — no need to start the SPA or install Node.
- **Quick docs:** Same content as the SPA Help page, but no sidebar, no routing, minimal CSS.
- **Portability:** Works wherever the Python server runs; no second port, no proxy.

## How it works here

- **Content:** Same `help_content.get_all_levels()` as the `ahk_help` tool and `/api/help`.
- **Rendering:** `_md_to_html(md)` in `server.py` — code blocks, `##`/`###`, `**bold**`, newlines. No heavy markdown library.
- **Route:** `GET /help` returns one HTML page with in-page nav anchors and a section per level.
- **Naming:** We call this “mini-help” to distinguish it from the full webapp (web_sota SPA on 10747).

## As a pattern for other MCPs

1. **Keep help content in one place** (e.g. a `help_content` module or dict). Expose it via:
   - MCP tool (e.g. `ahk_help`),
   - JSON API for the SPA (e.g. `GET /api/help`),
   - and a server-rendered HTML page (e.g. `GET /help`).
2. **Minimal HTML pipeline:** One function markdown→HTML (or subset), one function that builds the full page with nav + sections. No frontend build.
3. **Optional full webapp:** When you add a fleet SPA (retractable sidebar, multiple pages), keep `GET /help` as the “mini” option so backend-only users still get readable docs.

Result: **two ways to get help** — run the full webapp (fleet-standard) or run the server and open `/help` (mini-help).
