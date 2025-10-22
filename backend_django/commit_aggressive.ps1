# Script de PowerShell para hacer commit y push
Write-Host "Agregando cambios..."
git add .

Write-Host "Haciendo commit..."
git commit -m "Fix deployment issues with aggressive database correction - Create fix_database_aggressive.py - Update render.yaml - Fix CORS configuration - Ensure database columns are created during build"

Write-Host "Haciendo push..."
git push

Write-Host "Completado!"
