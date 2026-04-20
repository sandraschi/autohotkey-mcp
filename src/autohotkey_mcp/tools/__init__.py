"""AutoHotkey MCP tools: scriptlets, generation, and prefab UI cards."""

from autohotkey_mcp.tools.scriptlets import register_scriptlet_tools
from autohotkey_mcp.tools.prefab import register_prefab_tools

__all__ = ["register_scriptlet_tools", "register_prefab_tools"]
