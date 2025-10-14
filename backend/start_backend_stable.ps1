# Script para mantener el backend corriendo de forma estable
# Uso: .\start_backend_stable.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EVALAI - BACKEND ESTABLE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$VENV_PATH = "..\\.venv\Scripts\python.exe"
$BACKEND_DIR = $PSScriptRoot
$MAX_RETRIES = 3
$RETRY_DELAY = 5

# Cambiar al directorio del backend
Set-Location $BACKEND_DIR

# Verificar que existe el entorno virtual
if (-not (Test-Path $VENV_PATH)) {
    Write-Host "❌ ERROR: No se encuentra el entorno virtual en $VENV_PATH" -ForegroundColor Red
    Write-Host "   Ejecuta primero: python -m venv ..\.venv" -ForegroundColor Yellow
    exit 1
}

# Verificar que el puerto 8000 esté libre
$portInUse = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Puerto 8000 ya está en uso. Deteniendo procesos..." -ForegroundColor Yellow
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "✅ Iniciando backend en puerto 8000..." -ForegroundColor Green
Write-Host "   Presiona Ctrl+C para detener" -ForegroundColor Gray
Write-Host ""

# Iniciar el backend con reintentos automáticos
$retryCount = 0
while ($true) {
    try {
        # Ejecutar uvicorn
        & $VENV_PATH -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        
        # Si llega aquí, el servidor se cerró normalmente
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ Backend cerrado correctamente" -ForegroundColor Green
            break
        } else {
            throw "Backend cerrado con código de error $exitCode"
        }
        
    } catch {
        $retryCount++
        
        if ($retryCount -ge $MAX_RETRIES) {
            Write-Host ""
            Write-Host "❌ ERROR: Backend falló $MAX_RETRIES veces. Abortando." -ForegroundColor Red
            Write-Host "   Error: $_" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "⚠️  Backend cerrado inesperadamente (intento $retryCount de $MAX_RETRIES)" -ForegroundColor Yellow
        Write-Host "   Reiniciando en $RETRY_DELAY segundos..." -ForegroundColor Yellow
        Start-Sleep -Seconds $RETRY_DELAY
    }
}
