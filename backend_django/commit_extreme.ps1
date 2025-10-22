# Script de PowerShell para hacer commit y push
Write-Host "Agregando cambios..."
git add .

Write-Host "Haciendo commit..."
git commit -m "Implement extreme database fix solution - Create fix_database_extreme.py - Add extreme database fix directly in settings.py - Update render.yaml - Multiple layers of database correction"

Write-Host "Haciendo push..."
git push

Write-Host "Completado!"
