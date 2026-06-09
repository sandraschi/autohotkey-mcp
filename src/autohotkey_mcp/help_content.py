"""
Multilevel AutoHotkey v2 help content for ahk_help tool and /help webapp.
Levels: quick | reference | language | usage | tools | mcp_server

Each level is a full Markdown document — headings, code blocks, tables, prose.
Rendered in the webapp Help page and in show_ahk_help_card() prefab tool.
"""

# ─────────────────────────────────────────────────────────────────────────────
# QUICK
# ─────────────────────────────────────────────────────────────────────────────

QUICK = """\
# AutoHotkey v2 — Quick Reference

## What Is AutoHotkey?

AutoHotkey (AHK) is a free Windows scripting language for automation. Scripts
are plain `.ahk` files that react to hotkeys, window events, or timers and can
control the keyboard, mouse, GUI, files, clipboard, COM objects, and HTTP.
**v2** is the current branch — cleaner syntax, proper functions, strict typing
compared to legacy v1.

## This MCP Server

**autohotkey-mcp** lets your AI assistant manage scriptlets:

- List, run, stop scriptlets from the depot (`autohotkey-test`)
- Inspect source and header metadata
- AI-generate new AHK v2 scripts (FastMCP sampling → Ollama/LM Studio fallback)
- Refine vague ideas into precise AHK prompts
- Six rich Prefab UI cards when called from Claude Desktop / Cursor

**Ports:** Backend `10746` · Webapp `10747` · ScriptletCOMBridge `10744`

## Three Things to Know About v2

1. **`#Requires AutoHotkey v2.0+`** at the top of every script — no exceptions.
2. **Function call syntax everywhere.** `MsgBox("text", "Title", "OK")` not `MsgBox, text`.
3. **No `::hotkey::` label syntax.** Use `Hotkey("^!c", MyFn)`.

## Minimal Working Script

```ahk
; @name: Hello World
; @description: Pops a message on Ctrl+Alt+H
; @version: 1.0.0
; @category: productivity
; @hotkeys: Ctrl+Alt+H
#Requires AutoHotkey v2.0+
#SingleInstance Force

OnError(LogErrors)

Hotkey("^!h", ShowHello)

ShowHello(*) {
    MsgBox("Hello from AHK v2!", "Hi", "Icon!")
}

LogErrors(e, *) {
    FileAppend("[" FormatTime(A_Now) "] " e.Message "`n", A_ScriptDir "\errors.log")
}
```

## v1 → v2 Cheat Sheet

| v1 | v2 |
|----|----|
| `^!c::` | `Hotkey("^!c", MyFn)` |
| `Gui, Add, Edit` | `gui.Add("Edit", ...)` |
| `Random, out, 1, 100` | `out := Random(1, 100)` |
| `StringUpper, out, in` | `out := StrUpper(in)` |
| `FileSelectFolder, out` | `out := DirSelect()` |
| `MsgBox, 4, Title, msg` | `MsgBox("msg", "Title", "YesNo")` |
| `MsgBox timeout T10` | Use `TrayTip` or `SetTimer` |
| `for i := 1 to N` | `Loop N { i := A_Index }` |
| `%var%` in strings | Bare `var` or concatenation |

## Hotkey Modifier Symbols

| Symbol | Key |
|--------|-----|
| `^` | Ctrl |
| `!` | Alt |
| `+` | Shift |
| `#` | Win |
| `*` | Wildcard (any modifier) |
| `~` | Don't block original key |
| `$` | Hook (prevents self-send) |
"""

# ─────────────────────────────────────────────────────────────────────────────
# REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

