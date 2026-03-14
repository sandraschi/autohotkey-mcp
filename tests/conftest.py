"""Pytest fixtures for autohotkey-mcp."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from autohotkey_mcp.server import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client (no live server)."""
    return TestClient(app)
