# Script Simple de Inicio EvalAI
Write-Host "Iniciando EvalAI..." -ForegroundColor Green

# Iniciar Backend
Write-Host "Iniciando Backend Django..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\ramid\EvalAI\backend_django'; .\venv\Scripts\activate; python manage.py runserver 0.0.0.0:8000"

# Esperar un momento
Start-Sleep -Seconds 3

# Iniciar Frontend
Write-Host "Iniciando Frontend React..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\ramid\EvalAI\frontend'; npm run dev"

Write-Host "Sistema iniciado!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan