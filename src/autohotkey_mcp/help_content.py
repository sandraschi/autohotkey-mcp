"""
Multilevel AutoHotkey v2 help content for ahk_help tool and /help webapp.
Levels: quick | reference | language | usage | tools | mcp_server
"""

QUICK = """# AutoHotkey v2 – Quick
- **Script depot**: autohotkey-test repo (scriptlets/). Bridge: ScriptletCOMBridge.ahk on port 10744.
- **This MCP**: list/run/stop scriptlets, get source/metadata, optional AI generate (sandbox). Port 10746.
- **v2 only**: Use `#Requires AutoHotkey v2.0+`. No v1 syntax. Hotkey() not ::, MsgBox("msg","title","Icon!"), StrUpper/StrLower, Loop/for-in.
- **Docs**: GET http://127.0.0.1:10746/help for full web help."""

REFERENCE = """# AutoHotkey v2 – Reference
**Directives**: #Requires AutoHotkey v2.0+, #SingleInstance Force, #Include path
**GUI**: Gui(), gui.Add("Text"|"Button"|"Edit", options, text), gui.Show(), SetFont(), OnEvent("Click", callback), ObjBindMethod(Class, "Method")
**Hotkeys**: Hotkey("^!c", (*) => Fn()), Hotkey("^!v", NamedFn); use named function for try/catch
**Loops**: Loop N { }, Loop Parse str, delim, for i, v in arr, for i in Range(1,10)
**Strings**: StrLen, SubStr, StrReplace, StrUpper, StrLower, InStr, RegExMatch
**Files**: FileRead(path), FileOpen(path,"w","UTF-8").Write(text), DirSelect()
**Time**: FormatTime(&out, A_Now, "yyyy-MM-dd HH:mm:ss"), A_Now
**MsgBox**: MsgBox("Message","Title","Icon!") — no timeout in v2; use TrayTip for timed
**Timers**: SetTimer(callback, ms), SetTimer(callback, -ms) once, SetTimer(callback, 0) off
**Errors**: OnError(LogError), try/catch
**v1→v2 quick**: Gui, Add → gui.Add; Random, out, 1, 100 → out := Random(1,100); for i:=1 to 10 → Loop 10 { i := A_Index }; ^!c:: → Hotkey("^!c", Fn); FileSelectFolder → DirSelect(); .ToUpper() → StrUpper()"""

LANGUAGE = """# AutoHotkey v2 – Language
**Types**: String, Integer, Float, Array (arr := []), Map (m := Map()), Object, Buffer, Func, Class.
**Variables**: global by default in top level; use `local` in functions. Static in classes.
**Functions**: MyFn(param1, param2 := "default") { }, return value. Variadic: rest* or arr*.
**Classes**: class Name { static x := 1; Method() { } }, ObjBindMethod(Class, "Method").
**Operators**: := assignment, = comparison (in expressions), . concat, + - * / // **, && || !, in, has.
**Hotkey symbols**: ^ Ctrl, ! Alt, + Shift, # Win. Example: "^!c" = Ctrl+Alt+C.
**v1→v2**: Command syntax removed (use function calls). Gui, Add → gui.Add. Random, out, 1, 100 → out := Random(1,100). for i:=1 to 10 → Loop 10 { i := A_Index }. FileSelectFolder → DirSelect(). ^!c:: → Hotkey("^!c", Fn). MsgBox timeout (T10) does not exist in v2 — use TrayTip or ToolTip."""

USAGE = """# AutoHotkey v2 – Usage (scriptlets)
**Script header**: #Requires AutoHotkey v2.0+; @name, @description, @version, @hotkeys, @category in comments.
**Error handling**: OnError(LogError), log to scriptlets\\logs\\<name>.log.
**GUI**: Use Gui(), Add(), OnEvent("Close"|"Escape", Hide). No blocking MsgBox with timeout; use TrayTip/ToolTip.
**Hotkeys**: Prefer named functions for multi-statement or try/catch. F9 escape hatch for loops/games.
**Bridge**: ScriptletCOMBridge.ahk serves /run/<id>.ahk, /stop/<id>.ahk, /scriptlets, /status on 127.0.0.1:10744. Dashboard: /dashboard.
**Checklist**: #Requires v2; OnError; gui.Add not Gui, Add; Hotkey() not ::; value := Random(1,100); Loop/for-in not for i:=1 to 10; MsgBox 3 params only; DirSelect/FileRead/FileOpen; StrUpper/StrLower."""

TOOLS = """# autohotkey-mcp – Tools
- **list_scriptlets()**: List all scriptlets from bridge (id, name, description, category, running).
- **run_scriptlet(script_id)**: Run scriptlet by id (e.g. quick_notes). Calls bridge /run/<id>.ahk.
- **stop_scriptlet(script_id)**: Stop running scriptlet. Calls bridge /stop/<id>.ahk.
- **get_scriptlet_source(script_id)**: Read full .ahk source from depot (scriptlets/ or scriptlets/ai_generated/).
- **get_scriptlet_metadata(script_id)**: Read @description, @version, etc. from file header.
- **generate_scriptlet(prompt, filename?)**: [Dangerous] Write stub to scriptlets/ai_generated/ only. Review before moving to main depot.
- **ahk_help(level?, topic?)**: This help. level: quick | reference | language | usage | tools | mcp_server. topic: optional subsection."""

MCP_SERVER = """# autohotkey-mcp – MCP & Fleet
**Repo**: d:/dev/repos/autohotkey-mcp (standalone; not under RoboFang hands/).
**Port**: 10746. Health: GET http://127.0.0.1:10746/status. Tool: POST /tool with {"name":"...","arguments":{}}.
**Start**: uv run autohotkey-mcp or .\\start.ps1 (kills zombie on 10746).
**Env**: AUTOHOTKEY_BRIDGE_URL (default http://127.0.0.1:10744), AUTOHOTKEY_SCRIPT_DEPOT (default d:/dev/repos/autohotkey-test), PORT.
**Cursor**: Add MCP server with command uv, args ["--directory", "<path>/autohotkey-mcp", "run", "autohotkey-mcp"]. FastMCP 3.1 dual transport: stdio + HTTP on 10746.
**Depot**: ScriptletCOMBridge must be running (autohotkey-test start_dashboard.bat) for list/run/stop. get_source/get_metadata read from depot path."""

LEVELS: dict[str, str] = {
    "quick": QUICK,
    "reference": REFERENCE,
    "language": LANGUAGE,
    "usage": USAGE,
    "tools": TOOLS,
    "mcp_server": MCP_SERVER,
}

# Full markdown for webapp (single doc)
FULL_MD = "\n\n---\n\n".join([QUICK, REFERENCE, LANGUAGE, USAGE, TOOLS, MCP_SERVER])


def get_help(level: str = "quick", topic: str | None = None) -> str:
    """Return help content for level. topic reserved for future subsection filter."""
    key = (level or "quick").strip().lower()
    if key not in LEVELS:
        return f"Unknown level: {level}. Available: " + ", ".join(LEVELS.keys())
    out = LEVELS[key]
    if topic:
        # Optional: filter by topic keyword in content (future)
        out = out + f"\n\n(Topic filter: {topic} – not yet applied.)"
    return out


def get_all_levels() -> dict[str, str]:
    return dict(LEVELS)
