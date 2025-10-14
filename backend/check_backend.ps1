# Script para verificar el estado del backend
# Uso: .\check_backend.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EVALAI - ESTADO DEL BACKEND" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar procesos Python
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "✅ Procesos Python activos:" -ForegroundColor Green
    $pythonProcesses | ForEach-Object {
        Write-Host "   PID: $($_.Id) - CPU: $([math]::Round($_.CPU, 2))s - Memoria: $([math]::Round($_.WorkingSet64 / 1MB, 2))MB" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ No hay procesos Python corriendo" -ForegroundColor Red
}

Write-Host ""

# Verificar puerto 8000
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $listening = $port8000 | Where-Object { $_.State -eq 'Listen' }
    if ($listening) {
        Write-Host "✅ Puerto 8000: ESCUCHANDO" -ForegroundColor Green
        Write-Host "   Estado: $($listening.State)" -ForegroundColor Gray
        Write-Host "   Proceso ID: $($listening.OwningProcess)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Puerto 8000: EN USO (pero no escuchando)" -ForegroundColor Yellow
        $port8000 | ForEach-Object {
            Write-Host "   Estado: $($_.State) - PID: $($_.OwningProcess)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "❌ Puerto 8000: NO ESTÁ EN USO" -ForegroundColor Red
}

Write-Host ""

# Intentar conexión al backend
try {
    Write-Host "🔌 Probando conexión a http://localhost:8000..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Backend respondiendo correctamente (HTTP $($response.StatusCode))" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URLs disponibles:" -ForegroundColor Cyan
    Write-Host "   Documentación: http://localhost:8000/docs" -ForegroundColor Gray
    Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor Gray
    Write-Host "   API Base: http://localhost:8000/api" -ForegroundColor Gray
} catch {
    Write-Host "❌ Backend NO responde" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Verificar archivo de logs
$logFile = Join-Path $PSScriptRoot "backend.log"
if (Test-Path $logFile) {
    $logSize = (Get-Item $logFile).Length / 1KB
    Write-Host "📋 Log disponible: backend.log ($([math]::Round($logSize, 2)) KB)" -ForegroundColor Cyan
    Write-Host "   Ver últimas líneas: Get-Content backend.log -Tail 20" -ForegroundColor Gray
} else {
    Write-Host "ℹ️  No hay archivo de log" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