REFERENCE = """\
# AutoHotkey v2 — Language Reference

## Directives

```ahk
#Requires AutoHotkey v2.0+     ; mandatory — reject v1 runtime
#SingleInstance Force           ; replace prior instance on re-run
#Include relative\\path.ahk     ; include another file
#Warn All, Off                  ; suppress specific warning classes
```

## Variables & Types

```ahk
x := 42                 ; integer
y := 3.14               ; float
s := "hello"            ; string
arr := [1, 2, 3]        ; Array (1-based index)
m := Map("a", 1, "b", 2); Map
obj := {x: 10, y: 20}  ; plain Object
```

Arrays and Maps are objects — methods like `arr.Push(4)`, `arr.Length`,
`m.Has("a")`, `m.Delete("b")`, `m.Count`.

## Functions

```ahk
; Basic
Greet(name, greeting := "Hello") {
    return greeting " " name
}

; Variadic
Sum(nums*) {
    total := 0
    for n in nums
        total += n
    return total
}

; Fat-arrow (single expression)
Double := (x) => x * 2
```

## Classes

```ahk
class Counter {
    static instances := 0
    __New(start := 0) {
        this.count := start
        Counter.instances++
    }
    Increment(by := 1) {
        this.count += by
        return this
    }
    __Delete() {
        ; destructor
    }
}

c := Counter(10)
c.Increment().Increment(5)
MsgBox(c.count)  ; 16
```

## Hotkeys

```ahk
; Named function — supports try/catch, complex logic
Hotkey("^!c", CopyPath)
CopyPath(*) {
    try {
        A_Clipboard := WinGetTitle("A")
        TrayTip("Copied!", "AHK", "1")
    } catch e {
        MsgBox("Error: " e.Message)
    }
}

; Inline lambda — only for very short actions
Hotkey("^!r", (*) => Reload())

; Suspend all hotkeys
Hotkey("^!s", (*) => Suspend())
```

## Hotstrings

```ahk
; Basic replacement
:*:btw::by the way

; With options: case-sensitive (*), no-end-char (?)
:*?C:HTML::HyperText Markup Language
```

## GUI

```ahk
MyGui := Gui("+Resize", "My App")
MyGui.SetFont("s10", "Segoe UI")

edit := MyGui.Add("Edit", "w300 h150 vUserText")
btn  := MyGui.Add("Button", "w100 Default", "Submit")

btn.OnEvent("Click", Submit)
MyGui.OnEvent("Close", (*) => MyGui.Hide())
MyGui.OnEvent("Escape", (*) => MyGui.Hide())
MyGui.Show()

Submit(*) {
    saved := MyGui.Submit(false)   ; false = keep GUI open
    MsgBox("You typed: " saved.UserText)
}
```

**Common controls:** `Text`, `Edit`, `Button`, `Checkbox`, `Radio`,
`DropDownList`, `ListBox`, `ListView`, `TreeView`, `StatusBar`,
`Progress`, `Slider`, `Tab3`, `GroupBox`, `Picture`.

## Strings

```ahk
StrLen(s)                    ; length
SubStr(s, 2, 4)              ; position 2, 4 chars
StrReplace(s, "old", "new")  ; replace all
InStr(s, "find")             ; 0 if not found
StrUpper(s) / StrLower(s)
Trim(s) / LTrim(s) / RTrim(s)
StrSplit("a,b,c", ",")       ; returns Array

; Format (like printf)
s := Format("{1} has {:d} items ({:.2f}%)", name, n, pct)

; RegEx
if RegExMatch(s, "(\d+)", &m)
    MsgBox("Found: " m[1])
s2 := RegExReplace(s, "\s+", "_")
```

## Files & Folders

```ahk
; Read entire file
content := FileRead("D:\\data.txt", "UTF-8")

; Write
fh := FileOpen("out.txt", "w", "UTF-8")
fh.Write("Hello`n")
fh.Close()

; Append
FileAppend("line`n", "log.txt")

; Delete / Move / Copy
FileDelete("old.txt")
FileMove("a.txt", "b.txt", true)   ; true = overwrite
FileCopy("src.txt", "dst.txt", true)

; Folder dialog
chosen := DirSelect("*" A_MyDocuments, 3, "Pick a folder")

; Loop files
Loop Files "D:\\scripts\\*.ahk", "R" {  ; R = recursive
    MsgBox(A_LoopFilePath)
}
```

## Timers

```ahk
SetTimer(CheckClip, 2000)      ; repeat every 2s
SetTimer(CheckClip, -1000)     ; fire once after 1s
SetTimer(CheckClip, 0)         ; disable

CheckClip() {
    if A_Clipboard != last {
        last := A_Clipboard
        TrayTip("Clipboard changed", "AHK")
    }
}
```

## Error Handling

```ahk
OnError(GlobalHandler)

GlobalHandler(e, *) {
    FileAppend("[" FormatTime(A_Now) "] " e.Message " @ " e.File ":" e.Line "`n",
               A_ScriptDir "\\errors.log")
    return 1   ; return 1 = suppress default error dialog
}

; Local try/catch
try {
    result := DoRiskyThing()
} catch OSError as e {
    MsgBox("OS error " e.Number ": " e.Message)
} catch as e {
    MsgBox("Error: " e.Message)
} finally {
    Cleanup()
}
```

## Built-in Variables (Selected)

| Variable | Value |
|----------|-------|
| `A_ScriptDir` | Directory of the running script |
| `A_ScriptName` | Filename of the running script |
| `A_AppData` | `%APPDATA%` |
| `A_Desktop` | User desktop path |
| `A_MyDocuments` | My Documents path |
| `A_Temp` | Temp directory |
| `A_Now` | Current datetime `YYYYMMDDHHmmss` |
| `A_TickCount` | Milliseconds since boot |
| `A_Clipboard` | Current clipboard text |
| `A_Index` | Current Loop iteration (1-based) |
| `A_AhkPath` | Path to AutoHotkey executable |
| `A_IsAdmin` | 1 if running as administrator |
| `A_ComputerName` | Machine name |
| `A_UserName` | Windows username |
"""

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE
# ─────────────────────────────────────────────────────────────────────────────

