"""Tests for help_content module."""

from __future__ import annotations

import pytest

from autohotkey_mcp import help_content


def test_get_all_levels() -> None:
    levels = help_content.get_all_levels()
    assert isinstance(levels, dict)
    assert set(levels.keys()) == {"quick", "reference", "language", "usage", "tools", "mcp_server"}
    for k, v in levels.items():
        assert isinstance(v, str)
        assert len(v) > 0


def test_get_help_default() -> None:
    text = help_content.get_help()
    assert "AutoHotkey" in text or "scriptlets" in text
    assert "quick" in text.lower() or "Quick" in text


def test_get_help_levels() -> None:
    for level in help_content.LEVELS:
        text = help_content.get_help(level=level)
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Unknown" not in text or level in text


def test_get_help_unknown_level() -> None:
    text = help_content.get_help(level="nosuch")
    assert "Unknown" in text
    assert "nosuch" in text
    assert "quick" in text or "Available" in text


def test_get_help_with_topic() -> None:
    text = help_content.get_help(level="quick", topic="bridge")
    assert "quick" in text.lower() or "Quick" in text
    assert "topic" in text.lower() or "bridge" in text
