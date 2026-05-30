param(
    [int]$FrontendPort = 5173,
    [int]$BackendPort = 8000
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $RootDir "frontend"
$LogsDir = Join-Path $RootDir "logs"
$PidFile = Join-Path $LogsDir "stack_pids.json"

New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null

function Stop-TrackedProcesses {
    if (-not (Test-Path $PidFile)) {
        return
    }
    try {
        $tracked = Get-Content $PidFile -Raw | ConvertFrom-Json
        foreach ($name in @("backend_pid", "frontend_pid")) {
            $pid = $tracked.$name
            if ($pid) {
                Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # Ignore malformed pid file.
    }
}

function Stop-Ports([int[]]$Ports) {
    foreach ($port in $Ports) {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($conn in $conns) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

function Stop-ViteProcesses {
    $nodeProcs = Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" -ErrorAction SilentlyContinue
    foreach ($proc in $nodeProcs) {
        $cmd = $proc.CommandLine
        if ($cmd -and $cmd -match "vite" -and $cmd -match [regex]::Escape($FrontendDir)) {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

function Resolve-Python {
    $venvPython = Join-Path $RootDir "venv\Scripts\python.exe"
    $bundledPython = "C:\Users\ambat\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

    function Test-Python([string]$Candidate) {
        if (-not $Candidate) { return $false }
        if ($Candidate -ne "python" -and -not (Test-Path $Candidate)) { return $false }
        try {
            & $Candidate -c "import sys" | Out-Null
            return ($LASTEXITCODE -eq 0)
        } catch {
            return $false
        }
    }

    if ($env:VIRTUAL_ENV) {
        $activePython = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Python $activePython) { return $activePython }
    }
    if (Test-Python $bundledPython) { return $bundledPython }
    if (Test-Python $venvPython) { return $venvPython }
    if (Test-Python "python") { return "python" }
    throw "No usable Python interpreter found."
}

function Wait-ForPort([int]$Port, [int]$TimeoutSec = 20) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $listen = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($listen) { return $true }
        Start-Sleep -Milliseconds 400
    }
    return $false
}

Stop-TrackedProcesses
Stop-Ports -Ports @(5173, 5174, 5175, $BackendPort)
Stop-ViteProcesses

$pythonExe = Resolve-Python
$WorkspaceDir = Split-Path -Parent $RootDir

$backendCmd = "Set-Location -LiteralPath '$WorkspaceDir'; `$Host.UI.RawUI.WindowTitle='Trading Backend'; & '$pythonExe' -m uvicorn trading_system.main:app --host 127.0.0.1 --port $BackendPort"
$frontendCmd = "Set-Location -LiteralPath '$FrontendDir'; `$Host.UI.RawUI.WindowTitle='Trading Frontend'; cmd /c npm run dev -- --host 127.0.0.1 --port $FrontendPort --strictPort"

$backendProc = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd) `
    -WorkingDirectory $WorkspaceDir `
    -PassThru

$frontendProc = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCmd) `
    -WorkingDirectory $FrontendDir `
    -PassThru

@{
    backend_pid = $backendProc.Id
    frontend_pid = $frontendProc.Id
    started_at = (Get-Date).ToString("o")
    frontend_url = "http://localhost:$FrontendPort/"
    backend_url = "http://127.0.0.1:$BackendPort/"
} | ConvertTo-Json | Set-Content -Path $PidFile -Encoding UTF8

$frontendReady = Wait-ForPort -Port $FrontendPort
$backendReady = Wait-ForPort -Port $BackendPort

if (-not $frontendReady -or -not $backendReady) {
    Write-Host "Stack start incomplete. Check the opened Trading Backend/Trading Frontend windows for errors."
    exit 1
}

Write-Host "Trading stack started successfully."
Write-Host "Frontend: http://localhost:$FrontendPort/"
Write-Host "Backend : http://127.0.0.1:$BackendPort/"
Write-Host "To stop everything: powershell -ExecutionPolicy Bypass -File .\stop_trading_stack.ps1"
