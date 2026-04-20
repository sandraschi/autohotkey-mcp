Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Fleet-standard web_sota launcher: backend (10746) + SPA frontend (10747).
# Retractable sidebar, multiple pages (Overview, Help, Scriptlets, Status).
$BackendPort = 10746
$FrontendPort = 10747
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$WebSota = $PSScriptRoot

# 1. Kill squatters on backend and frontend ports
npx --yes kill-port $BackendPort $FrontendPort 2>$null

# 2. Start backend from repo root
Set-Location $ProjectRoot
$backendCmd = "Set-Location '$ProjectRoot'; uv run autohotkey-mcp"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 3. Wait for backend to listen
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    $conn = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue
    if ($conn) { break }
    Start-Sleep -Seconds 2
    $waited += 2
}

# 4. Start frontend (Vite) from web_sota
Set-Location $WebSota
if (-not (Test-Path "node_modules")) {
    npm install
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$WebSota'; npm run dev" -WindowStyle Normal

# 5. Brief wait for Vite to bind
Start-Sleep -Seconds 4

# 6. Open SPA in browser (frontend port)
Start-Process "http://127.0.0.1:${FrontendPort}/"

