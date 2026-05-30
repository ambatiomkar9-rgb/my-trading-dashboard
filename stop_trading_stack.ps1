$ErrorActionPreference = "SilentlyContinue"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogsDir = Join-Path $RootDir "logs"
$PidFile = Join-Path $LogsDir "stack_pids.json"

function Stop-Ports([int[]]$Ports) {
    foreach ($port in $Ports) {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($conn in $conns) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

if (Test-Path $PidFile) {
    try {
        $tracked = Get-Content $PidFile -Raw | ConvertFrom-Json
        foreach ($name in @("backend_pid", "frontend_pid")) {
            $pid = $tracked.$name
            if ($pid) {
                Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
            }
        }
    } catch { }
}

Stop-Ports @(5173, 5174, 5175, 8000)
Write-Host "Trading stack stopped."
