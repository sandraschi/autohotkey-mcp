# Tests

- **Run:** `just test` (or `uv sync --extra dev` then `uv run pytest tests -v`).
- If venv is locked (e.g. autohotkey-mcp.exe in use), run with `PYTHONPATH=src` and system pytest:
  - PowerShell: `$env:PYTHONPATH = "src"; python -m pytest tests -v`

**Layout:**
- `conftest.py` — `client` fixture (FastAPI TestClient).
- `test_server.py` — HTTP routes: `/health`, `/`, `/help`, `/api/help`, `/api/scriptlets`, `/status`, `POST /tool`. Uses mocks for `mcp.call_tool` where needed.
- `test_help_content.py` — `help_content.get_help`, `get_all_levels`, unknown level.

No live bridge or depot required for tests.
