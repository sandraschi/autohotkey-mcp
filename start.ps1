# Start AutoHotkey MCP server (fleet port 10746). Kill zombie on PORT first.
$ErrorActionPreference = "Stop"
$Port = 10746
try {
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.OwningProcess -ne 4) { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    }
} catch { }
Set-Location $PSScriptRoot
uv run autohotkey-mcp
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
