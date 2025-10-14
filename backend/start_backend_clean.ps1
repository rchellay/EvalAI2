# start_backend_clean.ps1
# Script para iniciar el backend sin emojis problematicos

$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  EVALAI - Iniciando Backend" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Configuracion
$VENV_PYTHON = "..\\.venv\Scripts\python.exe"
$BACKEND_DIR = $PSScriptRoot

# Verificar que existe el entorno virtual
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "[ERROR] No se encuentra el entorno virtual" -ForegroundColor Red
    Write-Host "   Ruta: $VENV_PYTHON" -ForegroundColor Red
    exit 1
}

# Matar procesos Python existentes
Write-Host "[1/3] Deteniendo procesos Python existentes..." -ForegroundColor Yellow
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Verificar que el puerto este libre
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[ADVERTENCIA] Puerto 8000 todavia en uso" -ForegroundColor Yellow
    Write-Host "   Esperando 3 segundos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

# Iniciar el backend
Write-Host "[2/3] Iniciando backend..." -ForegroundColor Yellow
Write-Host ""

Set-Location $BACKEND_DIR

# Iniciar sin --reload para evitar problemas
$process = Start-Process -FilePath $VENV_PYTHON `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" `
    -WorkingDirectory $BACKEND_DIR `
    -PassThru `
    -NoNewWindow

# Esperar a que inicie
Start-Sleep -Seconds 3

# Verificar que el proceso siga corriendo
if ($process.HasExited) {
    Write-Host "[ERROR] El backend se cerro inmediatamente" -ForegroundColor Red
    exit 1
}

# Verificar que el puerto este escuchando
$listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue

if (-not $listening) {
    Write-Host "[ADVERTENCIA] El puerto 8000 no esta escuchando aun" -ForegroundColor Yellow
    Write-Host "   Esperando 5 segundos mas..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    $listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    
    if (-not $listening) {
        Write-Host "[ERROR] El backend no esta escuchando en el puerto 8000" -ForegroundColor Red
        Stop-Process -Id $process.Id -Force
        exit 1
    }
}

Write-Host "[3/3] Backend iniciado correctamente!" -ForegroundColor Green
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Informacion del servidor:" -ForegroundColor White
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   PID: $($process.Id)" -ForegroundColor White
Write-Host "   URL: http://localhost:8000" -ForegroundColor White
Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Comandos utiles:" -ForegroundColor Yellow
Write-Host "   - Detener: Stop-Process -Id $($process.Id)" -ForegroundColor White
Write-Host "   - Estado: Get-Process -Id $($process.Id)" -ForegroundColor White
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
