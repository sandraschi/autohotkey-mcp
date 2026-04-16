"""Scriptlet tools: list, run, stop, get source/metadata, optional generate (sandbox), ahk_help, show_help.
Uses ScriptletCOMBridge when available; falls back to direct depot scan + subprocess run/stop with PID tracking.
"""

from __future__ import annotations

import asyncio
import os
import re
import signal
import subprocess
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context
from fastmcp.server.dependencies import OptionalCurrentContext

from autohotkey_mcp import help_content
from autohotkey_mcp import personas as personas_mod
from autohotkey_mcp import prompt_catalog
from autohotkey_mcp.prompt_refine import refine_generation_prompt
from autohotkey_mcp.scriptlet_generate import generate_ahk_script_to_file

BRIDGE_URL = os.getenv("AUTOHOTKEY_BRIDGE_URL", "http://127.0.0.1:10744").rstrip("/")
DEPOT = Path(os.getenv("AUTOHOTKEY_SCRIPT_DEPOT", "d:/dev/repos/autohotkey-test"))
SCRIPTLETS_DIR = DEPOT / "scriptlets"
AI_GENERATED_DIR = SCRIPTLETS_DIR / "ai_generated"

# In-memory instances when using direct run (no bridge). Multiple launches of the same script = multiple rows.
_running_instances: list[dict[str, Any]] = []


def _pid_is_alive(pid: int) -> bool:
    try:
        if os.name != "nt":
            os.kill(pid, 0)
            return True
    except OSError:
        return False
    except Exception:
        return False
    try:
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        return str(pid) in (r.stdout or "")
    except Exception:
        return True


def _prune_dead_instances() -> None:
    global _running_instances
    _running_instances = [i for i in _running_instances if _pid_is_alive(i["pid"])]


def _direct_running_ids() -> set[str]:
    _prune_dead_instances()
    return {str(i["script_id"]) for i in _running_instances}


