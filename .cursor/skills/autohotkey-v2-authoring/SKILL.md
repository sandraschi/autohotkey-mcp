---
name: autohotkey-v2-authoring
description: Author safe, idiomatic AutoHotkey v2 scripts for Windows automation — hotkeys, GUI, clipboard, files, and MCP autohotkey-mcp workflows (FastMCP sampling + local Ollama).
---

# AutoHotkey v2 authoring (autohotkey-mcp)

Use this skill when writing or reviewing **AutoHotkey v2** scripts, especially for **autohotkey-mcp** (`generate_scriptlet`, `refine_ahk_prompt`, depot layout).

## Non‑negotiables

- **Version:** `#Requires AutoHotkey v2.0` — never emit v1 command syntax (`Gui, Add`, `::` hotkey labels as primary style, etc.).
- **Headers:** Prefer metadata comments: `; @description:`, `; @version:`, `; @category:`, `; @hotkeys:` when sharing scriptlets.
- **Safety:** Do not implement keyloggers, credential theft, or hidden remote control. Refuse and suggest a safe alternative.
- **Execution:** Avoid `Run` with unsanitized user text; avoid arbitrary shell from prompt-controlled strings.

## Idioms (v2)

- **Hotkeys:** `Hotkey("^!c", myFunc)` or named functions — not legacy `^c::` blocks for new code.
- **GUI:** `myGui := Gui()`, `myGui.Add("Text", …)`, `myGui.OnEvent("Close", …)`, `myGui.Show()`.
- **Strings:** `StrSplit`, `StrReplace`, `RegExMatch`, `RegExReplace`; `A_Clipboard` for clipboard.
- **Timing:** `SetTimer`, `Sleep` sparingly; prefer event-driven GUI/hotkey flow.
- **Errors:** `try`/`catch` or `OnError` for non-trivial scripts; log to `scriptlets/logs/` when appropriate.

## autohotkey-mcp LLM paths

1. **Primary (MCP):** **FastMCP 3.1 `Context.sample`** — use from Cursor/compatible hosts for `generate_scriptlet` / `refine_ahk_prompt`. This is the intended “main course” for generation.
2. **Fallback / SPA:** **Local OpenAI-compatible HTTP** — `AUTOHOTKEY_LLM_BASE_URL` (e.g. `http://127.0.0.1:11434/v1`), `AUTOHOTKEY_LLM_MODEL` — Ollama, LM Studio. Used when sampling is unavailable (HTTP API, web SPA generate/chat).

## MCP resources (prompt catalog)

Agents can **read resources** (no tool call): `ahk://prompts/catalog` (full JSON), `ahk://prompts/categories`, `ahk://prompts/{prompt_id}` (e.g. `ahk://prompts/hk_toggle_mute`).

## Workflow

1. **Ideate:** Call `list_generation_prompts`, read `ahk://prompts/catalog`, or browse the webapp **Chat** presets.
2. **Refine:** `refine_ahk_prompt` on vague ideas; paste result into `generate_scriptlet`.
3. **Generate:** `generate_scriptlet` writes only under `scriptlets/ai_generated/` after validation.
4. **Review:** Read source with `get_scriptlet_source`; move to main `scriptlets/` only after trust checks.
5. **Run:** `run_scriptlet` / bridge — never run unreviewed generated code on sensitive accounts.

## Output expectations for generators

When the model must output code, wrap only AHK in markdown fences if needed; start with `#Requires AutoHotkey v2.0` and metadata lines as required by the MCP server validator.

## Quick checklist before “done”

- [ ] v2-only syntax; `#Requires` present  
- [ ] No unsafe `Run`/network exfiltration  
- [ ] Hotkeys documented or obvious  
- [ ] Tested at least with a dry run / MsgBox smoke path  
