# Script simple para iniciar EvalAI
# Ejecutar desde el directorio raíz del proyecto

Write-Host "Iniciando EvalAI..." -ForegroundColor Green

# Detener procesos existentes
Write-Host "Deteniendo procesos existentes..." -ForegroundColor Yellow
taskkill /f /im python.exe 2>$null
taskkill /f /im node.exe 2>$null

# Iniciar backend
Write-Host "Iniciando backend Django..." -ForegroundColor Cyan
Start-Process -FilePath ".\backend_django\venv\Scripts\python.exe" -ArgumentList "manage.py", "runserver", "8000" -WorkingDirectory ".\backend_django" -WindowStyle Normal

# Esperar un momento
Start-Sleep -Seconds 3

# Iniciar frontend
Write-Host "Iniciando frontend Vite..." -ForegroundColor Cyan
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory ".\frontend" -WindowStyle Normal

Write-Host "Servidores iniciados!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
