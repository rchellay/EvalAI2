# Script para detener EvalAI
# Ejecutar como: powershell -ExecutionPolicy Bypass -File .\DETENER_EVALAI.ps1

Write-Host "🛑 Deteniendo EvalAI..." -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow

# Detener procesos Python (Django)
Write-Host "🔧 Deteniendo Backend Django..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Detener procesos Node (Vite/React)
Write-Host "⚛️  Deteniendo Frontend React..." -ForegroundColor Cyan
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Esperar un momento para que los procesos terminen
Start-Sleep -Seconds 2

Write-Host "✅ EvalAI detenido correctamente" -ForegroundColor Green
Write-Host "💡 Para iniciarlo de nuevo, ejecuta: INICIAR_EVALAI.ps1" -ForegroundColor Cyan
