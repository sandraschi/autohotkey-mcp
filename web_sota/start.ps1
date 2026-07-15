Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Fleet-standard web_sota launcher: backend (10746) + SPA frontend (10747).
$BackendPort = 10746
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

$FrontendPort = 10747
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$WebSota = $PSScriptRoot
$ApiHealth = "http://127.0.0.1:$BackendPort/health"

function Test-AhkBackendHealthy {
    try {
        $r = Invoke-WebRequest -Uri $ApiHealth -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        return ($r.StatusCode -eq 200)
    } catch {
        return $false
    }
}

$startBackend = -not (Test-AhkBackendHealthy)
$startFrontend = $true

if (-not $startBackend) {
    Write-Host "Backend already healthy at $ApiHealth — reusing." -ForegroundColor Green
}

$frontendListening = @(Get-NetTCPConnection -LocalPort $FrontendPort -State Listen -ErrorAction SilentlyContinue)
if ($frontendListening.Count -gt 0) {
    Write-Host "Frontend already listening on :$FrontendPort — reusing." -ForegroundColor Green
    $startFrontend = $false
}

if ($startBackend -or $startFrontend) {
    npx --yes kill-port $BackendPort $FrontendPort 2>$null
}

if ($startBackend) {
    Set-Location $ProjectRoot
    $backendCmd = "Set-Location '$ProjectRoot'; uv run python -m autohotkey_mcp.server --serve"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle $WindowStyle

    $maxWait = 30
    $waited = 0
    $ok = $false
    while ($waited -lt $maxWait) {
        if (Test-AhkBackendHealthy) { $ok = $true; break }
        Start-Sleep -Seconds 2
        $waited += 2
    }
    if (-not $ok) {
        Write-Host "ERROR: Backend did not become healthy on :$BackendPort within ${maxWait}s." -ForegroundColor Red
        exit 1
    }
}

if ($startFrontend) {
    Set-Location $WebSota
    if (-not (Test-Path "node_modules")) {
        npm install
    }
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$WebSota'; npm run dev" -WindowStyle $WindowStyle
    Start-Sleep -Seconds 4
}

Start-Process "http://127.0.0.1:${FrontendPort}/"
