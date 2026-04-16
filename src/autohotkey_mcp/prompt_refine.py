"""Turn rough ideas into clear generation prompts (same dual-path LLM as script generation)."""

from __future__ import annotations

from typing import Any

from fastmcp.server.context import Context

from autohotkey_mcp.dual_llm import complete_dual_path

REFINE_SYSTEM = """You refine rough user ideas into **one** clear prompt for an AutoHotkey **v2** script generator.

Rules:
- Output **only** the refined prompt text (no preamble, no markdown fences).
- English is fine unless the user wrote in another language — match the user's language.
- Include: trigger (hotkey or auto-run), main behavior, important edge cases, and constraints (e.g. no admin).
- Do **not** output AHK source code.
- If the idea is unsafe (keylogging, stealing passwords, hiding malware), refuse briefly and suggest a safe alternative instead of a harmful prompt.
- Keep length under ~1200 characters unless the user needs more detail.
"""


async def refine_generation_prompt(
    rough: str,
    ctx: Context | None,
    *,
    persona_system_extra: str | None = None,
) -> dict[str, Any]:
    """Return success + refined text + source (sampling|http|None)."""
    rough = (rough or "").strip()
    if len(rough) < 3:
        return {"success": False, "error": "rough idea must be at least a few characters"}

    system = REFINE_SYSTEM
    if persona_system_extra and persona_system_extra.strip():
        system = REFINE_SYSTEM + "\n\nVoice / perspective:\n" + persona_system_extra.strip()

    user = (
        f"Rough idea from the user:\n\n{rough}\n\nWrite the single refined generation prompt only."
    )

    text, src = await complete_dual_path(
        user,
        ctx,
        system,
        temperature=0.35,
        max_tokens=2048,
    )
    if not text:
        return {
            "success": False,
            "error": "No LLM output. Use an MCP client with sampling, or configure AUTOHOTKEY_LLM_* for localhost.",
        }

    refined = text.strip()
    return {
        "success": True,
        "refined_prompt": refined,
        "source": src or "unknown",
    }
