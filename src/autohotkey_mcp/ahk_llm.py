"""Local LLM completion for AHK generation — OpenAI-compatible API, localhost-only (SSRF-safe)."""

from __future__ import annotations

import json
import os
import re
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import urlparse

import httpx

DEFAULT_BASE = os.getenv("AUTOHOTKEY_LLM_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")
DEFAULT_MODEL = os.getenv("AUTOHOTKEY_LLM_MODEL", "llama3.2")
DEFAULT_TIMEOUT = float(os.getenv("AUTOHOTKEY_LLM_TIMEOUT", "120"))


def allowed_llm_base(url: str) -> bool:
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            return False
        h = (p.hostname or "").lower()
        return h in ("127.0.0.1", "localhost", "::1")
    except Exception:
        return False


def resolve_base() -> str:
    raw = DEFAULT_BASE.strip().rstrip("/")
    if not allowed_llm_base(raw):
        raise ValueError(
            f"AUTOHOTKEY_LLM_BASE_URL must be http(s)://127.0.0.1, localhost, or ::1 (got {raw!r})",
        )
    return raw


AHK_GENERATOR_SYSTEM = """You are an expert AutoHotkey **v2** script author. Output **only** valid AHK v2 source code.

Hard rules:
- Start with a line exactly: `#Requires AutoHotkey v2.0`
- Include a comment header block with these lines (semicolon prefix):
  - `; @description: <one line>`
  - `; @category: ai_generated`
  - `; @version: 1.0.0`
  - `; @generated_by: autohotkey-mcp`
- Use **v2 syntax only** (not v1). Prefer `MsgBox("text")`, `Hotkey("F1", myFunc)`, functions with `=>` where appropriate.
- Do **not** embed network calls to arbitrary URLs unless the user explicitly asked for HTTP; prefer local automation.
- Do **not** use `Run` to launch `powershell`/`cmd` with user-controlled strings from the prompt in a dangerous way — keep scripts self-contained.
- If the request is impossible or unsafe, output a minimal script that shows `MsgBox("Cannot safely fulfill: ...", "autohotkey-mcp")` and explains in the @description.
- Output **nothing** outside the script: no markdown fences unless you need them — if you use ``` fences, put only AHK inside.

After the header, implement what the user asked. Keep scripts short and readable."""


def extract_ahk_source(raw: str) -> str:
    """Pull AHK from model output (strip markdown fences)."""
    text = raw.strip()
    fence = re.search(r"```(?:ahk|autoit|text)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    if text.startswith("#Requires"):
        return text
    # Sometimes models wrap in a single ``` block without language tag
    fence2 = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if fence2:
        inner = fence2.group(1).strip()
        if inner.startswith("#Requires") or "AutoHotkey" in inner[:200]:
            return inner
    return text


def validate_generated_ahk(code: str) -> tuple[bool, str]:
    if len(code) < 40:
        return False, "Generated output too short"
    if "#Requires AutoHotkey v2" not in code:
        return False, "Missing #Requires AutoHotkey v2.0"
    if "; @description:" not in code and "; @description :" not in code:
        # allow slight spacing variants
        if not re.search(r";\s*@description\s*:", code):
            return False, "Missing metadata: ; @description: …"
    return True, ""


def build_openai_chat_messages(
    messages: list[dict[str, str]],
    *,
    system: str | None = None,
) -> list[dict[str, Any]]:
    """Build OpenAI-style message list for ``/chat/completions`` (system + user/assistant turns)."""
    msgs: list[dict[str, Any]] = []
    if system and system.strip():
        msgs.append({"role": "system", "content": system.strip()})
    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "")
        if role not in ("user", "assistant", "system") or not isinstance(content, str):
            continue
        if role == "system" and msgs and msgs[0].get("role") == "system" and system:
            continue
        msgs.append({"role": role, "content": content})
    return msgs


async def complete_via_http(system: str, user: str) -> str:
    base = resolve_base()
    model = DEFAULT_MODEL
    url = f"{base}/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    key = os.getenv("AUTOHOTKEY_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
        "max_tokens": 8192,
    }

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("LLM returned no choices")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM returned empty content")
    return content


async def chat_via_http(
    messages: list[dict[str, str]],
    *,
    system: str | None = None,
    temperature: float = 0.65,
    max_tokens: int = 4096,
) -> str:
    """Multi-turn chat against localhost OpenAI-compatible ``/chat/completions`` (SPA / no MCP sampling)."""
    base = resolve_base()
    model = DEFAULT_MODEL
    url = f"{base}/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    key = os.getenv("AUTOHOTKEY_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"

    msgs = build_openai_chat_messages(messages, system=system)
    if not msgs:
        raise ValueError("No valid messages")

    payload: dict[str, Any] = {
        "model": model,
        "messages": msgs,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("LLM returned no choices")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM returned empty content")
    return content


async def chat_via_http_stream(
    messages: list[dict[str, str]],
    *,
    system: str | None = None,
    temperature: float = 0.65,
    max_tokens: int = 4096,
) -> AsyncIterator[str]:
    """Stream assistant text deltas from OpenAI-compatible ``/chat/completions`` (``stream: true``)."""
    base = resolve_base()
    model = DEFAULT_MODEL
    url = f"{base}/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    key = os.getenv("AUTOHOTKEY_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"

    msgs = build_openai_chat_messages(messages, system=system)
    if not msgs:
        raise ValueError("No valid messages")

    payload: dict[str, Any] = {
        "model": model,
        "messages": msgs,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line or line.startswith(":"):
                    continue
                if not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = obj.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                piece = delta.get("content")
                if isinstance(piece, str) and piece:
                    yield piece


def http_llm_available() -> bool:
    """True if localhost OpenAI-compatible completion can be attempted."""
    try:
        resolve_base()
    except ValueError:
        return False
    return bool(DEFAULT_MODEL.strip())