LANGUAGE = """\
# AutoHotkey v2 — Language Deep Dive

## Control Flow

```ahk
; if / else if / else
if (x > 10) {
    DoThing()
} else if (x > 0) {
    DoOther()
} else {
    Fallback()
}

; Ternary
label := (score >= 50) ? "pass" : "fail"

; Switch (no fall-through by default)
switch key {
case "a": ActionA()
case "b", "c": ActionBC()
default: MsgBox("Unknown: " key)
}
```

## Loops

```ahk
; Count loop
Loop 5 {
    MsgBox("Iteration " A_Index)
}

; While
while (queue.Length > 0) {
    item := queue.Pop()
    Process(item)
}

; Until (do-while equivalent)
Loop {
    result := TryConnect()
    if result
        break
    Sleep(1000)
}

; For-in (Array)
fruits := ["apple", "banana", "cherry"]
for i, fruit in fruits
    ToolTip(i ": " fruit, , , i)

; For-in (Map)
ages := Map("Alice", 30, "Bob", 25)
for name, age in ages
    FileAppend(name ": " age "`n", "out.txt")

; Parse string
for word in StrSplit("one two three", " ")
    MsgBox(word)

; Files
Loop Files A_Desktop "\\*.txt" {
    FileAppend(A_LoopFileName "`n", "list.txt")
}

; Subfolders only
Loop Files "D:\\Projects\\*", "D" {
    MsgBox("Dir: " A_LoopFileName)
}
```

## Functions In Depth

```ahk
; Default parameters
Connect(host, port := 80, tls := false) {
    ; ...
}

; ByRef — modify caller's variable
Swap(&a, &b) {
    tmp := a
    a := b
    b := tmp
}
x := 1, y := 2
Swap(&x, &y)   ; x=2, y=1

; Closures (capture outer variables)
MakeCounter(start) {
    count := start
    return () => ++count
}
inc := MakeCounter(0)
MsgBox(inc())  ; 1
MsgBox(inc())  ; 2

; Returning multiple values via Map
GetStats(arr) {
    total := 0
    for v in arr
        total += v
    return Map("sum", total, "avg", total / arr.Length, "count", arr.Length)
}
stats := GetStats([10, 20, 30])
MsgBox("avg=" stats["avg"])
```

## Object-Oriented Patterns

```ahk
class EventEmitter {
    __New() {
        this._handlers := Map()
    }
    On(event, fn) {
        if !this._handlers.Has(event)
            this._handlers[event] := []
        this._handlers[event].Push(fn)
        return this
    }
    Emit(event, data?) {
        if this._handlers.Has(event)
            for fn in this._handlers[event]
                fn(data?)
    }
}

; Inheritance
class Animal {
    __New(name) {
        this.name := name
    }
    Speak() => MsgBox(this.name " says something")
}

class Dog extends Animal {
    Speak() => MsgBox(this.name " says Woof!")
}
d := Dog("Rex")
d.Speak()
```

## COM & Windows Integration

```ahk
; Shell operations
shell := ComObject("Shell.Application")
shell.Open("D:\\Projects")

; WScript.Shell — run and get output
wsh := ComObject("WScript.Shell")
exec := wsh.Exec("cmd /c dir /b C:\\")
output := exec.StdOut.ReadAll()

; Internet Explorer / MSHTML automation (legacy)
ie := ComObject("InternetExplorer.Application")
ie.Visible := true
ie.Navigate("https://example.com")

; Word automation
word := ComObject("Word.Application")
word.Visible := true
doc := word.Documents.Add()
doc.Content.Text := "Hello from AHK v2"
doc.SaveAs2("D:\\test.docx")
word.Quit()
```

## Window Management

```ahk
; Activate, wait, check
WinActivate("Notepad")
WinWaitActive("Notepad", , 3)   ; wait up to 3s

; Get/set properties
title := WinGetTitle("A")       ; active window
hwnd  := WinExist("Notepad")
WinMove(100, 100, 800, 600, hwnd)
WinSetAlwaysOnTop(true, hwnd)
WinMinimize(hwnd)
WinMaximize(hwnd)
WinRestore(hwnd)

; Send keystrokes to a window
WinActivate("Notepad")
Send("Hello, World!{Enter}")
Send("^s")                      ; Ctrl+S

; Control interaction (direct, no focus needed)
ControlSetText("Edit1", "New content", "Notepad")
ControlClick("Button1", "MyApp")
text := ControlGetText("Edit1", "Notepad")
```

## Clipboard

```ahk
; Read
data := A_Clipboard

; Write
A_Clipboard := "New content"
ClipWait(2)   ; wait up to 2s for clipboard to fill

; Monitor changes
OnClipboardChange(ClipChanged)
ClipChanged(type) {
    if type = 1   ; text
        ToolTip("Clipboard: " SubStr(A_Clipboard, 1, 40))
}
```

## Process & System

```ahk
; Run a process
Run "notepad.exe"
Run "cmd /c dir", "C:\\", "Hide"

; Run and wait
RunWait "msiexec /i setup.msi", , "Hide"

; Environment
path := EnvGet("PATH")
EnvSet("MY_VAR", "hello")

; System info
MsgBox("CPU: " A_ComputerName " | Admin: " A_IsAdmin)

; ProcessExist / ProcessClose
if ProcessExist("notepad.exe")
    ProcessClose("notepad.exe")

; Shutdown / reboot
; Shutdown(1)   ; 1=logoff, 2=shutdown, 4=reboot, 8=force
```

## Sending Input

```ahk
; Keyboard
Send("{LCtrl down}c{LCtrl up}")   ; Ctrl+C (explicit)
Send("^c")                          ; Ctrl+C (shorthand)
Send("Hello{Enter}World{Tab}!")
Send("{F5}")
Send("{Blind}^z")                   ; Blind mode — keep current modifiers

; With delay
SendMode "Event"
SetKeyDelay(50, 50)
Send("slow typing")

; Mouse
Click(500, 300)                     ; left click at x,y
Click("Right", 500, 300)            ; right click
MouseMove(500, 300, 10)             ; move (speed 10)
MouseClickDrag("Left", 0, 0, 100, 100)
```
"""

