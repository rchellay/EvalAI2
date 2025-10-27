# Reparación completa del backend Django - EvalAI
Write-Host "Starting full repair of the Django backend..." -ForegroundColor Cyan

# Ir a la carpeta correcta
Set-Location "C:\Users\ramid\EvalAI\backend_django"

# 1️⃣ Detener servidor si está activo
Write-Host "Stopping previous Django servers..."
Get-Process | Where-Object { $_.ProcessName -like "python*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 2️⃣ Eliminar migraciones antiguas
Write-Host "Deleting old migrations..."
Get-ChildItem -Path "core\migrations" -Include *.py,*.pyc -Exclude "__init__.py" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue

# 3️⃣ Borrar base de datos (solo si es SQLite)
if (Test-Path "db.sqlite3") {
    Write-Host "Deleting SQLite database..."
    Remove-Item "db.sqlite3" -Force
}

# 4️⃣ Regenerar migraciones
Write-Host "Generating new migrations..."
python manage.py makemigrations core

# 5️⃣ Aplicar migraciones
Write-Host "Applying migrations..."
python manage.py migrate

# 6️⃣ Crear superusuario automático (por si no existe)
Write-Host "Creating automatic superuser (admin/admin123)..."
$env:DJANGO_SUPERUSER_USERNAME="admin"
$env:DJANGO_SUPERUSER_EMAIL="admin@example.com"
$env:DJANGO_SUPERUSER_PASSWORD="admin123"
python manage.py createsuperuser --noinput 2>$null

# 7️⃣ Cargar datos iniciales si existen
if (Test-Path "core\fixtures") {
    Write-Host "Loading initial data..."
    python manage.py loaddata core\fixtures\*.json
}

# 8️⃣ Lanzar servidor local
Write-Host "Starting Django server at http://127.0.0.1:8000 ..." -ForegroundColor Green
python manage.py runserver