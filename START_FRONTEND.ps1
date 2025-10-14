# Script permanente para frontend
# Mantiene el proceso corriendo
Set-Location C:\Users\ramid\EvalAI\frontend
Write-Host "Iniciando Vite en puerto 5173..." -ForegroundColor Green
npm run dev
# Mantener ventana abierta si hay error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al iniciar Vite. Presiona Enter para cerrar..." -ForegroundColor Red
    Read-Host
}