# ─────────────────────────────────────────────────────────────────────────────
# USAGE
# ─────────────────────────────────────────────────────────────────────────────

USAGE = """\
# AutoHotkey v2 — Scriptlet Authoring Guide

## Script Header Convention

Every scriptlet in the depot must have a metadata header block. The MCP server
reads these fields for the list, detail, and generate tools.

```ahk
; @name: Quick Notes
; @description: Floating sticky-note window, Ctrl+Alt+N to toggle
; @version: 1.0.0
; @category: productivity
; @hotkeys: Ctrl+Alt+N
#Requires AutoHotkey v2.0+
#SingleInstance Force
```

**Required fields:** `@name`, `@description`, `@category`  
**Recommended:** `@version`, `@hotkeys`  
**Categories:** `hotkeys` `gui` `clipboard` `files` `windows` `strings`
`system` `productivity` `games` `testing` `network` `ai_generated` `general`

## Boilerplate Template

```ahk
; @name: My Scriptlet
; @description: One-sentence description of what it does
; @version: 1.0.0
; @category: productivity
; @hotkeys: Ctrl+Alt+X
#Requires AutoHotkey v2.0+
#SingleInstance Force

; Error handler — always include
OnError(LogErrors)

; ── Main ──────────────────────────────────────────────────────────────────────

Hotkey("^!x", MainAction)

MainAction(*) {
    try {
        ; your code here
        TrayTip("Done!", A_ScriptName, "1")
    } catch as e {
        LogErrors(e)
    }
}

; ── Error logging ─────────────────────────────────────────────────────────────

LogErrors(e, *) {
    logDir := A_ScriptDir "\\logs"
    if !DirExist(logDir)
        DirCreate(logDir)
    FileAppend(
        "[" FormatTime(A_Now, "yyyy-MM-dd HH:mm:ss") "] "
        e.Message " @ " e.File ":" e.Line "`n",
        logDir "\\" A_ScriptName ".log"
    )
    return 1   ; suppress error dialog
}
```

## GUI Scriptlets

For scripts that show a window:

```ahk
; @name: Clipboard Transformer
; @description: Transform clipboard text (upper/lower/title case)
; @version: 1.0.0
; @category: clipboard
; @hotkeys: Ctrl+Alt+T
#Requires AutoHotkey v2.0+
#SingleInstance Force

OnError(LogErrors)

global gGui := ""

Hotkey("^!t", ToggleGui)

ToggleGui(*) {
    if IsObject(gGui) && gGui.Hwnd {
        if WinExist("ahk_id " gGui.Hwnd)
            gGui.Hide()
        else
            gGui.Show()
        return
    }
    BuildGui()
}

BuildGui() {
    global gGui
    gGui := Gui("+AlwaysOnTop", "Clipboard Transformer")
    gGui.SetFont("s10", "Segoe UI")
    gGui.Add("Text", "w200", "Transform clipboard:")
    gGui.Add("Button", "w90", "UPPER").OnEvent("Click", (*) => Transform("upper"))
    gGui.Add("Button", "xp+95 w90", "lower").OnEvent("Click", (*) => Transform("lower"))
    gGui.Add("Button", "x10 w90", "Title Case").OnEvent("Click", (*) => Transform("title"))
    gGui.OnEvent("Close", (*) => gGui.Hide())
    gGui.OnEvent("Escape", (*) => gGui.Hide())
    gGui.Show("w210")
}

Transform(mode) {
    text := A_Clipboard
    result := mode = "upper" ? StrUpper(text)
            : mode = "lower" ? StrLower(text)
            : StrTitle(text)
    A_Clipboard := result
    TrayTip("Transformed!", "Clipboard", "1")
}

LogErrors(e, *) {
    FileAppend("[" FormatTime(A_Now) "] " e.Message "`n", A_ScriptDir "\\errors.log")
    return 1
}
```

## Hotkey-Only Scriptlets

For scripts with no GUI — keep them lean:

```ahk
; @name: Window Snap Left
; @description: Snap active window to left half of screen
; @version: 1.0.0
; @category: windows
; @hotkeys: Win+Left (supplements built-in with monitor awareness)
#Requires AutoHotkey v2.0+
#SingleInstance Force

OnError(LogErrors)

Hotkey("#Left", SnapLeft)

SnapLeft(*) {
    hwnd := WinExist("A")
    mon  := MonitorGet(MonitorGetPrimary())
    ; use SysGet for work area (excludes taskbar)
    MonitorGetWorkArea(MonitorGetPrimary(), &left, &top, &right, &bottom)
    w := (right - left) // 2
    h := bottom - top
    WinMove(left, top, w, h, hwnd)
}

LogErrors(e, *) {
    FileAppend("[" FormatTime(A_Now) "] " e.Message "`n", A_ScriptDir "\\errors.log")
    return 1
}
```

## Escape Hatch Pattern (Games / Loops)

Any script with a long-running loop must have an escape hatch:

```ahk
Hotkey("F9", (*) => ExitApp())    ; emergency stop
Hotkey("F10", (*) => Pause(-1))   ; pause/resume
```

## ai_generated/ Sandbox

Scripts generated by `generate_scriptlet` land in `scriptlets/ai_generated/`.

**Before using:**
1. Read the source — look for unexpected `Run`, `Send`, `FileDelete`
2. Check `@category` and hotkeys don't conflict with system shortcuts
3. Test in a VM or sandbox session if in doubt
4. Promote to `scriptlets/` only after review

The depot's `ai_generated/README.md` summarises the review process.

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `^!c::` label syntax | `Hotkey("^!c", MyFn)` |
| `MsgBox timeout T10` | `TrayTip(...)` or `SetTimer((*) => ToolTip(), -3000)` |
| `gui.Add` without gui object | `myGui := Gui(); myGui.Add(...)` |
| `StrReplace` as command | `s := StrReplace(s, "a", "b")` |
| Bare `python` in `Run` | `Run "cmd /c python script.py"` with full path |
| `Loop, 10` (v1 syntax) | `Loop 10` |
| `%var%` dereferencing | Bare `var` in expressions |
| `OutputVar` as first param | All builtins return values now |

## Performance Tips

- Use `SetTimer` for polling, not busy `Loop`
- Prefer `ControlClick`/`ControlSend` over `Send` when target window known
- Use `Critical` sparingly (blocks all messages)
- `Sleep(0)` yields to other scripts without sleeping
- For file I/O in loops, open once and close after: `FileOpen` → loop → `Close()`
"""

