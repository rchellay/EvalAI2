# Script para iniciar el backend Django
Write-Host "🚀 Iniciando Backend Django REST Framework..." -ForegroundColor Green

# Verificar si hay un servidor corriendo
$pythonProcess = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcess) {
    Write-Host "⚠️  Hay un servidor Python corriendo. Deteniendo..." -ForegroundColor Yellow
    Stop-Process -Name python* -Force
    Start-Sleep -Seconds 2
}

# Cambiar al directorio del backend
Set-Location $PSScriptRoot

# Activar entorno virtual y ejecutar servidor
Write-Host "📦 Activando entorno virtual..." -ForegroundColor Cyan
$venvPath = "..\..\.venv\Scripts\python.exe"

Write-Host "🔧 Aplicando migraciones..." -ForegroundColor Cyan
& $venvPath manage.py migrate

Write-Host "✅ Servidor Django listo en http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API REST disponible en http://localhost:8000/api/" -ForegroundColor Green
Write-Host "👤 Admin panel en http://localhost:8000/admin/" -ForegroundColor Green
Write-Host "" 
Write-Host "🔑 Credenciales admin: admin / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Gray
Write-Host ""

# Iniciar servidor
& $venvPath manage.py runserver 0.0.0.0:8000
