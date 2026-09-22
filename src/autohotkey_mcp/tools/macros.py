"""Macro SOP tools: list/get/upsert/delete //trigger macros used by macro_expander.ahk.

The SOP file (``sop/macros.md`` in the script depot) is the single source of truth
for both the AHK scriptlet (which polls its mtime and auto-reloads) and these MCP
tools (which edit it). Format: "## name" headings; the body text below each is the
expansion template. {1} {2} ... are positional placeholders filled from
space-separated args typed after the macro name in the //trigger.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP

from autohotkey_mcp.depot import resolve_depot_path

DEPOT = resolve_depot_path()
SOP_PATH = DEPOT / "sop" / "macros.md"

_DEFAULT_PREAMBLE = (
    "# Macro SOP - //trigger definitions for macro_expander.ahk\n\n"
    "Each `## name` heading below is a macro. Typing `//name arg1 arg2` then\n"
    "Tab or Enter (in any app) expands it using the body text as a template.\n\n"
    "- `{1}`, `{2}`, ... are positional parameters, filled from space-separated\n"
    "  args typed after the macro name.\n"
    "- Unused placeholders are stripped if you don't pass enough args.\n"
    "- macro_expander.ahk polls this file's mtime and reloads automatically\n"
    "  within a few seconds of any edit (no restart needed).\n"
)

_NAME_RE = re.compile(r"^[a-z0-9_]+$")


def _parse(content: str) -> tuple[str, dict[str, str]]:
    """Return (preamble, {name: body}) preserving macro insertion order.

    Mirrors macro_expander.ahk's own parser exactly (split on "\\n## ") so both
    sides of this file stay in sync.
    """
    parts = content.split("\n## ")
    preamble = (parts[0].rstrip() + "\n") if parts else _DEFAULT_PREAMBLE
    macros: dict[str, str] = {}
    for block in parts[1:]:
        block = block.strip("\r\n \t")
        if not block:
            continue
        lines = block.split("\n", 1)
        name = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if name:
            macros[name] = body
    return preamble, macros


def _serialize(preamble: str, macros: dict[str, str]) -> str:
    out = preamble.rstrip() + "\n"
    for name, body in macros.items():
        out += f"\n## {name}\n{body}\n"
    return out


def _load() -> tuple[str, dict[str, str]]:
    if not SOP_PATH.exists():
        return _DEFAULT_PREAMBLE, {}
    return _parse(SOP_PATH.read_text(encoding="utf-8"))


def _save(preamble: str, macros: dict[str, str]) -> None:
    SOP_PATH.parent.mkdir(parents=True, exist_ok=True)
    SOP_PATH.write_text(_serialize(preamble, macros), encoding="utf-8")


def register_macro_tools(mcp: FastMCP) -> None:
    """Register macro_list, macro_get, macro_upsert, macro_delete."""

    async def _macro_list() -> dict[str, Any]:
        _, macros = _load()
        items = []
        for name, body in macros.items():
            placeholders = sorted({int(n) for n in re.findall(r"\{(\d+)\}", body)})
            items.append({"name": name, "template": body, "param_count": len(placeholders)})
        return {
            "success": True,
            "macros": items,
            "count": len(items),
            "sop_path": str(SOP_PATH),
        }

    async def _macro_get(name: str) -> dict[str, Any]:
        _, macros = _load()
        name = name.strip().lower()
        if name not in macros:
            return {"success": False, "error": f"Macro '{name}' not found"}
        return {"success": True, "name": name, "template": macros[name]}

    async def _macro_upsert(name: str, template: str) -> dict[str, Any]:
        name = name.strip().lower()
        if not _NAME_RE.match(name):
            return {
                "success": False,
                "error": "name must be lowercase letters, digits, underscore only",
            }
        if not template.strip():
            return {"success": False, "error": "template cannot be empty"}
        preamble, macros = _load()
        created = name not in macros
        macros[name] = template.strip()
        _save(preamble, macros)
        return {"success": True, "name": name, "created": created}

    async def _macro_delete(name: str) -> dict[str, Any]:
        name = name.strip().lower()
        preamble, macros = _load()
        if name not in macros:
            return {"success": False, "deleted": False, "error": f"Macro '{name}' not found"}
        del macros[name]
        _save(preamble, macros)
        return {"success": True, "deleted": True, "name": name}

    @mcp.tool()
    async def macro_ops(
        operation: Literal["list", "get", "upsert", "delete"],
        name: str | None = None,
        template: str | None = None,
    ) -> dict[str, Any]:
        """
        //trigger macro SOP management (portmanteau).

        [RATIONALE]
        Consolidates 4 related operations into a single tool to prevent tool explosion while enabling
        full API coverage (fleet TOOL_DESIGN_STANDARDS.md SS1: portmanteau mandatory above ~20 tools).
        Macros are `//trigger` text-expansion templates used by macro_expander.ahk, stored in
        sop/macros.md (single source of truth, polled and auto-reloaded by the AHK side).

        ## Operations
        - **list**: List all macros with template body and positional {n} placeholder count.
        - **get**: Get one macro's template by name. Requires `name`.
        - **upsert**: Create or update a macro. Requires `name` (lowercase letters/digits/underscore
          only) and `template` (use {1} {2} ... for positional params).
        - **delete**: Delete a macro. Requires `name`.

        ## Return Format
        {"success": bool, ...operation-specific fields}

        ## Examples
        await macro_ops(operation="list")
        await macro_ops(operation="upsert", name="standup", template="Status: {1}. Blockers: {2}.")
        """
        if operation == "list":
            return await _macro_list()
        if operation == "get":
            if not name:
                return {"success": False, "error": "name is required for operation='get'"}
            return await _macro_get(name)
        if operation == "upsert":
            if not name or template is None:
                return {"success": False, "error": "name and template are required for operation='upsert'"}
            return await _macro_upsert(name, template)
        if operation == "delete":
            if not name:
                return {"success": False, "error": "name is required for operation='delete'"}
            return await _macro_delete(name)
        return {"success": False, "error": f"Unknown operation: {operation!r}"}
