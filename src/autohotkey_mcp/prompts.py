"""MCP Prompts for autohotkey-mcp (FastMCP 3.2 @mcp.prompt()).

These are conversation starters / instruction sets that MCP hosts can surface
to users or use as system instructions. Distinct from the generation prompt catalog
(prompt_catalog.py), which is a library of ready-to-use scriptlet idea prompts.
"""

from __future__ import annotations

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts for autohotkey-mcp."""

    @mcp.prompt()
    def generate_ahk_scriptlet(description: str) -> str:
        """
        Scaffold a complete AutoHotkey v2 scriptlet from a natural-language description.
        Use this prompt to generate a production-ready .ahk file for the scriptlet depot.
        """
        return f"""You are an AutoHotkey v2 expert generating a scriptlet for the autohotkey-test depot.

Generate a complete, working AutoHotkey v2 script for: {description}

## Requirements

**Header block** (required at top of every scriptlet):
```
; @name: <Human-readable name>
; @description: <One sentence>
; @version: 1.0.0
; @category: <hotkeys|gui|clipboard|files|windows|strings|system|productivity|games|testing|network>
; @hotkeys: <e.g. Ctrl+Alt+C or none>
#Requires AutoHotkey v2.0+
#SingleInstance Force
```

**v2 rules** (no exceptions):
- `Hotkey("^!c", FnName)` not `^!c::`
- `MsgBox("text", "title", "Icon!")` — 3 params, no timeout in v2 (use TrayTip)
- `StrUpper(s)` / `StrLower(s)` not `.ToUpper()`
- `out := Random(1, 100)` not `Random, out, 1, 100`
- `Loop N {{ }}` not `Loop, N`
- `DirSelect()` not `FileSelectFolder`
- `gui.Add(...)` not `Gui, Add`
- `OnError(LogErrors)` for error handling

**Structure**:
1. Header block
2. `OnError(LogErrors)` registration
3. Main logic / hotkeys / GUI
4. `LogErrors(e, *) {{ ... }}` function at end

Output only the complete .ahk source code. No markdown fences, no explanation outside comments.
"""

    @mcp.prompt()
    def refine_ahk_idea(rough_idea: str) -> str:
        """
        Turn a vague AHK automation idea into a clear, detailed prompt for generate_scriptlet.
        Use before calling generate_scriptlet when the request is underspecified.
        """
        return f"""You are an AutoHotkey v2 expert helping clarify a scriptlet request.

Rough idea: {rough_idea}

Transform this into a precise, unambiguous prompt for AutoHotkey v2 scriptlet generation.

Your refined prompt should specify:
1. **Trigger**: what activates it (hotkey, startup, timer, GUI button, etc.)
2. **Action**: exactly what it does, step by step
3. **GUI**: if any, describe controls (Edit, Button, ListBox, etc.)
4. **Edge cases**: what happens if the target window is missing, clipboard is empty, etc.
5. **Category**: one of hotkeys/gui/clipboard/files/windows/strings/system/productivity/games/testing/network

Output only the refined prompt text — concise, specific, ready to pass to generate_scriptlet.
"""

    @mcp.prompt()
    def debug_ahk_script(script_source: str, error_message: str = "") -> str:
        """
        Diagnose and fix an AutoHotkey v2 script. Provide source and optional error message.
        Returns corrected source with inline comments explaining each fix.
        """
        error_section = f"\n\n**Error reported:**\n```\n{error_message}\n```" if error_message else ""
        return f"""You are an AutoHotkey v2 expert debugging a script.{error_section}

**Script to debug:**
```ahk
{script_source}
```

## Debugging checklist

**Common v1→v2 issues:**
- `Gui, Add` → `gui.Add()`
- `::hotkey::` → `Hotkey("hotkey", FnName)`
- `Random, out, 1, 100` → `out := Random(1, 100)`
- `StringUpper/Lower` → `StrUpper/StrLower()`
- `MsgBox timeout (T10)` → remove or use TrayTip
- `FileSelectFolder` → `DirSelect()`
- `for i := 1 to N` → `Loop N {{ i := A_Index }}`
- Missing `*` in error handler: `OnError(fn)` where `fn(e, *)` has variadic param

