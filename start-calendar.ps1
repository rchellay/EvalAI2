# Start backend and frontend for calendar testing
$ErrorActionPreference = 'Stop'

$venvPython = 'C:/Users/ramid/EvalAI/.venv/Scripts/python.exe'

Write-Host "Starting Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location C:\Users\ramid\EvalAI\backend; $venvPython -m uvicorn app.main:app --reload"

Start-Sleep -Seconds 3

Write-Host "Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location C:\Users\ramid\EvalAI\frontend; npm run dev"

Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000 (or auto-assigned port)" -ForegroundColor Yellow
