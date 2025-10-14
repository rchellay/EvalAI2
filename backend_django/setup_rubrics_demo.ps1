# Script PowerShell para configurar ejemplos de rúbricas
# Ubicación: backend_django\setup_rubrics_demo.ps1

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  🎓 CONFIGURACIÓN DE DEMO - MÓDULO DE RÚBRICAS" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "❌ Error: No se encontró el entorno virtual." -ForegroundColor Red
    Write-Host "   Asegúrate de estar en el directorio backend_django" -ForegroundColor Yellow
    exit 1
}

# Paso 1: Generar rúbricas
Write-Host "📋 Paso 1/2: Generando rúbricas de ejemplo..." -ForegroundColor Green
Write-Host "   - Presentación Oral (4 criterios)" -ForegroundColor Gray
Write-Host "   - Proyecto de Investigación Científica (4 criterios)" -ForegroundColor Gray
Write-Host ""

.\venv\Scripts\python.exe generate_rubric_examples.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Error al generar rúbricas." -ForegroundColor Red
    exit 1
}

# Paso 2: Generar evaluaciones
Write-Host "`n📝 Paso 2/2: Generando evaluaciones de ejemplo..." -ForegroundColor Green
Write-Host "   - 15 evaluaciones para Presentación Oral" -ForegroundColor Gray
Write-Host "   - 12 evaluaciones para Proyecto de Investigación" -ForegroundColor Gray
Write-Host ""

.\venv\Scripts\python.exe generate_sample_evaluations.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Error al generar evaluaciones." -ForegroundColor Red
    exit 1
}

# Resumen final
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  ✨ CONFIGURACIÓN COMPLETA" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "✅ Sistema de rúbricas listo para demostración`n" -ForegroundColor Green

Write-Host "📊 Datos generados:" -ForegroundColor Yellow
Write-Host "   • 2 rúbricas activas" -ForegroundColor White
Write-Host "   • 8 criterios de evaluación" -ForegroundColor White
Write-Host "   • 32 niveles de desempeño" -ForegroundColor White
Write-Host "   • 27 evaluaciones realizadas" -ForegroundColor White
Write-Host "   • 108 puntuaciones registradas`n" -ForegroundColor White

Write-Host "🔗 URLs de acceso:" -ForegroundColor Yellow
Write-Host "   Lista:      http://localhost:5173/rubricas" -ForegroundColor Cyan
Write-Host "   Aplicar:    http://localhost:5173/rubricas/1/aplicar" -ForegroundColor Cyan
Write-Host "   Resultados: http://localhost:5173/rubricas/resultados`n" -ForegroundColor Cyan

Write-Host "🚀 Próximos pasos:" -ForegroundColor Yellow
Write-Host "   1. Inicia el backend:  python manage.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host "   2. Inicia el frontend: cd ..\frontend; npm run dev" -ForegroundColor White
Write-Host "   3. Abre: http://localhost:5173/rubricas`n" -ForegroundColor White

Write-Host "💡 Funcionalidades disponibles:" -ForegroundColor Yellow
Write-Host "   ✓ Ver lista de rúbricas" -ForegroundColor Green
Write-Host "   ✓ Crear/editar rúbricas" -ForegroundColor Green
Write-Host "   ✓ Aplicar evaluaciones interactivas" -ForegroundColor Green
Write-Host "   ✓ Ver gráficos de resultados" -ForegroundColor Green
Write-Host "   ✓ Exportar datos a CSV`n" -ForegroundColor Green

Write-Host "¡Disfruta explorando el sistema de rúbricas! 🎉`n" -ForegroundColor Magenta
