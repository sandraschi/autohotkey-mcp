"""Preset prompts for AHK v2 generation and ideation (MCP tools + web SPA)."""

from __future__ import annotations

from typing import Any

# id: stable slug; category: filter key; prompt: passed to generate_scriptlet or chat
PROMPTS: list[dict[str, Any]] = [
    # Hotkeys & input
    {
        "id": "hk_toggle_mute",
        "title": "Global mute toggle",
        "category": "hotkeys",
        "tags": ["audio", "media"],
        "prompt": (
            "Hotkey Win+Shift+M toggles system mute (use whatever API works on Windows without admin; "
            "if not possible, show a MsgBox explaining the limitation)."
        ),
    },
    {
        "id": "hk_paste_plain",
        "title": "Paste clipboard as plain text",
        "category": "hotkeys",
        "tags": ["clipboard"],
        "prompt": (
            "Ctrl+Shift+V pastes the clipboard as plain text (strip formatting): get clipboard, set as text, paste."
        ),
    },
    {
        "id": "hk_always_on_top",
        "title": "Toggle active window always-on-top",
        "category": "hotkeys",
        "tags": ["window"],
        "prompt": "Ctrl+Alt+T toggles always-on-top for the active window.",
    },
    {
        "id": "hk_transparency",
        "title": "Adjust active window transparency",
        "category": "hotkeys",
        "tags": ["window"],
        "prompt": (
            "Hotkeys: Win+Alt+WheelUp / Win+Alt+WheelDown increase/decrease transparency of the active window "
            "(clamp 50–255). Show tooltip with current value."
        ),
    },
    {
        "id": "hk_kill_app",
        "title": "Emergency close foreground app",
        "category": "hotkeys",
        "tags": ["window"],
        "prompt": (
            "Hotkey Ctrl+Alt+Escape kills the foreground process after a confirmation (Yes/No) dialog."
        ),
    },
    # GUI
    {
        "id": "gui_clipboard_history",
        "title": "Simple clipboard history (small GUI)",
        "category": "gui",
        "tags": ["clipboard"],
        "prompt": (
            "A small Gui with a ListBox showing last 10 clipboard text entries (in-memory). "
            "Double-click copies selection back to clipboard and hides the GUI. F1 shows the GUI."
        ),
    },
    {
        "id": "gui_quick_launcher",
        "title": "Quick launcher (list + filter)",
        "category": "gui",
        "tags": ["productivity"],
        "prompt": (
            "Gui with Edit and ListBox: user types to filter a static list of app paths (array in script). "
            "Enter launches selected path with Run."
        ),
    },
    {
        "id": "gui_reminder",
        "title": "One-shot reminder timer",
        "category": "gui",
        "tags": ["timer"],
        "prompt": (
            "Gui: minutes + message + Start. After delay, TrayTip shows the message. Single instance."
        ),
    },
    {
        "id": "gui_color_picker_note",
        "title": "Pixel color under cursor (readout)",
        "category": "gui",
        "tags": ["pixel"],
        "prompt": (
            "Hotkey shows a small Gui with pixel RGB under cursor (update while mouse moves), "
            "Copy button copies hex to clipboard."
        ),
    },
    # Clipboard & text
    {
        "id": "clip_transform",
        "title": "Transform selection: uppercase",
        "category": "clipboard",
        "tags": ["text"],
        "prompt": (
            "Hotkey copies selection, converts to UPPERCASE, pastes back (simulate Ctrl+C, transform, Ctrl+V)."
        ),
    },
    {
        "id": "clip_join_lines",
        "title": "Join lines with comma",
        "category": "clipboard",
        "tags": ["text"],
        "prompt": (
            "Hotkey takes clipboard text, splits lines, trims, joins with ', ' and puts back on clipboard."
        ),
    },
    {
        "id": "clip_strip_empty",
        "title": "Remove empty lines from clipboard",
        "category": "clipboard",
        "tags": ["text"],
        "prompt": "Hotkey removes empty lines from clipboard text and sets clipboard again.",
    },
    # Files & paths
    {
        "id": "file_open_explorer",
        "title": "Open Explorer here",
        "category": "files",
        "tags": ["explorer"],
        "prompt": (
            "Hotkey opens File Explorer in the folder of the active window's file path if available; "
            "otherwise MsgBox."
        ),
    },
    {
        "id": "file_log_append",
        "title": "Append timestamped line to log file",
        "category": "files",
        "tags": ["logging"],
        "prompt": (
            "Hotkey appends one line: ISO timestamp + active window title + optional user note from input box "
            "to script_dir\\logs\\journal.txt (create folder if needed)."
        ),
    },
    {
        "id": "file_rename_serial",
        "title": "Rename files in folder with serial",
        "category": "files",
        "tags": ["batch"],
        "prompt": (
            "Gui: pick folder, prefix string, start number. Renames selected pattern *.txt to prefix0001.txt style "
            "(ask confirmation before rename)."
        ),
    },
    # Window management
    {
        "id": "win_center",
        "title": "Center active window",
        "category": "windows",
        "tags": ["layout"],
        "prompt": "Hotkey centers the active window on the primary monitor (keep size).",
    },
    {
        "id": "win_snap",
        "title": "Snap active window left/right half",
        "category": "windows",
        "tags": ["layout"],
        "prompt": (
            "Win+Alt+Left and Win+Alt+Right snap active window to left/right half of work area."
        ),
    },
    {
        "id": "win_roll",
        "title": "Minimize other windows",
        "category": "windows",
        "tags": ["layout"],
        "prompt": "Hotkey minimizes all windows except the active one (best-effort loop).",
    },
    # Strings & parsing
    {
        "id": "str_regex_replace_gui",
        "title": "Regex find/replace on clipboard",
        "category": "strings",
        "tags": ["regex"],
        "prompt": (
            "Small Gui: pattern, replacement, button Apply — runs RegExReplace on clipboard and show preview."
        ),
    },
    {
        "id": "str_extract_urls",
        "title": "Extract URLs from clipboard",
        "category": "strings",
        "tags": ["regex"],
        "prompt": (
            "Hotkey finds URLs in clipboard text, shows ListBox in Gui, double-click copies one URL."
        ),
    },
    # System & tray
    {
        "id": "sys_tray_menu",
        "title": "Tray menu: reload / exit",
        "category": "system",
        "tags": ["tray"],
        "prompt": (
            "A_IconMenu with Reload, Open script folder, Exit. On startup TrayTip shows script name."
        ),
    },
    {
        "id": "sys_single_instance",
        "title": "Single instance + second instance shows GUI",
        "category": "system",
        "tags": ["instance"],
        "prompt": (
            "#SingleInstance Force. If script already running, show MsgBox 'Already running' and exit."
        ),
    },
    # Productivity
    {
        "id": "prod_date_stamp",
        "title": "Type current date",
        "category": "productivity",
        "tags": ["typing"],
        "prompt": "Hotkey types current date yyyy-MM-dd at caret (use SendText).",
    },
    {
        "id": "prod_block_input_toggle",
        "title": "BlockInput while typing",
        "category": "productivity",
        "tags": ["typing"],
        "prompt": (
            "Demonstrate BlockInput during a short Send sequence (with comment warning about use)."
        ),
    },
    {
        "id": "prod_workspace_switch",
        "title": "Switch to specific window title",
        "category": "productivity",
        "tags": ["window"],
        "prompt": (
            "Hotkey activates first window whose title contains a configurable substring (variable at top). "
            "TrayTip if not found."
        ),
    },
    # Games / input (safe)
    {
        "id": "game_toggle",
        "title": "Suspend hotkeys in fullscreen",
        "category": "games",
        "tags": ["suspend"],
        "prompt": (
            "Hotkey Win+Pause toggles Suspend (so game hotkeys do not fire). TrayTip state."
        ),
    },
    {
        "id": "game_click_burst",
        "title": "Hold to auto-click (toggle)",
        "category": "games",
        "tags": ["mouse"],
        "prompt": (
            "Hotkey toggles a timer that clicks at current position at fixed interval (ms in variable). "
            "Second hotkey stops. Include warning comment about ToS."
        ),
    },
    # Testing / dev
    {
        "id": "dev_hello",
        "title": "Smoke test",
        "category": "testing",
        "tags": ["smoke"],
        "prompt": "Minimal script: MsgBox shows A_AhkVersion and script path.",
    },
    {
        "id": "dev_error_handler",
        "title": "Global OnError logger",
        "category": "testing",
        "tags": ["errors"],
        "prompt": (
            "Register OnError that appends error message + stack to script_dir\\logs\\errors.log."
        ),
    },
    # Networking (user-approved only)
    {
        "id": "net_http_get",
        "title": "Fetch URL to clipboard (simple)",
        "category": "network",
        "tags": ["http"],
        "prompt": (
            "Gui: URL field + Fetch button. Uses ComObject WinHttp.WinHttpRequest.5.1 to GET and put response "
            "text in Edit (HTTPS only). No eval."
        ),
    },
    # Meta
    {
        "id": "meta_refuse_unsafe",
        "title": "Template: refuse unsafe request",
        "category": "meta",
        "tags": ["safety"],
        "prompt": (
            "If user asks for keylogging or password stealing, show MsgBox refusing and exit. "
            "Otherwise MsgBox hello."
        ),
    },
    {
        "id": "meta_template",
        "title": "Script template with header metadata",
        "category": "meta",
        "tags": ["template"],
        "prompt": (
            "A minimal v2 script with #Requires, @description, @version, @category, hotkey F1 shows MsgBox."
        ),
    },
    {
        "id": "mouse_crosshair",
        "title": "Show mouse position in tooltip",
        "category": "hotkeys",
        "tags": ["mouse"],
        "prompt": "Hold hotkey shows ToolTip with mouse screen coordinates; release hides tooltip.",
    },
    {
        "id": "dpi_aware",
        "title": "Note DPI awareness comment",
        "category": "meta",
        "tags": ["dpi"],
        "prompt": (
            "Small script with comment block explaining DPI/coordinates considerations for window placement."
        ),
    },
    {
        "id": "sound_beep_pattern",
        "title": "Beep pattern for timer done",
        "category": "productivity",
        "tags": ["audio"],
        "prompt": "SetTimer fires after 25 minutes and plays three SoundBeep tones in sequence.",
    },
    {
        "id": "monitor_count",
        "title": "MsgBox monitor count",
        "category": "windows",
        "tags": ["monitor"],
        "prompt": "Hotkey shows MsgBox with MonitorCount and primary work area dimensions.",
    },
]


def get_prompts(*, category: str | None = None) -> list[dict[str, Any]]:
    if not category or not str(category).strip():
        return list(PROMPTS)
    c = category.strip().lower()
    return [p for p in PROMPTS if str(p.get("category", "")).lower() == c]


def categories() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for p in PROMPTS:
        cat = str(p.get("category") or "general")
        if cat not in seen:
            seen.add(cat)
            out.append(cat)
    return sorted(out)


def get_prompt_by_id(prompt_id: str) -> dict[str, Any] | None:
    pid = prompt_id.strip().lower()
    for p in PROMPTS:
        if str(p.get("id", "")).lower() == pid:
            return p
    return None


def list_prompts_for_api() -> list[dict[str, Any]]:
    """Public fields for JSON."""
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "category": p.get("category"),
            "tags": p.get("tags") or [],
            "prompt": p["prompt"],
        }
        for p in PROMPTS
    ]
