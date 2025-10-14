# Script para ejecutar backend como servicio en background
# Uso: .\start_backend_service.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EVALAI - BACKEND SERVICE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$BACKEND_DIR = $PSScriptRoot
$VENV_PYTHON = Join-Path $BACKEND_DIR "..\\.venv\Scripts\python.exe"
$LOG_FILE = Join-Path $BACKEND_DIR "backend.log"

# Verificar entorno virtual
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "❌ ERROR: No se encuentra el entorno virtual" -ForegroundColor Red
    exit 1
}

# Matar procesos anteriores
Write-Host "🔄 Deteniendo procesos Python anteriores..." -ForegroundColor Yellow
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Limpiar el puerto
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Liberando puerto 8000..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

# Cambiar al directorio del backend
Set-Location $BACKEND_DIR

# Crear archivo de log si no existe
if (-not (Test-Path $LOG_FILE)) {
    New-Item -Path $LOG_FILE -ItemType File -Force | Out-Null
}

Write-Host "✅ Iniciando backend en background..." -ForegroundColor Green
Write-Host "   Puerto: 8000" -ForegroundColor Gray
Write-Host "   Log: backend.log" -ForegroundColor Gray
Write-Host ""

# Iniciar proceso en background (sin ventana)
$processArgs = @{
    FilePath = $VENV_PYTHON
    ArgumentList = @("-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000")
    WorkingDirectory = $BACKEND_DIR
    RedirectStandardOutput = $LOG_FILE
    RedirectStandardError = $LOG_FILE
    NoNewWindow = $true
    PassThru = $true
}

$process = Start-Process @processArgs

# Esperar un momento para verificar que inició
Start-Sleep -Seconds 3

# Verificar que el proceso sigue corriendo
if ($process.HasExited) {
    Write-Host "❌ ERROR: El backend se cerró inmediatamente" -ForegroundColor Red
    Write-Host "   Revisa el archivo backend.log para más detalles" -ForegroundColor Yellow
    exit 1
}

# Verificar que el puerto está escuchando
$listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $listening) {
    Write-Host "⚠️  ADVERTENCIA: Puerto 8000 no está escuchando aún" -ForegroundColor Yellow
    Write-Host "   Esperando 5 segundos más..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    $listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if (-not $listening) {
        Write-Host "❌ ERROR: Backend no está escuchando en puerto 8000" -ForegroundColor Red
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

Write-Host "✅ Backend corriendo correctamente!" -ForegroundColor Green
Write-Host "   PID: $($process.Id)" -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver logs: Get-Content backend.log -Tail 20 -Wait" -ForegroundColor Gray
Write-Host "   Detener: Stop-Process -Id $($process.Id)" -ForegroundColor Gray
Write-Host "   Estado: Get-Process -Id $($process.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Accede a: http://localhost:8000/docs" -ForegroundColor Cyan
