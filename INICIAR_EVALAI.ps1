# Script para iniciar EvalAI automáticamente
# Ejecutar como: powershell -ExecutionPolicy Bypass -File .\INICIAR_EVALAI.ps1

Write-Host "Iniciando EvalAI - Sistema de Evaluacion Educativa" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Yellow

# Función para verificar si un puerto está abierto
function Test-Port {
    param($hostname, $port)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.Connect($hostname, $port)
        $client.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Detener procesos existentes
Write-Host "Deteniendo procesos existentes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Verificar que los directorios existen
if (-not (Test-Path "backend_django")) {
    Write-Host "Error: Directorio backend_django no encontrado" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "Error: Directorio frontend no encontrado" -ForegroundColor Red
    exit 1
}

# Iniciar Backend Django
Write-Host "Iniciando Backend Django..." -ForegroundColor Cyan
Set-Location "backend_django"

# Verificar que el entorno virtual existe
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Error: Entorno virtual no encontrado en backend_django\venv\" -ForegroundColor Red
    Write-Host "Ejecuta: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activar entorno virtual y ejecutar migraciones
Write-Host "Activando entorno virtual..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

Write-Host "Aplicando migraciones..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" manage.py migrate

# Iniciar servidor Django en segundo plano
Write-Host "Iniciando servidor Django..." -ForegroundColor Cyan
Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "manage.py", "runserver", "0.0.0.0:8000" -NoNewWindow

# Esperar a que el backend esté listo
Write-Host "Esperando que el backend este listo..." -ForegroundColor Yellow
$attempts = 0
while (-not (Test-Port "localhost" 8000) -and $attempts -lt 30) {
    Start-Sleep -Seconds 1
    $attempts++
    Write-Host "Intento $attempts/30..." -ForegroundColor Gray
}

if (Test-Port "localhost" 8000) {
    Write-Host "Backend listo en http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "Error: Backend no pudo iniciarse" -ForegroundColor Red
    exit 1
}

# Volver al directorio raíz e iniciar Frontend
Set-Location ".."
Write-Host "Iniciando Frontend React..." -ForegroundColor Cyan
Set-Location "frontend"

# Verificar que node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Error: node_modules no encontrado" -ForegroundColor Red
    Write-Host "Ejecuta: npm install" -ForegroundColor Yellow
    exit 1
}

# Iniciar servidor Vite en segundo plano
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow

# Esperar a que el frontend esté listo
Write-Host "Esperando que el frontend este listo..." -ForegroundColor Yellow
$attempts = 0
while (-not (Test-Port "localhost" 5173) -and $attempts -lt 30) {
    Start-Sleep -Seconds 1
    $attempts++
    Write-Host "Intento $attempts/30..." -ForegroundColor Gray
}

if (Test-Port "localhost" 5173) {
    Write-Host "Frontend listo en http://localhost:5173" -ForegroundColor Green
} else {
    Write-Host "Error: Frontend no pudo iniciarse" -ForegroundColor Red
    exit 1
}

# Volver al directorio raíz
Set-Location ".."

Write-Host ""
Write-Host "EvalAI esta listo!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Admin:    http://localhost:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales admin: admin / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "Los servidores estan corriendo en segundo plano." -ForegroundColor Cyan
Write-Host "Para detenerlos, ejecuta: DETENER_EVALAI.ps1" -ForegroundColor Cyan
Write-Host ""

# Abrir el navegador automáticamente
Write-Host "Abriendo navegador..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host "Listo! Puedes usar EvalAI ahora." -ForegroundColor Green