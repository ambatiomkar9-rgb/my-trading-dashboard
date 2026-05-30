$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$proj = Resolve-Path (Join-Path $root "..")
Set-Location $proj

Write-Host "Project:" $proj

if (Test-Path ".\.env") {
  Write-Host "Loading .env ..."
  Get-Content .\.env | ForEach-Object {
    if ($_ -match "^\s*#") { return }
    if ($_ -match "^\s*$") { return }
    $kv = $_.Split("=", 2)
    if ($kv.Count -eq 2) {
      $name = $kv[0].Trim()
      $val = $kv[1].Trim()
      if ($name) {
        # PowerShell doesn't allow dynamic $env:$name assignment directly.
        # Use the Env: drive instead.
        if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Trim('"') }
        if ($val.StartsWith("'") -and $val.EndsWith("'")) { $val = $val.Trim("'") }
        Set-Item -Path ("Env:" + $name) -Value $val
      }
    }
  }
}

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
  throw "ssh not found. Install OpenSSH Client on Windows."
}

# Helper: run a command array and return @{ out=...; code=... }
function Invoke-CmdArray {
  param([string[]]$CmdArgs)
  if (-not $CmdArgs -or $CmdArgs.Count -lt 1) {
    return @{ out = "No command args provided."; code = 1 }
  }
  if ($CmdArgs.Count -eq 1) {
    $out = & $CmdArgs[0] 2>&1
    return @{ out = $out; code = $LASTEXITCODE }
  }
  $out = & $CmdArgs[0] $CmdArgs[1..($CmdArgs.Count-1)] 2>&1
  return @{ out = $out; code = $LASTEXITCODE }
}

# IMPORTANT: $Host is a built-in, read-only PowerShell variable (case-insensitive).
# Use distinct variable names.
$hermesCmd = $env:HERMES_CMD
$hermesWslDistro = $env:HERMES_WSL_DISTRO
$hermesHost = $env:HERMES_SSH_HOST
$hermesUser = $env:HERMES_SSH_USER
$hermesPort = $env:HERMES_SSH_PORT
$hermesKey  = $env:HERMES_SSH_IDENTITY_FILE

if ($hermesCmd) {
  Write-Host "Using HERMES_CMD from .env:" $hermesCmd
  $args = @()
  $args += ($hermesCmd -split ' ')
  $args += @("--version")
  Write-Host "Running:" ($args -join " ")

  $res = Invoke-CmdArray -CmdArgs $args
  if ($res.code -eq 0) {
    Write-Host $res.out
    Write-Host "OK: Hermes reachable via HERMES_CMD"
    exit 0
  }

  # If user configured "wsl hermes" but Hermes isn't on PATH, attempt safe fallbacks.
  # This prevents the common "/bin/bash: hermes: command not found" issue.
  if ($args[0] -match '^(wsl|wsl\.exe)$') {
    $fallbackHermes = "/home/ambat/.local/bin/hermes"

    $wslArgs = @("wsl")
    if ($hermesWslDistro) { $wslArgs += @("-d", $hermesWslDistro) }
    $wslArgs += @("--", $fallbackHermes, "--version")

    Write-Host "HERMES_CMD failed (exit=$($res.code)). Trying WSL fallback:" ($wslArgs -join " ")
    $res2 = Invoke-CmdArray -CmdArgs $wslArgs
    if ($res2.code -eq 0) {
      Write-Host $res2.out
      Write-Host "OK: Hermes reachable via WSL fallback ($fallbackHermes)"
      exit 0
    }

    # Last resort: run via bash -lc so login PATH is loaded (if Hermes is installed but PATH isn't).
    $bashCmd = "command -v hermes >/dev/null 2>&1 && hermes --version || $fallbackHermes --version"
    $wslArgs3 = @("wsl")
    if ($hermesWslDistro) { $wslArgs3 += @("-d", $hermesWslDistro) }
    $wslArgs3 += @("--", "bash", "-lc", $bashCmd)
    Write-Host "Trying WSL login-shell fallback:" ($wslArgs3 -join " ")
    $res3 = Invoke-CmdArray -CmdArgs $wslArgs3
    if ($res3.code -eq 0) {
      Write-Host $res3.out
      Write-Host "OK: Hermes reachable via WSL login-shell fallback"
      exit 0
    }
  }

  Write-Host $res.out
  Write-Host "Hermes failed via HERMES_CMD (exit=$($res.code))."
  Write-Host "Falling back to SSH mode (if HERMES_SSH_* is configured)..."
}

if (-not $hermesHost) { throw "HERMES_SSH_HOST is empty in .env and HERMES_CMD not set." }
if (-not $hermesUser) { throw "HERMES_SSH_USER is empty in .env" }
if (-not $hermesPort) { $hermesPort = "22" }

$dest = "$hermesUser@$hermesHost"

$args = @(
  "-T",
  "-o", "BatchMode=yes",
  "-o", "ConnectTimeout=6",
  "-o", "StrictHostKeyChecking=accept-new",
  "-p", "$hermesPort"
)
if ($hermesKey) { $args += @("-i", "$hermesKey") }
$args += @("$dest", "hermes", "--version")

Write-Host "Running:" "ssh" ($args -join " ")
$out = & ssh @args 2>&1
$code = $LASTEXITCODE
if ($code -ne 0) {
  Write-Host $out
  throw "SSH/Hermes failed (exit=$code). Fix SSH server/auth and retry."
}
Write-Host $out
Write-Host "OK: Hermes reachable over SSH"
