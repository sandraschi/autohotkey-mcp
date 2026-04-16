"""LLM-backed AHK generation: **primary** = FastMCP sampling; **fallback** = localhost HTTP; one validation retry."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from fastmcp.server.context import Context

from autohotkey_mcp.ahk_llm import (
    AHK_GENERATOR_SYSTEM,
    extract_ahk_source,
    validate_generated_ahk,
)
from autohotkey_mcp.dual_llm import complete_dual_path

logger = logging.getLogger(__name__)

# Type alias for FastMCP dependency injection
ContextType = Context | None


def _safe_stem(filename: str | None, prompt: str) -> str:
    base = (filename or prompt)[:80]
    safe = re.sub(r"[^\w\-]", "_", base).strip("_")
    return safe or "generated"


async def generate_ahk_script_to_file(
    prompt: str,
    filename: str | None,
    ai_generated_dir: Path,
    ctx: ContextType = None,
) -> dict[str, Any]:
    """
    Generate AHK v2 source: **FastMCP sampling first** (when ``ctx`` is the MCP session), then localhost HTTP.
    Writes only under ai_generated_dir. ``ctx`` is None for the REST SPA (HTTP-only).
    """
    prompt = (prompt or "").strip()
    if len(prompt) < 3:
        return {
            "success": False,
            "error": "prompt must be a non-empty description of what the script should do",
        }

    stem = _safe_stem(filename, prompt)
    base = f"{stem}.ahk"
    ai_generated_dir.mkdir(parents=True, exist_ok=True)
    root = ai_generated_dir.resolve()
    path = (root / base).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return {"success": False, "error": "Invalid filename (path escape)"}

    raw, gen_src = await complete_dual_path(
        prompt, ctx, AHK_GENERATOR_SYSTEM, temperature=0.3, max_tokens=8192
    )
    if not raw:
        return {
            "success": False,
            "error": "No LLM output. **Preferred:** use an MCP host with **FastMCP sampling** (e.g. Cursor). "
            "**Otherwise:** set AUTOHOTKEY_LLM_BASE_URL (e.g. http://127.0.0.1:11434/v1) and "
            "AUTOHOTKEY_LLM_MODEL and run Ollama or LM Studio locally (used when sampling is unavailable).",
            "hint": "No placeholder file is written on failure.",
        }

    code = extract_ahk_source(raw)
    ok, verr = validate_generated_ahk(code)

    if not ok:
        retry_user = (
            f"Fix this AutoHotkey v2 script.\nValidation error: {verr}\n\n"
            f"---\n{code}\n---\nOutput only the full corrected script with #Requires AutoHotkey v2.0 "
            f"and metadata lines ; @description: … ; @category: ai_generated …"
        )
        raw2, gen2 = await complete_dual_path(
            retry_user,
            ctx,
            AHK_GENERATOR_SYSTEM,
            temperature=0.2,
            max_tokens=8192,
        )
        if raw2:
            code = extract_ahk_source(raw2)
            ok, verr = validate_generated_ahk(code)
            if gen2:
                gen_src = gen2

    if not ok:
        return {
            "success": False,
            "error": f"Generated output failed validation: {verr}",
            "preview": code[:1200] if code else None,
            "hint": "Try a clearer prompt or a stronger model; no file was written.",
        }

    path.write_text(code, encoding="utf-8")
    return {
        "success": True,
        "path": str(path),
        "script_id": stem,
        "generation_source": gen_src or "unknown",
        "warning": "Review before moving to main scriptlets/. Untrusted scripts can harm your machine.",
    }
