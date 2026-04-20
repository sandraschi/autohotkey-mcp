set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# AutoHotkey MCP – just recipes
# Usage: just <recipe>   or   just --list

default:
    just --list

stats:
    uv run python tools/repo_stats.py

# Run backend only (port 10746)
run server:
    uv run autohotkey-mcp

# Lint and format Python
lint check:
    uv run ruff check .
    uv run ruff format --check .

format fmt:
    uv run ruff check .
    uv run ruff format .

# Run tests (use PYTHONPATH=src if venv sync fails)
test:
    uv sync --extra dev
    uv run pytest tests -v

# Sync deps (backend)
install:
    uv sync

# Install frontend deps
install-web:
    cd web_sota
    npm install

# Launch full webapp (backend + frontend, opens browser)
# Prefer: .\web_sota\start.ps1
web start:
    .\web_sota\start.ps1

# Clean build artifacts and caches (also clears .ruff_cache; avoids uv when Scripts\*.exe is locked)
clean:
    powershell -NoProfile -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, .ruff_cache, .pytest_cache, web_sota/node_modules, web_sota/dist; Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Write-Host 'Cleaned.'"

# Backend health check (requires server running)
health:
    curl -s http://127.0.0.1:10746/health