**Check also:**
- `#Requires AutoHotkey v2.0+` present
- All functions defined before or after use (v2 is fine either way)
- GUI: `OnEvent("Close", (*) => gui.Hide())` not `Gui, +Label`
- Hotkeys: named function references (not inline lambdas with try/catch)

Output the corrected script source (with `; FIX:` comments) followed by a brief summary of what was changed.
"""

    @mcp.prompt()
    def migrate_v1_to_v2(v1_source: str) -> str:
        """
        Migrate an AutoHotkey v1 script to v2. Returns complete v2 source with migration notes.
        """
        return f"""You are an AutoHotkey expert migrating a v1 script to v2.

**v1 source to migrate:**
```ahk
{v1_source}
```

## Migration rules (apply all)

| v1 | v2 |
|----|----|
| `^!c::` (hotkey label) | `Hotkey("^!c", MyFn)` + `MyFn(*) {{ ... }}` |
| `Gui, Add, Edit` | `gui := Gui(); gui.Add("Edit", ...)` |
| `Gui, Show` | `gui.Show()` |
| `Gui, Destroy` | `gui.Destroy()` |
| `GuiControl, , CtrlVar, val` | `ctrl.Value := val` |
| `StringUpper, out, in` | `out := StrUpper(in)` |
| `StringLower, out, in` | `out := StrLower(in)` |
| `Random, out, lo, hi` | `out := Random(lo, hi)` |
| `FileSelectFolder, out` | `out := DirSelect()` |
| `FileSelectFile, out` | `out := FileSelect()` |
| `for i := 1 to N` | `Loop N {{ i := A_Index }}` |
| `MsgBox, 4, Title, msg` | `MsgBox("msg", "Title", "YesNo")` |
| `IfMsgBox Yes` | `if (result = "Yes")` after `result := MsgBox(...)` |
| `MsgBox timeout T10` | remove or replace with `SetTimer(() => ..., -10000)` |
| `%var%` in strings | `var` directly or `"text" var "text"` |
| `EnvGet, out, VAR` | `out := EnvGet("VAR")` |
| `SplitPath, path, ...` | `SplitPath(path, &name, &dir, ...)` |

Output the complete migrated v2 script with:
1. `; @migrated-from: v1` in header
2. `#Requires AutoHotkey v2.0+`
3. `; MIGRATED:` comments on changed lines
4. A brief changelog at top listing key changes made
"""

    @mcp.prompt()
    def review_ahk_for_safety(script_source: str) -> str:
        """
        Review an AutoHotkey v2 script for security and safety concerns before adding to the depot.
        """
        return f"""You are a security-aware AutoHotkey v2 reviewer.

**Script to review:**
```ahk
{script_source}
```

## Safety review checklist

**RED FLAGS (refuse or strongly warn):**
- Keylogging: `Input`, `InputHook` capturing passwords or sensitive data
- Credential harvesting: reading browser/app password stores
- Network exfiltration: sending user data to remote servers without consent
- `RunAs` escalation without clear purpose
- `BlockInput` for extended periods
- Registry writes to sensitive keys (Run, RunOnce, services)
- Downloading and executing code: `URLDownloadToFile` + `Run`

**YELLOW FLAGS (require comment/justification):**
- `Run` with external executables
- File deletion without confirmation
- Reading files from user profile / AppData
- Clipboard reads in background timers
- Hotkeys that interfere with system shortcuts (Win+L, etc.)

**GREEN (common safe patterns):**
- Window management, always-on-top, snapping
- Clipboard transforms (read → transform → write)
- GUI launchers with explicit user action
- Text expansion via hotstrings
- Audio controls via SoundSet

Provide a structured report:
1. **Risk level**: LOW / MEDIUM / HIGH / CRITICAL
2. **Issues found** (list each with line reference if possible)
3. **Recommendations** (specific fixes or warnings to add)
4. **Verdict**: APPROVE / APPROVE WITH CHANGES / REJECT
"""
