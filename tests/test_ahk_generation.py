"""AHK LLM extraction, validation, and generate_ahk_script_to_file (mocked)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from autohotkey_mcp.ahk_llm import extract_ahk_source, validate_generated_ahk
from autohotkey_mcp.scriptlet_generate import generate_ahk_script_to_file

_VALID = """#Requires AutoHotkey v2.0
; @description: test
; @category: ai_generated
; @version: 1.0.0
MsgBox("ok", "t")
"""


def test_extract_ahk_from_fence() -> None:
    raw = f"Here is the script:\n```ahk\n{_VALID}\n```"
    assert extract_ahk_source(raw).strip().startswith("#Requires")


def test_validate_good() -> None:
    ok, err = validate_generated_ahk(_VALID)
    assert ok and err == ""


def test_validate_bad_no_requires() -> None:
    # Must be long enough to pass the minimum-length gate so we exercise the #Requires check.
    bad = "MsgBox('x')\n" + ("; pad line\n" * 8)
    ok, err = validate_generated_ahk(bad)
    assert not ok
    assert "Requires" in err or "requires" in err.lower()


@pytest.mark.asyncio
async def test_generate_writes_valid_file(tmp_path: Path) -> None:
    with patch(
        "autohotkey_mcp.scriptlet_generate.complete_dual_path",
        new_callable=AsyncMock,
    ) as m:
        m.return_value = (_VALID, "http")
        out = await generate_ahk_script_to_file("show a message box", "gen_test", tmp_path, None)
    assert out["success"] is True
    assert out.get("generation_source") == "http"
    p = tmp_path / "gen_test.ahk"
    assert p.exists()
    assert "#Requires AutoHotkey v2" in p.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_generate_no_llm_fails_cleanly(tmp_path: Path) -> None:
    with patch(
        "autohotkey_mcp.scriptlet_generate.complete_dual_path",
        new_callable=AsyncMock,
    ) as m:
        m.return_value = (None, None)
        out = await generate_ahk_script_to_file("describe something", None, tmp_path, None)
    assert out["success"] is False
    assert "No LLM" in out.get("error", "") or "error" in out
    assert "placeholder" in out.get("hint", "").lower()
