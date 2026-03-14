"""Scriptlet tools: list, run, stop, get source/metadata, optional generate (sandbox), ahk_help, show_help."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP

from autohotkey_mcp import help_content

BRIDGE_URL = os.getenv("AUTOHOTKEY_BRIDGE_URL", "http://127.0.0.1:10744").rstrip("/")
DEPOT = Path(os.getenv("AUTOHOTKEY_SCRIPT_DEPOT", "d:/dev/repos/autohotkey-test"))
SCRIPTLETS_DIR = DEPOT / "scriptlets"
AI_GENERATED_DIR = SCRIPTLETS_DIR / "ai_generated"


async def _bridge_get(path: str, timeout: float = 10.0) -> dict[str, Any] | list[Any] | str:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BRIDGE_URL}{path}", timeout=timeout)
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        if "application/json" in ct:
            return r.json()
        return r.text


async def _bridge_get_text(path: str, timeout: float = 10.0) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BRIDGE_URL}{path}", timeout=timeout)
        r.raise_for_status()
        return r.text


def _depot_path(script_id: str) -> Path:
    """Resolve scriptlets/<id>.ahk; allow ai_generated/<id>.ahk."""
    base = SCRIPTLETS_DIR / f"{script_id}.ahk"
    if base.exists():
        return base
    ai = AI_GENERATED_DIR / f"{script_id}.ahk"
    if ai.exists():
        return ai
    return SCRIPTLETS_DIR / f"{script_id}.ahk"


def _read_metadata(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not path.exists():
        return out
    text = path.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"(?m)^;\s*@(\w+):\s*(.+?)(?=\r?\n|$)", text):
        key, val = m.group(1).strip(), m.group(2).strip()
        out[key] = val
    if not out and re.search(r"(?m)^;\s*@description\s*:\s*(.+)", text):
        out["description"] = re.search(r"(?m)^;\s*@description\s*:\s*(.+)", text).group(1).strip()
    return out


def register_scriptlet_tools(mcp: FastMCP) -> None:
    """Register list_scriptlets, run_scriptlet, stop_scriptlet, get_scriptlet_source, get_scriptlet_metadata, generate_scriptlet, ahk_help, show_help."""

    @mcp.tool()
    async def list_scriptlets() -> dict[str, Any]:
        """
        List all AutoHotkey scriptlets from the bridge (autohotkey-test depot).
        Returns id, name, description, category, running. Requires ScriptletCOMBridge on 10744.
        """
        try:
            data = await _bridge_get("/scriptlets")
        except httpx.RequestError as e:
            return {"error": str(e), "scriptlets": [], "bridge_url": BRIDGE_URL}
        if isinstance(data, list):
            return {"scriptlets": data, "bridge_url": BRIDGE_URL}
        return {"scriptlets": [], "raw": data, "bridge_url": BRIDGE_URL}

    @mcp.tool()
    async def run_scriptlet(script_id: str) -> dict[str, Any]:
        """
        Run a scriptlet by id (e.g. quick_notes). Calls bridge /run/<id>.ahk.
        """
        script_id = script_id.strip().removesuffix(".ahk")
        try:
            out = await _bridge_get_text(f"/run/{script_id}.ahk")
            return {"success": True, "message": out, "script_id": script_id}
        except httpx.RequestError as e:
            return {"success": False, "error": str(e), "script_id": script_id}

    @mcp.tool()
    async def stop_scriptlet(script_id: str) -> dict[str, Any]:
        """
        Stop a running scriptlet by id. Calls bridge /stop/<id>.ahk.
        """
        script_id = script_id.strip().removesuffix(".ahk")
        try:
            out = await _bridge_get_text(f"/stop/{script_id}.ahk")
            return {"success": True, "message": out, "script_id": script_id}
        except httpx.RequestError as e:
            return {"success": False, "error": str(e), "script_id": script_id}

    @mcp.tool()
    async def get_scriptlet_source(script_id: str) -> dict[str, Any]:
        """
        Read full source of a scriptlet from the depot (scriptlets/<id>.ahk or scriptlets/ai_generated/<id>.ahk).
        """
        script_id = script_id.strip().removesuffix(".ahk")
        path = _depot_path(script_id)
        if not path.exists():
            return {"found": False, "script_id": script_id, "path": str(path)}
        return {
            "found": True,
            "script_id": script_id,
            "path": str(path),
            "source": path.read_text(encoding="utf-8", errors="replace"),
        }

    @mcp.tool()
    async def get_scriptlet_metadata(script_id: str) -> dict[str, Any]:
        """
        Read header metadata (@description, @version, @hotkeys, etc.) from the depot file.
        """
        script_id = script_id.strip().removesuffix(".ahk")
        path = _depot_path(script_id)
        if not path.exists():
            return {"found": False, "script_id": script_id, "metadata": {}}
        return {"found": True, "script_id": script_id, "metadata": _read_metadata(path)}

    @mcp.tool()
    async def generate_scriptlet(
        prompt: str,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """
        [Dangerous] Generate a new .ahk script from a prompt. Writes ONLY to scriptlets/ai_generated/.
        Do not move to main depot without review. filename: base name without .ahk (default from prompt).
        """
        AI_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^\w\-]", "_", (filename or prompt)[:80]).strip("_") or "generated"
        base = f"{safe}.ahk"
        path = AI_GENERATED_DIR / base
        # Stub: write a minimal script; in production you would call an LLM to generate from prompt.
        stub = f"""; Generated script – review before use.
; Prompt: {prompt[:200]}
#Requires AutoHotkey v2.0
; TODO: implement from prompt
MsgBox("Generated stub. Replace with real logic.", "autohotkey-mcp")
"""
        path.write_text(stub, encoding="utf-8")
        return {
            "success": True,
            "path": str(path),
            "script_id": safe,
            "warning": "Review before moving to main depot. Stub only; replace with real logic.",
        }

    @mcp.tool()
    async def ahk_help(
        level: str = "quick",
        topic: str | None = None,
    ) -> dict[str, Any]:
        """
        Multilevel AutoHotkey v2 and autohotkey-mcp help. level: quick | reference | language | usage | tools | mcp_server.
        topic: optional subsection (reserved). Returns markdown text for the requested level.
        """
        text = help_content.get_help(level=level, topic=topic)
        levels = list(help_content.LEVELS.keys())
        return {
            "level": level,
            "topic": topic,
            "content": text,
            "available_levels": levels,
        }

    @mcp.tool()
    async def show_help() -> dict[str, Any]:
        """
        Return URLs to open the help in a browser. Mini-help (server-rendered, one page) at /help;
        full webapp (SPA, sidebar, multiple pages) at port 10747 if web_sota is running.
        Tell the user to open the url in a browser to display the page.
        """
        port = os.getenv("PORT", "10746")
        mini_help_url = f"http://127.0.0.1:{port}/help"
        full_webapp_url = "http://127.0.0.1:10747/"
        return {
            "mini_help_url": mini_help_url,
            "full_webapp_url": full_webapp_url,
            "message": f"Open {mini_help_url} in a browser to view the mini-help page. For the full webapp (sidebar, Help/Scriptlets/Status), open {full_webapp_url} (requires web_sota/start.ps1).",
        }
