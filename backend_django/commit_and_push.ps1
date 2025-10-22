# Script de PowerShell para hacer commit y push
Write-Host "Agregando cambios..."
git add .

Write-Host "Haciendo commit..."
git commit -m "Fix remaining deployment issues - Fix OperationalError import issue - Create fix_database_columns.py script - Update render.yaml - Fix remaining field references"

Write-Host "Haciendo push..."
git push

Write-Host "Completado!"
