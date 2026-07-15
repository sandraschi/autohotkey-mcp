# autohotkey-mcp (MCPB Bundle)

MCP server for AutoHotkey v2 scriptlets: list, run, stop, source/metadata, AI generation (sampling), prefab UI cards, MCP prompts. Uses ScriptletCOMBridge and autohotkey-test repo as depot.

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "autohotkey-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "autohotkey_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **list_scriptlets**: list_scriptlets

## Requirements

- Python 3.12+
- uv