def _find_ahk_exe() -> str | None:
    """Return path to AutoHotkey v2 exe, or None. Checks env, then common install paths."""
    exe = os.getenv("AUTOHOTKEY_EXE") or os.getenv("AHK_PATH")
    if exe and Path(exe).exists():
        return exe
    candidates = [
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "AutoHotkey/v2/AutoHotkey64.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))
        / "AutoHotkey/v2/AutoHotkey64.exe",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "AutoHotkey/v2/AutoHotkey32.exe",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def _list_scriptlets_direct() -> list[dict[str, Any]]:
    """Scan depot for *.ahk and build list from file metadata. Includes running state from _running."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for folder in (SCRIPTLETS_DIR, AI_GENERATED_DIR):
        if not folder.exists():
            continue
        for path in folder.glob("*.ahk"):
            script_id = path.stem
            if script_id in seen:
                continue
            seen.add(script_id)
            meta = _read_metadata(path)
            out.append(
                {
                    "id": script_id,
                    "name": meta.get("name") or script_id,
                    "description": meta.get("description") or "",
                    "category": meta.get("category") or "general",
                    "running": script_id in _direct_running_ids(),
                }
            )
    return sorted(out, key=lambda x: x["id"])


def _kill_pid(pid: int) -> bool:
    """Kill process by PID. Windows: taskkill; else SIGTERM."""
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                timeout=5,
            )
        else:
            os.kill(pid, signal.SIGTERM)
        return True
    except Exception:
        return False


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


def _enrich_scriptlet_categories(items: list[Any]) -> list[dict[str, Any]]:
    """Ensure each scriptlet dict has category; fill from depot @category when bridge omits it."""
    out: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        d = dict(raw)
        if not str(d.get("category") or "").strip():
            sid = str(d.get("id") or d.get("name") or "").strip().removesuffix(".ahk")
            if sid:
                path = _depot_path(sid)
                if path.exists():
                    meta = _read_metadata(path)
                    d["category"] = (meta.get("category") or "general").strip() or "general"
        if not str(d.get("category") or "").strip():
            d["category"] = "general"
        out.append(d)
    return out


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


def _enrich_scriptlet_row(script_id: str) -> dict[str, Any]:
    path = _depot_path(script_id)
    meta = _read_metadata(path) if path.exists() else {}
    hk = str(meta.get("hotkeys") or meta.get("hotkey") or "").strip()
    return {
        "script_id": script_id,
        "name": meta.get("name") or script_id,
        "description": (meta.get("description") or "")[:800],
        "hotkeys": hk,
        "category": (meta.get("category") or "general").strip() or "general",
    }


async def get_running_overview() -> dict[str, Any]:
    """Direct PIDs + bridge-reported running rows, with depot metadata (hotkeys, description)."""
    _prune_dead_instances()
    instances: list[dict[str, Any]] = []
    for inst in _running_instances:
        sid = str(inst["script_id"])
        row = _enrich_scriptlet_row(sid)
        row["pid"] = int(inst["pid"])
        row["source"] = "direct"
        instances.append(row)
    try:
        data = await _bridge_get("/scriptlets")
        raw_list = (
            data
            if isinstance(data, list)
            else (data.get("scriptlets", []) if isinstance(data, dict) else [])
        )
        if isinstance(raw_list, list):
            enriched = _enrich_scriptlet_categories(raw_list)
            for item in enriched:
                if not isinstance(item, dict) or not item.get("running"):
                    continue
                sid = str(item.get("id") or item.get("name") or "").strip().removesuffix(".ahk")
                if not sid:
                    continue
                row = _enrich_scriptlet_row(sid)
                row["pid"] = None
                row["source"] = "bridge"
                instances.append(row)
    except Exception:
        pass
    return {
        "instances": instances,
        "bridge_url": BRIDGE_URL,
        "direct_tracked": len(_running_instances),
    }


def register_scriptlet_tools(mcp: FastMCP) -> None:
    """Register scriptlet tools, generate/refine/list_prompts, ahk_help, show_help."""

    @mcp.tool()
    async def list_scriptlets() -> dict[str, Any]:
        """
        List all AutoHotkey scriptlets. Uses bridge (10744) when available; else scans depot directly.
        Returns id, name, description, category, running.
        """
        try:
            data = await _bridge_get("/scriptlets")
        except httpx.RequestError:
            scriptlets = _list_scriptlets_direct()
            return {
                "scriptlets": scriptlets,
                "source": "depot",
                "bridge_unavailable": True,
                "depot": str(DEPOT),
            }
        if isinstance(data, list):
            enriched = _enrich_scriptlet_categories(data)
            return {"scriptlets": enriched, "bridge_url": BRIDGE_URL}
        raw_list = data.get("scriptlets", []) if isinstance(data, dict) else []
        if not isinstance(raw_list, list):
            raw_list = []
        return {"scriptlets": _enrich_scriptlet_categories(raw_list), "bridge_url": BRIDGE_URL}

    @mcp.tool()
    async def run_scriptlet(script_id: str) -> dict[str, Any]:
        """
        Run a scriptlet by id (e.g. quick_notes). Uses bridge when available; else runs AHK directly and tracks PID.
        """
        script_id = script_id.strip().removesuffix(".ahk")
        try:
            out = await _bridge_get_text(f"/run/{script_id}.ahk")
            return {"success": True, "message": out, "script_id": script_id, "source": "bridge"}
        except httpx.RequestError:
            pass
        path = _depot_path(script_id)
        if not path.exists():
            return {"success": False, "error": f"Script not found: {path}", "script_id": script_id}
        ahk = _find_ahk_exe()
        if not ahk:
            return {
                "success": False,
                "error": "AutoHotkey not found. Set AUTOHOTKEY_EXE or install AHK v2.",
                "script_id": script_id,
            }
        try:
            proc = await asyncio.create_subprocess_exec(
                ahk,
                str(path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                cwd=str(path.parent),
            )
            _running_instances.append({"script_id": script_id, "pid": proc.pid, "source": "direct"})
            return {
                "success": True,
                "message": "Started (direct)",
                "script_id": script_id,
                "pid": proc.pid,
                "source": "direct",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "script_id": script_id}

    @mcp.tool()
    async def stop_scriptlet(script_id: str, pid: int | None = None) -> dict[str, Any]:
        """
        Stop a running scriptlet. **Direct runs:** kills tracked PID(s); pass ``pid`` to stop one instance when
        several copies of the same script are running. **Bridge:** uses COM bridge stop when no direct match.
        """
        script_id = script_id.strip().removesuffix(".ahk")
        global _running_instances
        _prune_dead_instances()
        if pid is not None:
            matches = [
                i for i in _running_instances if i["script_id"] == script_id and i["pid"] == pid
            ]
        else:
            matches = [i for i in _running_instances if i["script_id"] == script_id]
        if matches:
            killed: list[int] = []
            for t in matches:
                if _kill_pid(int(t["pid"])):
                    killed.append(int(t["pid"]))
            dead = set(killed)
            _running_instances = [i for i in _running_instances if int(i["pid"]) not in dead]
            return {
                "success": len(killed) > 0,
                "message": f"Stopped PID(s): {killed}" if killed else "Kill failed",
                "script_id": script_id,
                "pids": killed,
                "source": "direct",
            }
        try:
            out = await _bridge_get_text(f"/stop/{script_id}.ahk")
            return {"success": True, "message": out, "script_id": script_id, "source": "bridge"}
        except httpx.RequestError:
            pass
        return {
            "success": False,
            "error": "Not running or not tracked (no matching PID; bridge unavailable or stop failed)",
            "script_id": script_id,
        }

    @mcp.tool()
    async def list_running_scriptlets() -> dict[str, Any]:
        """
        List **currently running** scriptlets: script id, hotkeys/description from file headers, PID when known
        (direct launch), and whether the row came from the COM bridge or MCP direct run.
        """
        return await get_running_overview()

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
        ctx: Context | None = OptionalCurrentContext(),
    ) -> dict[str, Any]:
        """
        Generate a new AutoHotkey v2 script from a natural-language prompt. Writes ONLY to scriptlets/ai_generated/.

        **Primary:** FastMCP **sampling** (`Context.sample`) when the MCP host supports it (e.g. Cursor).
        **Fallback:** localhost OpenAI-compatible HTTP — `AUTOHOTKEY_LLM_BASE_URL`, `AUTOHOTKEY_LLM_MODEL` (Ollama/LM Studio).
        No file is written on failure.

        filename: optional base name without .ahk (sanitized). Review output before moving to the main depot.
        """
        return await generate_ahk_script_to_file(prompt, filename, AI_GENERATED_DIR, ctx)

    @mcp.tool()
    async def list_generation_prompts(category: str | None = None) -> dict[str, Any]:
        """
        List built-in preset prompts for `generate_scriptlet` (categories: hotkeys, gui, clipboard, files, …).
        Each entry has id, title, category, tags, and prompt text.
        """
        items = prompt_catalog.get_prompts(category=category)
        return {
            "prompts": [
                {
                    "id": p["id"],
                    "title": p.get("title"),
                    "category": p.get("category"),
                    "tags": p.get("tags") or [],
                    "prompt": p.get("prompt"),
                }
                for p in items
            ],
            "categories": prompt_catalog.categories(),
        }

    @mcp.tool()
    async def refine_ahk_prompt(
        rough: str,
        persona_id: str | None = None,
        ctx: Context | None = OptionalCurrentContext(),
    ) -> dict[str, Any]:
        """
        Turn a vague idea into a clear prompt for `generate_scriptlet`. Same LLM path as generation:
        **FastMCP sampling first**, localhost HTTP if sampling is unavailable.

        persona_id: optional — one of the web personas (e.g. ahk_expert, teacher) to bias tone; omit for neutral.
        """
        extra = personas_mod.persona_system(persona_id)
        return await refine_generation_prompt(rough, ctx, persona_system_extra=extra)

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
            "message": f"Open {mini_help_url} for mini-help. Full webapp (Overview, Help, Chat, Scriptlets, Running, Status): {full_webapp_url} (run web_sota/start.ps1).",
        }
