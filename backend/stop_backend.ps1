# Script para detener el backend
# Uso: .\stop_backend.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EVALAI - DETENER BACKEND" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Buscar procesos Python
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "🔍 Procesos Python encontrados:" -ForegroundColor Yellow
    $pythonProcesses | ForEach-Object {
        Write-Host "   PID: $($_.Id) - $($_.ProcessName)" -ForegroundColor Gray
    }
    Write-Host ""
    
    Write-Host "🛑 Deteniendo procesos..." -ForegroundColor Yellow
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    Write-Host "✅ Procesos detenidos" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No hay procesos Python corriendo" -ForegroundColor Gray
}

# Verificar puerto 8000
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Puerto 8000 todavía en uso" -ForegroundColor Yellow
    Write-Host "   Esperando a que se libere..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
} else {
    Write-Host "✅ Puerto 8000 liberado" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Backend detenido correctamente" -ForegroundColor Green
