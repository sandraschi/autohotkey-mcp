"""HTTP route tests for autohotkey-mcp server."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["service"] == "autohotkey-mcp"
    assert "port" in data


def test_root(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "autohotkey-mcp"
    assert data["help"] == "/help"
    assert "api" in data


def test_mini_help(client: TestClient) -> None:
    r = client.get("/help")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    html = r.text
    assert "AutoHotkey MCP" in html
    assert "quick" in html or "Quick" in html
    assert "10747" in html


def test_api_help_all(client: TestClient) -> None:
    r = client.get("/api/help")
    assert r.status_code == 200
    data = r.json()
    assert "levels" in data
    levels = data["levels"]
    assert "quick" in levels
    assert "mcp_server" in levels
    assert isinstance(levels["quick"], str)


def test_api_help_level(client: TestClient) -> None:
    r = client.get("/api/help?level=quick")
    assert r.status_code == 200
    data = r.json()
    assert data["level"] == "quick"
    assert "content" in data
    assert "AutoHotkey" in data["content"] or "scriptlets" in data["content"]


def test_api_help_unknown_level(client: TestClient) -> None:
    r = client.get("/api/help?level=nosuch")
    assert r.status_code == 200
    data = r.json()
    assert "content" in data
    assert "Unknown" in data["content"] or "nosuch" in data["content"]


def test_status_ok_without_bridge(client: TestClient) -> None:
    """Status returns ok even when list_scriptlets fails (no bridge)."""
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["service"] == "autohotkey-mcp"


def test_api_scriptlets_returns_list(client: TestClient) -> None:
    """Without bridge, api_scriptlets may 500 or return empty list depending on mcp.call_tool."""
    r = client.get("/api/scriptlets")
    # Either success with scriptlets key or 500
    if r.status_code == 200:
        data = r.json()
        assert "scriptlets" in data
        assert isinstance(data["scriptlets"], list)
    else:
        assert r.status_code == 500
        data = r.json()
        assert "scriptlets" in data
        assert data["scriptlets"] == []


@patch("autohotkey_mcp.server.mcp")
def test_api_scriptlets_mocked(mock_mcp: object, client: TestClient) -> None:
    """Api scriptlets returns structured_content when call_tool returns it."""
    mock_result = type("R", (), {"structured_content": {"scriptlets": [{"id": "x", "name": "Test"}]}})()
    mock_mcp.call_tool = AsyncMock(return_value=mock_result)
    r = client.get("/api/scriptlets")
    assert r.status_code == 200
    data = r.json()
    assert data["scriptlets"] == [{"id": "x", "name": "Test"}]


def test_post_tool_missing_name(client: TestClient) -> None:
    r = client.post("/tool", json={})
    assert r.status_code == 400
    data = r.json()
    assert data.get("success") is False
    assert "error" in data or "name" in data.get("error", "").lower()


@patch("autohotkey_mcp.server.mcp")
def test_post_tool_ahk_help(mock_mcp: object, client: TestClient) -> None:
    """POST /tool with ahk_help returns content."""
    mock_mcp.call_tool = AsyncMock(
        return_value=type("R", (), {"content": [type("C", (), {"text": '{"level":"quick","content":"Hi"}'})()]})()
    )
    r = client.post("/tool", json={"name": "ahk_help", "arguments": {"level": "quick"}})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert "result" in data


@patch("autohotkey_mcp.server.mcp")
def test_post_tool_show_help(mock_mcp: object, client: TestClient) -> None:
    """POST /tool show_help returns mini_help_url and full_webapp_url."""
    mock_mcp.call_tool = AsyncMock(
        return_value=type(
            "R",
            (),
            {
                "structured_content": {
                    "mini_help_url": "http://127.0.0.1:10746/help",
                    "full_webapp_url": "http://127.0.0.1:10747/",
                    "message": "Open in browser",
                }
            },
        )()
    )
    r = client.post("/tool", json={"name": "show_help", "arguments": {}})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    result = data.get("result", {})
    assert result.get("mini_help_url", "").endswith("/help")
    assert "10747" in result.get("full_webapp_url", "")
    assert "message" in result
