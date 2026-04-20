"""LLM completion: **primary** = FastMCP 3.1 `Context.sample` (host / MCP client LLM).

**Fallback** = localhost OpenAI-compatible HTTP (Ollama, LM Studio, etc.) via `AUTOHOTKEY_LLM_*`.
Used for script generation, prompt refinement, and any tool that needs a model when sampling is unavailable
(e.g. HTTP-only SPA or headless runs).
"""

from __future__ import annotations

import logging
from fastmcp.server.context import Context

from autohotkey_mcp.ahk_llm import complete_via_http, http_llm_available

logger = logging.getLogger(__name__)


async def complete_dual_path(
    user_text: str,
    ctx: Context | None,
    system: str,
    *,
    temperature: float = 0.3,
    max_tokens: int = 8192,
) -> tuple[str | None, str | None]:
    """Return (text, source) where source is ``\"sampling\"`` | ``\"http\"`` | None.

    **Order (intentional):**

    1. **FastMCP sampling** — when ``ctx`` is present, call ``ctx.sample`` first. This is the
       intended path for Cursor, Claude Desktop, and other MCP hosts that expose the client's LLM.
    2. **Local HTTP** — only if sampling did not return text (no context, unsupported host, error,
       or empty response) *and* ``http_llm_available()`` is true.

    Local HTTP is not a "second-class" model in quality terms; it is the **offline / SPA / API**
    path when there is no MCP sampling session.
    """
    raw: str | None = None
    src: str | None = None
    text_in = user_text.strip()

    if ctx is not None:
        try:
            result = await ctx.sample(
                messages=text_in,
                system_prompt=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = getattr(result, "text", None)
            if not (isinstance(text, str) and text.strip()):
                alt = getattr(result, "result", None)
                if isinstance(alt, str) and alt.strip():
                    text = alt
            if isinstance(text, str) and text.strip():
                raw = text.strip()
                src = "sampling"
        except Exception as e:
            logger.warning(
                "FastMCP sampling unavailable or failed (trying localhost HTTP if configured): %s",
                e,
            )

    if raw is None and http_llm_available():
        try:
            raw = await complete_via_http(system, text_in)
            src = "http"
        except Exception as e:
            logger.warning("Local HTTP LLM failed: %s", e)

    return raw, src
