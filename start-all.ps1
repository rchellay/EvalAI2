# PowerShell script to start backend (FastAPI) and frontend (Vite)
# Usage: Right-click -> Run with PowerShell OR: powershell -ExecutionPolicy Bypass -File .\start-all.ps1

$ErrorActionPreference = 'Stop'

# Detect local virtual environment python if exists
$venvPython = Join-Path -Path $PSScriptRoot -ChildPath '.venv/Scripts/python.exe'
if (Test-Path $venvPython) {
	Write-Host "Using virtualenv: $venvPython" -ForegroundColor DarkCyan
	$pythonCmd = $venvPython
} else {
	Write-Host "No .venv detected, falling back to system 'python'" -ForegroundColor DarkYellow
	$pythonCmd = 'python'
}

Write-Host "Starting Backend (Uvicorn) ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command","cd backend; $pythonCmd -m uvicorn app.main:app --reload" | Out-Null

Start-Sleep -Seconds 2

Write-Host "Starting Frontend (Vite) ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command","cd frontend; npm run dev" | Out-Null

Write-Host "Both processes launched in separate PowerShell windows." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000  |  Frontend: http://localhost:3000" -ForegroundColor Yellow
