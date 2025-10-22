# Script de PowerShell para hacer commit y push
Write-Host "Agregando cambios..."
git add .

Write-Host "Haciendo commit..."
git commit -m "Fix Django Admin delete operations errors - Add custom delete methods to all admin classes - Add proper error handling - Add user-friendly error messages"

Write-Host "Haciendo push..."
git push

Write-Host "Completado!"
