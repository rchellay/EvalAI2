# Script para iniciar el backend correctamente
Set-Location -Path "C:\Users\ramid\EvalAI\backend"
Write-Host "🚀 Iniciando backend en http://localhost:8000" -ForegroundColor Green
C:/Users/ramid/EvalAI/.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
