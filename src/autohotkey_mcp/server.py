"""
AutoHotkey MCP server: scriptlet depot + ScriptletCOMBridge.
Exposes GET /status (for RoboFang Hub) and POST /tool (for bridge connector).
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastmcp import FastMCP

from autohotkey_mcp import help_content
from autohotkey_mcp.tools import register_scriptlet_tools

PORT = int(os.getenv("PORT", "10746"))
HOST = os.getenv("HOST", "127.0.0.1")

mcp = FastMCP("autohotkey-mcp")
register_scriptlet_tools(mcp)

app = FastAPI(title="AutoHotkey MCP", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, Any]:
    """Fleet health check (web_sota start scripts and manifest use this)."""
    return {"ok": True, "service": "autohotkey-mcp", "port": PORT}


@app.get("/api/scriptlets")
async def api_scriptlets() -> JSONResponse:
    """SPA: list scriptlets (same as list_scriptlets tool)."""
    try:
        result = await mcp.call_tool("list_scriptlets", {})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "scriptlets": []})
    if hasattr(result, "structured_content") and result.structured_content is not None:
        data = result.structured_content
    elif hasattr(result, "content") and result.content:
        raw = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"scriptlets": []}
    else:
        data = {"scriptlets": []}
    if isinstance(data, dict) and "scriptlets" in data:
        return JSONResponse(content=data)
    return JSONResponse(content={"scriptlets": data if isinstance(data, list) else []})


@app.get("/api/help")
async def api_help(level: str | None = None) -> JSONResponse:
    """SPA: help content. level= quick|reference|language|usage|tools|mcp_server or omit for all."""
    if level:
        content = help_content.get_help(level=level)
        return JSONResponse(content={"level": level, "content": content})
    return JSONResponse(content={"levels": help_content.get_all_levels()})


@app.get("/status")
async def status() -> dict[str, Any]:
    """Hub and proxy: GET /status."""
    try:
        result = await mcp.call_tool("list_scriptlets", {})
    except Exception:
        return {"ok": True, "service": "autohotkey-mcp", "port": PORT}
    if hasattr(result, "structured_content") and result.structured_content is not None:
        return {"ok": True, "service": "autohotkey-mcp", "port": PORT, "scriptlets": result.structured_content}
    if hasattr(result, "content") and result.content:
        raw = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
        try:
            data = json.loads(raw)
            return {"ok": True, "service": "autohotkey-mcp", "port": PORT, "scriptlets": data}
        except json.JSONDecodeError:
            pass
    return {"ok": True, "service": "autohotkey-mcp", "port": PORT}


def _md_to_html(md: str) -> str:
    """Minimal markdown to HTML for mini-help (code blocks, headings, bold, newlines)."""
    import html
    import re

    out = md
    def sub_code(m: re.Match) -> str:
        return "<pre><code>" + html.escape(m.group(1)) + "</code></pre>"
    out = re.sub(r"```(?:\w*)\n(.*?)```", sub_code, out, flags=re.DOTALL)
    out = html.escape(out)
    out = re.sub(r"^### (.+)$", r"<h3>\1</h3>", out, flags=re.MULTILINE)
    out = re.sub(r"^## (.+)$", r"<h2>\1</h2>", out, flags=re.MULTILINE)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = out.replace("\n", "<br/>\n")
    return out


def _mini_help_html() -> str:
    """Single-page mini-help (no SPA, no npm). Alternative to full web_sota."""
    levels = help_content.get_all_levels()
    order = ["quick", "reference", "language", "usage", "tools", "mcp_server"]
    nav = "".join(f'<a href="#{k}">{k}</a> ' for k in order if k in levels)
    sections = "".join(
        f'<section id="{k}"><h2>{k}</h2><div class="c">{_md_to_html(levels[k])}</div></section>'
        for k in order if k in levels
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AutoHotkey MCP – Help</title>
<style>body{{font-family:system-ui,sans-serif;margin:1rem 2rem;max-width:900px;line-height:1.5;}}
nav{{margin-bottom:1rem;padding:.5rem 0;border-bottom:1px solid #ccc;}} nav a{{margin-right:1rem;}}
section{{margin-bottom:2rem;}} .c{{white-space:pre-wrap;}} pre{{background:#f5f5f5;padding:.75rem;overflow-x:auto;}}
strong{{font-weight:600;}} a{{color:#06c;}}</style></head><body>
<h1>AutoHotkey MCP – Help</h1>
<nav>{nav}</nav>
{sections}
<p><small>Mini-help (server-rendered). Full webapp: <a href="http://127.0.0.1:10747/">10747</a> · <a href="/">/</a> <a href="/status">/status</a></small></p>
</body></html>"""


@app.get("/help", response_class=HTMLResponse)
async def mini_help() -> str:
    """Mini-help: single server-rendered page (no SPA). Lightweight alternative to full webapp."""
    return _mini_help_html()


@app.get("/")
async def root() -> dict[str, Any]:
    """Root: minimal service info. Full webapp on 10747; mini-help at /help."""
    return {"service": "autohotkey-mcp", "port": PORT, "health": "/health", "help": "/help", "api": ["/api/help", "/api/scriptlets"]}


@app.post("/tool")
async def tool(request: Request) -> JSONResponse:
    """Bridge connector: POST /tool with {"name": "...", "arguments": {...}}."""
    try:
        body = await request.json()
        name = body.get("name") or body.get("tool")
        arguments = body.get("arguments") or body.get("params") or {}
        if not name:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Missing 'name' or 'tool'"},
            )
        result = await mcp.call_tool(name, arguments)
        if hasattr(result, "structured_content") and result.structured_content is not None:
            data = result.structured_content
        elif hasattr(result, "content") and result.content:
            raw = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"raw": raw}
        else:
            data = {"result": str(result)}
        return JSONResponse(content={"result": data, "success": True})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


def main() -> None:
    import asyncio
    import uvicorn

    async def _run_dual() -> None:
        config = uvicorn.Config(app, host=HOST, port=PORT, log_level="info")
        server = uvicorn.Server(config)
        http_task = asyncio.create_task(server.serve())
        try:
            await mcp.run_stdio_async()
        finally:
            http_task.cancel()
            try:
                await http_task
            except asyncio.CancelledError:
                pass

    asyncio.run(_run_dual())


if __name__ == "__main__":
    main()
    sys.exit(0)
