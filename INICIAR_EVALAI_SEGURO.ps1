# Script de Inicio EvalAI - PowerShell
# Inicia tanto el backend como el frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    INICIANDO EvalAI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend_django" -PathType Container)) {
    Write-Host "❌ Error: No se encuentra el directorio backend_django" -ForegroundColor Red
    Write-Host "   Ejecuta este script desde la raíz del proyecto EvalAI" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

if (-not (Test-Path "frontend" -PathType Container)) {
    Write-Host "❌ Error: No se encuentra el directorio frontend" -ForegroundColor Red
    Write-Host "   Ejecuta este script desde la raíz del proyecto EvalAI" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar archivo .env
if (-not (Test-Path ".env" -PathType Leaf)) {
    Write-Host "⚠️  Advertencia: No se encuentra el archivo .env" -ForegroundColor Yellow
    Write-Host "   Copia .env.example a .env y configura tus claves API" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "[1/2] Iniciando Backend Django..." -ForegroundColor Yellow
Set-Location "backend_django"

# Verificar entorno virtual
if (-not (Test-Path "venv" -PathType Container)) {
    Write-Host "❌ Error: No se encuentra el entorno virtual" -ForegroundColor Red
    Write-Host "   Ejecuta: python -m venv venv" -ForegroundColor Yellow
    Set-Location ".."
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"

# Verificar Django
try {
    python -c "import django; print('Django version:', django.get_version())" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Django no está instalado" -ForegroundColor Red
        Write-Host "   Ejecuta: pip install -r requirements.txt" -ForegroundColor Yellow
        Set-Location ".."
        Read-Host "Presiona Enter para salir"
        exit 1
    }
} catch {
    Write-Host "❌ Error: Django no está instalado" -ForegroundColor Red
    Write-Host "   Ejecuta: pip install -r requirements.txt" -ForegroundColor Yellow
    Set-Location ".."
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Django encontrado" -ForegroundColor Green

# Iniciar servidor Django en background
Write-Host "Iniciando servidor Django en puerto 8000..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; venv\Scripts\Activate.ps1; python manage.py runserver 0.0.0.0:8000"

Set-Location ".."

Write-Host "[2/2] Iniciando Frontend React..." -ForegroundColor Yellow
Set-Location "frontend"

# Verificar Node.js
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Node.js no está instalado" -ForegroundColor Red
        Set-Location ".."
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Node.js no está instalado" -ForegroundColor Red
    Set-Location ".."
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar node_modules
if (-not (Test-Path "node_modules" -PathType Container)) {
    Write-Host "⚠️  Instalando dependencias de Node.js..." -ForegroundColor Yellow
    npm install
}

# Iniciar servidor React en background
Write-Host "Iniciando servidor React en puerto 5173..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

Set-Location ".."

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    EvalAI INICIADO CORRECTAMENTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Acceso al sistema:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Admin:    http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Notas:" -ForegroundColor White
Write-Host "   - Los servidores se ejecutan en ventanas separadas" -ForegroundColor Gray
Write-Host "   - Para detener: Cierra las ventanas de PowerShell" -ForegroundColor Gray
Write-Host "   - Para reiniciar: Ejecuta este script nuevamente" -ForegroundColor Gray
Write-Host ""

Read-Host "Presiona Enter para continuar"
