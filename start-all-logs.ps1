# Start backend and frontend capturing logs to files (logs/backend.log & logs/frontend.log)
$ErrorActionPreference = 'Stop'

$logDir = Join-Path $PSScriptRoot 'logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backendLog = Join-Path $logDir "backend_$timestamp.log"
$frontendLog = Join-Path $logDir "frontend_$timestamp.log"

$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (Test-Path $venvPython) { 
    $pythonCmd = "`"$venvPython`""
    Write-Host "Using virtualenv: $venvPython" -ForegroundColor DarkCyan
} else { 
    $pythonCmd = 'python'
    Write-Host "Using system python" -ForegroundColor DarkYellow
}

$backendCmd = "Set-Location backend; & $pythonCmd -m uvicorn app.main:app --reload *>&1 | Out-File -FilePath '$backendLog' -Encoding utf8"
$frontendCmd = "Set-Location frontend; npm run dev *>&1 | Out-File -FilePath '$frontendLog' -Encoding utf8"

Write-Host "Logging backend -> $backendLog" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command",$backendCmd

Start-Sleep -Seconds 2

Write-Host "Logging frontend -> $frontendLog" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command",$frontendCmd

Write-Host "Launched with log capture. Use Get-Content -Wait logs\backend_*.log to tail." -ForegroundColor Green
