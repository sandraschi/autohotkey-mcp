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
    mock_result = type(
        "R", (), {"structured_content": {"scriptlets": [{"id": "x", "name": "Test"}]}}
    )()
    mock_mcp.call_tool = AsyncMock(return_value=mock_result)
    r = client.get("/api/scriptlets")
    assert r.status_code == 200
    data = r.json()
    assert data["scriptlets"] == [{"id": "x", "name": "Test"}]


def test_api_running(client: TestClient) -> None:
    r = client.get("/api/running")
    assert r.status_code == 200
    data = r.json()
    assert "instances" in data
    assert isinstance(data["instances"], list)
    assert "bridge_url" in data


@patch("autohotkey_mcp.server.mcp")
def test_api_stop_scriptlet(mock_mcp: object, client: TestClient) -> None:
    mock_mcp.call_tool = AsyncMock(
        return_value=type(
            "R",
            (),
            {
                "content": [
                    type(
                        "C",
                        (),
                        {"text": '{"success": true, "script_id": "foo", "source": "bridge"}'},
                    )()
                ]
            },
        )()
    )
    r = client.post("/api/stop_scriptlet", json={"script_id": "foo"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True


def test_api_personas(client: TestClient) -> None:
    r = client.get("/api/personas")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("personas"), list)
    assert len(data["personas"]) >= 1
    assert data["personas"][0].get("id")


def test_api_prompts(client: TestClient) -> None:
    r = client.get("/api/prompts")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("prompts"), list)
    assert len(data["prompts"]) >= 1
    assert isinstance(data.get("categories"), list)


def test_api_prompts_category_filter(client: TestClient) -> None:
    r = client.get("/api/prompts", params={"category": "hotkeys"})
    assert r.status_code == 200
    data = r.json()
    for p in data.get("prompts", []):
        assert str(p.get("category", "")).lower() == "hotkeys"


@patch("autohotkey_mcp.server.refine_generation_prompt", new_callable=AsyncMock)
def test_api_refine_prompt(mock_refine: AsyncMock, client: TestClient) -> None:
    mock_refine.return_value = {
        "success": True,
        "refined_prompt": "Clear prompt text.",
        "source": "http",
    }
    r = client.post("/api/refine_prompt", json={"rough": "make a thing"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert mock_refine.called


@patch("autohotkey_mcp.server.http_llm_available", return_value=True)
@patch("autohotkey_mcp.server.chat_via_http", new_callable=AsyncMock)
def test_api_chat(mock_chat: AsyncMock, _avail: bool, client: TestClient) -> None:
    mock_chat.return_value = "Use Hotkey() in v2."
    r = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "How do I bind Ctrl+Shift+X?"}]},
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert "Hotkey" in data.get("message", "")


@patch("autohotkey_mcp.server.generate_ahk_script_to_file", new_callable=AsyncMock)
def test_api_generate_scriptlet(mock_gen: AsyncMock, client: TestClient) -> None:
    mock_gen.return_value = {
        "success": True,
        "path": "C:\\tmp\\x.ahk",
        "script_id": "x",
        "generation_source": "http",
    }
    r = client.post("/api/generate_scriptlet", json={"prompt": "Show a MsgBox"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert mock_gen.called


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
        return_value=type(
            "R", (), {"content": [type("C", (), {"text": '{"level":"quick","content":"Hi"}'})()]}
        )()
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


@pytest.mark.asyncio
async def test_mcp_resource_prompt_catalog() -> None:
    from autohotkey_mcp.server import mcp

    r = await mcp.read_resource("ahk://prompts/catalog")
    assert "hk_toggle_mute" in str(r)


@pytest.mark.asyncio
async def test_mcp_resource_prompt_by_id() -> None:
    from autohotkey_mcp.server import mcp

    r = await mcp.read_resource("ahk://prompts/hk_toggle_mute")
    assert "Global mute" in str(r)


@pytest.mark.asyncio
async def test_mcp_resource_prompt_unknown() -> None:
    from autohotkey_mcp.server import mcp

    r = await mcp.read_resource("ahk://prompts/__no_such_prompt__")
    assert "unknown" in str(r).lower()


@patch("autohotkey_mcp.server.http_llm_available", return_value=True)
@patch("autohotkey_mcp.server.chat_via_http_stream")
def test_api_chat_stream_sse(mock_stream: object, _avail: bool, client: TestClient) -> None:
    async def agen():
        yield "hello"

    mock_stream.return_value = agen()
    r = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "hi"}], "stream": True},
    )
    assert r.status_code == 200
    assert "text/event-stream" in (r.headers.get("content-type") or "")
    assert "data:" in r.text
    assert "hello" in r.text
