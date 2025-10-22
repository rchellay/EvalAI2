# Script de PowerShell para hacer commit y push
Write-Host "Agregando cambios..."
git add .

Write-Host "Haciendo commit..."
git commit -m "Fix all remaining deployment issues - Create robust fix_database_complete.py script - Update render.yaml - Fix all remaining field references in diagnostics"

Write-Host "Haciendo push..."
git push

Write-Host "Completado!"