# ─────────────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────────────

TOOLS = """\
# autohotkey-mcp — Tool Reference

## Scriptlet Management

### list_scriptlets()

Returns all scriptlets in the depot with metadata.

**Source priority:** ScriptletCOMBridge (port 10744) → depot scan fallback  
**Returns:** Array of `{id, name, description, category, running, path}`

```json
[
  {
    "id": "quick_notes",
    "name": "quick notes",
    "description": "Floating sticky-note window",
    "category": "productivity",
    "running": false
  }
]
```

### run_scriptlet(script_id)

Run a scriptlet by its id (filename stem without `.ahk`).

**Bridge mode:** `GET /run/{script_id}.ahk` on 10744  
**Direct mode:** Spawns `AutoHotkey64.exe scriptlets/{id}.ahk`, tracks PID

```
run_scriptlet("quick_notes")
→ {"success": true, "pid": 12345, "source": "direct"}
```

### stop_scriptlet(script_id, pid?)

Stop a running scriptlet. Pass `pid` when multiple instances of the same
script are running under direct (non-bridge) mode.

```
stop_scriptlet("quick_notes")          → stops first match
stop_scriptlet("quick_notes", 12345)   → stops specific PID
```

### list_running_scriptlets()

Returns all currently active scriptlet instances with metadata.

```json
[
  {
    "script_id": "quick_notes",
    "pid": 12345,
    "source": "direct",
    "hotkeys": "Ctrl+Alt+N",
    "description": "Floating sticky-note window"
  }
]
```

### get_scriptlet_source(script_id)

Read the full `.ahk` source from depot. Checks `scriptlets/` then
`scriptlets/ai_generated/`. Never uses bridge.

### get_scriptlet_metadata(script_id)

Read `@key: value` header fields from the file. Returns a dict of all
recognised metadata fields (`name`, `description`, `version`, `category`,
`hotkeys`, plus any custom fields).

---

## AI Generation

### generate_scriptlet(prompt, filename?)

Generate a new AHK v2 script from a natural-language prompt.

**Path 1 — FastMCP sampling:** When called from Cursor or Claude Desktop,
uses the host LLM via `ctx.sample()`. This is the preferred path — no
local model required.

**Path 2 — Localhost HTTP:** Falls back to `AUTOHOTKEY_LLM_BASE_URL` 
(default: Ollama on port 11434) when sampling is unavailable.

**Output:** Written to `scriptlets/ai_generated/{filename}.ahk` only
after validation. Nothing written on failure. Returns `script_id` of
the saved file.

```
generate_scriptlet(
  "Hotkey Ctrl+Alt+P that pastes the current date in ISO format"
)
→ {"success": true, "script_id": "paste_iso_date", "path": "..."}
```

**Review generated scripts before running** — see the Usage tab.

### refine_ahk_prompt(rough, persona_id?)

Turn a vague idea into a precise, unambiguous prompt ready for
`generate_scriptlet`. Useful when you know what you want but can't
phrase it technically.

```
refine_ahk_prompt("make a thing that keeps my screen awake")
→ "Create an AHK v2 scriptlet that prevents screensaver/sleep by
   sending a harmless keypress (e.g. Shift) every 4 minutes using
   SetTimer. Include a tray menu to enable/disable. Category: system."
```

### list_generation_prompts(category?)

Returns the built-in prompt catalog — 40+ preset ideas with id, title,
tags, and the full prompt text. Filter by category or browse all.

Categories: `productivity`, `system`, `clipboard`, `windows`, `gui`,
`games`, `files`, `mcp`, `fun`

---

## Help

### ahk_help(level?, topic?)

Return help documentation as Markdown.

| Level | Content |
|-------|---------|
| `quick` | Overview, cheat sheet, hotkey symbols |
| `reference` | Full syntax: variables, GUI, strings, files, timers, errors |
| `language` | Control flow, closures, OOP, COM, window/process management |
| `usage` | Scriptlet authoring guide, templates, common mistakes |
| `tools` | This page — all MCP tools with examples |
| `mcp_server` | Server config, ports, env vars, Claude Desktop setup |

### show_help()

Returns clickable URLs for the mini-help page (`/help`) and the full
webapp (`http://127.0.0.1:10747`).

---

## Prefab UI Cards (Claude Desktop / Cursor)

When called from an MCP host that renders Prefab UI, these six tools
produce rich interactive cards. From the webapp they return plain text
and raw JSON.

| Tool | Card type | Content |
|------|-----------|---------|
| `show_scriptlets_card()` | DataTable | All scriptlets: Dot status, Badge category, search, paginate |
| `show_running_scriptlets_card()` | Dashboard + DataTable | Metric KPIs + live instance table |
| `show_ahk_help_card(level)` | Tabs + Markdown | All 6 help levels in tabbed view |
| `show_scriptlet_detail_card(id)` | Code + Badges + Kbd | Full source, metadata, hotkey chips |
| `show_generation_result_card(id)` | Code + warning | Generated script with safety banner |
| `show_server_status_card()` | Dashboard + DataTable | KPIs + config table |

---

## MCP Prompts

Five `@mcp.prompt()` conversation starters available in Claude Desktop:

| Prompt | Use case |
|--------|----------|
| `generate_ahk_scriptlet(description)` | Full v2 generation system prompt |
| `refine_ahk_idea(rough_idea)` | Sharpen a vague request |
| `debug_ahk_script(source, error?)` | Diagnose and fix a script |
| `migrate_v1_to_v2(v1_source)` | Full v1→v2 migration with annotations |
| `review_ahk_for_safety(source)` | RED/YELLOW/GREEN safety report |

---

## REST API (Webapp)

The backend at `http://127.0.0.1:10746` also exposes these endpoints
for the SPA and for direct use:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | `{"ok": true}` |
| GET | `/api/scriptlets` | Same as list_scriptlets |
| GET | `/api/running` | Same as list_running_scriptlets |
| GET | `/api/scriptlet/:id` | Source + metadata for one scriptlet |
| POST | `/api/run_scriptlet` | `{"script_id": "..."}` |
| POST | `/api/stop_scriptlet` | `{"script_id": "..."}` |
| GET | `/api/help` | All help levels as `{"levels": {...}}` |
| POST | `/api/chat` | SSE streaming chat (Ollama/LM Studio) |
| POST | `/api/generate_scriptlet` | HTTP generate (no MCP sampling) |
| POST | `/tool` | `{"name": "...", "arguments": {...}}` — call any MCP tool |
"""

