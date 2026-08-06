"""AutoHotkey MCP tools: scriptlets, generation, macros, and prefab UI cards."""

from autohotkey_mcp.tools.macros import register_macro_tools
from autohotkey_mcp.tools.prefab import register_prefab_tools
from autohotkey_mcp.tools.scriptlets import register_scriptlet_tools

__all__ = ["register_scriptlet_tools", "register_prefab_tools", "register_macro_tools"]
