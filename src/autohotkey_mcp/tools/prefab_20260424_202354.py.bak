"""Prefab UI tools for autohotkey-mcp.

Fleet-mandatory: list / status / stats surfaces with PrefabApp cards.
Tools in this module use app=True and return ToolResult + PrefabApp.
Registration is controlled by env AUTOHOTKEY_PREFAB_APPS (0 = skip, default on).
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Text

logger = logging.getLogger(__name__)


def _prefab_enabled() -> bool:
    return os.getenv("AUTOHOTKEY_PREFAB_APPS", "1").lower() not in ("0", "false", "no")


def _status_dot(running: bool) -> str:
    return "● " if running else "○ "


def register_prefab_tools(mcp: FastMCP) -> None:
    """Register Prefab App tools. Skipped when AUTOHOTKEY_PREFAB_APPS=0."""

    if not _prefab_enabled():
        logger.info("AUTOHOTKEY_PREFAB_APPS=0 — skipping Prefab tool registration")
        return

    # Import here to avoid circular dep with scriptlets.py
    from autohotkey_mcp.tools.scriptlets import (
        _list_scriptlets_direct,
        _bridge_get,
        _enrich_scriptlet_categories,
        get_running_overview,
    )
    from autohotkey_mcp import help_content
    import httpx

    @mcp.tool(app=True)
    async def show_scriptlets_card() -> ToolResult:
        """
        Show all AutoHotkey scriptlets as a rich Prefab card (list / status view).
        Displays id, name, category, and running state. Uses bridge if available; else depot scan.
        """
        # Fetch scriptlet list (same logic as list_scriptlets)
        try:
            data = await _bridge_get("/scriptlets")
            if isinstance(data, list):
                items = _enrich_scriptlet_categories(data)
            else:
                raw = data.get("scriptlets", []) if isinstance(data, dict) else []
                items = _enrich_scriptlet_categories(raw if isinstance(raw, list) else [])
            source = "bridge"
        except (httpx.RequestError, Exception):
            items = _list_scriptlets_direct()
            source = "depot"

        total = len(items)
        running_count = sum(1 for s in items if s.get("running"))

        # Build plain-text summary (always set for non-Prefab hosts)
        lines = [f"AutoHotkey Scriptlets ({total} total, {running_count} running) [{source}]"]
        for s in items:
            marker = _status_dot(bool(s.get("running")))
            lines.append(f"{marker}{s.get('id', '?')}  [{s.get('category', 'general')}]  {s.get('description', '')[:60]}")
        plain = "\n".join(lines)

        # Build Prefab card
        with Card(css_class="max-w-2xl") as view:
            with CardHeader():
                CardTitle(f"AutoHotkey Scriptlets — {total} total, {running_count} running")
            with CardContent():
                Text(f"Source: {source}")
                for s in items:
                    marker = _status_dot(bool(s.get("running")))
                    cat = s.get("category") or "general"
                    desc = (s.get("description") or "")[:80]
                    sid = s.get("id") or s.get("name") or "?"
                    Text(f"{marker}{sid}  [{cat}]  {desc}")

        return ToolResult(
            content=plain,
            structured_content=PrefabApp(view=view, title="AHK Scriptlets"),
        )

    @mcp.tool(app=True)
    async def show_running_scriptlets_card() -> ToolResult:
        """
        Show currently running AutoHotkey scriptlets as a Prefab card (status surface).
        Includes PID (direct runs), hotkeys, description, and run source (direct/bridge).
        """
        data = await get_running_overview()
        instances: list[dict[str, Any]] = data.get("instances", [])
        count = len(instances)

        # Plain text summary
        if count == 0:
            plain = "No AutoHotkey scriptlets currently running."
        else:
            lines = [f"Running AutoHotkey Scriptlets: {count}"]
            for inst in instances:
                pid_str = f"  PID {inst['pid']}" if inst.get("pid") else ""
                hk = f"  hotkeys: {inst['hotkeys']}" if inst.get("hotkeys") else ""
                lines.append(f"● {inst.get('script_id', '?')}{pid_str}  [{inst.get('source', '?')}]{hk}")
                if inst.get("description"):
                    lines.append(f"  {inst['description'][:100]}")
            plain = "\n".join(lines)

        # Prefab card
        with Card(css_class="max-w-xl") as view:
            with CardHeader():
                CardTitle(f"Running Scriptlets — {count}")
            with CardContent():
                if count == 0:
                    Text("No scriptlets currently running.")
                else:
                    for inst in instances:
                        pid_str = f" PID {inst['pid']}" if inst.get("pid") else ""
                        src = inst.get("source") or "?"
                        sid = inst.get("script_id") or "?"
                        Text(f"● {sid}{pid_str}  [{src}]")
                        if inst.get("hotkeys"):
                            Text(f"  Hotkeys: {inst['hotkeys']}")
                        if inst.get("description"):
                            Text(f"  {inst['description'][:100]}")

        return ToolResult(
            content=plain,
            structured_content=PrefabApp(view=view, title="Running AHK Scriptlets"),
        )

    @mcp.tool(app=True)
    async def show_ahk_help_card(level: str = "quick") -> ToolResult:
        """
        Show AutoHotkey v2 help as a Prefab card. level: quick | reference | language | usage | tools | mcp_server.
        """
        text = help_content.get_help(level=level)
        available = list(help_content.LEVELS.keys())

        plain = f"AHK Help [{level}]\n\n{text}"

        with Card(css_class="max-w-2xl") as view:
            with CardHeader():
                CardTitle(f"AutoHotkey v2 Help — {level}")
            with CardContent():
                Text(f"Available levels: {', '.join(available)}")
                # Split into chunks so each paragraph is a separate Text node
                for chunk in text.split("\n"):
                    if chunk.strip():
                        Text(chunk)

        return ToolResult(
            content=plain,
            structured_content=PrefabApp(view=view, title=f"AHK Help: {level}"),
        )