# ─────────────────────────────────────────────────────────────────────────────
# MCP_SERVER
# ─────────────────────────────────────────────────────────────────────────────

MCP_SERVER = """\
# autohotkey-mcp — Server Configuration

## Architecture

```
Claude Desktop / Cursor (MCP host)
    │  stdio transport (auto-detected when stdin is a pipe)
    ▼
autohotkey-mcp  (FastMCP 3.2.4)
    ├── 16 MCP tools
    ├── 5 MCP prompts  (@mcp.prompt)
    ├── 3 MCP resources  (ahk://prompts/*)
    ├── SkillsDirectoryProvider  (.cursor/skills/)
    │
    ├── FastAPI HTTP  :10746
    │   ├── /api/*  REST endpoints for SPA
    │   ├── /tool   POST bridge (name + arguments)
    │   ├── /help   mini HTML help page (no npm needed)
    │   └── /health, /status
    │
    └── Vite React SPA  :10747
        ├── Overview (dashboard cards)
        ├── Help (tabbed Markdown)
        ├── Chat (streaming, personas, presets)
        ├── Scriptlets (list + search)
        ├── Scriptlets/:id (detail, run/stop)
        ├── Running (live instances, kill)
        ├── Prefab Tools (invoke all 6 tools)
        └── Status (server health)

ScriptletCOMBridge.ahk  :10744  (autohotkey-test)
    ├── GET /scriptlets → JSON array
    ├── GET /run/:name  → spawn .ahk
    ├── GET /stop/:name → kill .ahk
    └── GET /dashboard  → HTML UI
```

## Start

```powershell
# Full webapp (backend + SPA, opens browser)
.\\web_sota\\start.ps1

# Or via fleet starts:
D:\\Dev\\repos\\mcp-central-docs\\starts\\autohotkey-mcp-start.bat

# Backend only (MCP stdio auto-detected)
uv run autohotkey-mcp

# justfile recipes
just run      # backend only
just web      # backend + frontend
just lint     # ruff check + format check
just test     # pytest
just health   # curl /health
```

## Cursor / Claude Desktop Configuration

```json
{
  "mcpServers": {
    "autohotkey-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "D:/Dev/repos/autohotkey-mcp",
        "run",
        "autohotkey-mcp"
      ]
    }
  }
}
```

When stdin is a pipe (Cursor, Claude Desktop), the server **automatically
runs stdio-only** — no HTTP, no port 10746 bind. Set
`AUTOHOTKEY_MCP_HTTP=0` to force stdio-only when running from a terminal.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTOHOTKEY_SCRIPT_DEPOT` | `d:/dev/repos/autohotkey-test` | Root of the AHK depot (must contain `scriptlets/`) |
| `AUTOHOTKEY_BRIDGE_URL` | `http://127.0.0.1:10744` | ScriptletCOMBridge base URL |
| `AUTOHOTKEY_EXE` | (auto-detect) | Path to `AutoHotkey64.exe` for direct runs |
| `AUTOHOTKEY_MCP_HTTP` | (auto) | `0` = force stdio-only |
| `PORT` | `10746` | Backend HTTP port |
| `AUTOHOTKEY_LLM_BASE_URL` | `http://127.0.0.1:11434/v1` | OpenAI-compatible chat endpoint (Ollama / LM Studio) |
| `AUTOHOTKEY_LLM_MODEL` | `llama3.2` | Model id for completions |
| `AUTOHOTKEY_LLM_API_KEY` | (unset) | Bearer token (also reads `OPENAI_API_KEY`) |
| `AUTOHOTKEY_LLM_TIMEOUT` | `120` | HTTP completion timeout (seconds) |
| `AUTOHOTKEY_PREFAB_APPS` | `1` | `0` = disable Prefab tool registration |
| `AUTOHOTKEY_SKILLS_DIR` | `.cursor/skills` | Override SkillsDirectoryProvider root |

## LLM Generation Architecture

```
generate_scriptlet(prompt)
    │
    ├─► ctx.sample() via FastMCP  ← preferred path in Cursor/Claude Desktop
    │       Uses host LLM (Claude, GPT-4, etc.) — no local model needed
    │       Falls back if ctx unavailable or sampling fails
    │
    └─► AUTOHOTKEY_LLM_BASE_URL   ← fallback: local HTTP
            Ollama:    http://127.0.0.1:11434/v1
            LM Studio: http://127.0.0.1:1234/v1
            Any OpenAI-compatible endpoint

On failure (both paths fail or script validation fails):
    → nothing written to disk, error returned to caller
```

**Recommended local models for AHK generation:**
- `qwen2.5-coder:14b` — best code quality at moderate size
- `deepseek-coder-v2:16b` — strong on structured code
- `llama3.2:3b` — fast, adequate for simple scriptlets
- `qwen3.5:27b` — Sandra's fleet sweet spot (~40 tok/s on 4090)

## MCP Resources

Agents and tools that support MCP resources can read the prompt catalog:

```
ahk://prompts/catalog          → full JSON array of all preset prompts
ahk://prompts/categories       → ["productivity","system","clipboard",...]
ahk://prompts/{id}             → single preset or {"error":"not found"}
```

## Health & Monitoring

```powershell
# Health check
curl http://127.0.0.1:10746/health
# {"ok": true, "service": "autohotkey-mcp", "port": 10746}

# Status page
curl http://127.0.0.1:10746/status

# Mini HTML help (no SPA required)
Start-Process http://127.0.0.1:10746/help

# Check bridge
curl http://127.0.0.1:10744/status
```

## Fleet Registration

- **WEBAPP_PORTS.md:** 10744 (bridge), 10746 (backend), 10747 (frontend)
- **FLEET_INDEX.md:** `autohotkey-mcp` — AHK Scriptlet Hub v0.2.0
- **starts/:** `autohotkey-mcp-start.bat`, `autohotkey-test-start.bat`
- **glama.json:** marketplace metadata at repo root
- **llms.txt / llms-full.txt:** agent-readable documentation

## Depot: autohotkey-test

The scriptlet depot is a separate repo at `D:\\Dev\\repos\\autohotkey-test`.

```
autohotkey-test/
├── ScriptletCOMBridge.ahk   HTTP bridge on :10744
├── start.bat / start.ps1    fleet-standard launcher
├── scriptlets/              75+ .ahk files
│   ├── ai_generated/        MCP-generated scripts (sandbox)
│   ├── games/               Snake, Tetris, Chess, etc.
│   └── ...
├── utils/                   linter, batch debugger
└── docs/                    syntax guide, bugbash reports
```

Start the depot: `D:\\Dev\\repos\\mcp-central-docs\\starts\\autohotkey-test-start.bat`

When the bridge is running, `list_scriptlets` / `run_scriptlet` /
`stop_scriptlet` route through it. When it's not, autohotkey-mcp scans
the depot directly and spawns AHK via subprocess.

`get_scriptlet_source` and `get_scriptlet_metadata` **always** read
from disk — they do not go through the bridge.

## Related Servers

| Tool | What it does | When to pick this one |
|------|-------------|----------------------|
| **autohotkey-mcp** (here — 10746/10747) | AHK scriptlet depot — list, run, stop, generate `.ahk` scripts. Shows "CUA at work" HUD while scriptlets run. | You have a **depot of AHK scripts** or need **raw low-level recording/replay** via AHK's built-in recorder. Best for legacy apps, games, or custom hotkey macros. |
| **pywinauto-mcp** (10788/10789) | Native Windows UI automation via UIA element tree + OCR + screenshots. Shows "CUA at work" HUD during `analyze_winapp` and `global_keylogger`. | You need to **inspect controls, click buttons, read text** from modern Windows apps. Best when the app exposes a UIA accessibility tree. |
| **windows-operations-mcp** (10748/10749) | PowerShell + system management | You need OS-level operations (processes, registry, files). |
| **robofang** (10870-10872) | Fleet supervisor — can orchestrate autohotkey-mcp via `/tool` bridge | You want scheduled / event-driven AHK script execution. |

**How to choose:**
- Need to **record mouse/keyboard and replay**? → AHK's built-in recorder + `autohotkey-mcp run_scriptlet`
- Need to **read text from a window, click a button by its automation ID**? → `pywinauto-mcp automation_elements`
- Need to **crawl an unknown app's UI tree**? → `pywinauto-mcp analyze_winapp`
- Both show a **"CUA at work"** HUD (blinking red overlay + e-stop button) during operations so you know when automation is active.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Registry & helpers
# ─────────────────────────────────────────────────────────────────────────────

LEVELS: dict[str, str] = {
    "quick": QUICK,
    "reference": REFERENCE,
    "language": LANGUAGE,
    "usage": USAGE,
    "tools": TOOLS,
    "mcp_server": MCP_SERVER,
}

FULL_MD = "\n\n---\n\n".join(LEVELS.values())


def get_help(level: str = "quick", topic: str | None = None) -> str:
    """Return help content for level. topic reserved for future subsection filter."""
    key = (level or "quick").strip().lower()
    if key not in LEVELS:
        return f"Unknown level: {level!r}. Available: {', '.join(LEVELS.keys())}"
    out = LEVELS[key]
    if topic:
        out = out + f"\n\n*(Topic filter: {topic} — not yet applied.)*"
    return out


def get_all_levels() -> dict[str, str]:
    return dict(LEVELS)
