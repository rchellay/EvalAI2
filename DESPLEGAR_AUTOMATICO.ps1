# Script de Despliegue Automático EvalAI
# Despliega tanto el backend (Render) como el frontend (Vercel)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    DESPLIEGUE AUTOMÁTICO EvalAI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "render.yaml" -PathType Leaf)) {
    Write-Host "❌ Error: No se encuentra render.yaml" -ForegroundColor Red
    Write-Host "   Ejecuta este script desde la raíz del proyecto EvalAI" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

if (-not (Test-Path "frontend/vercel.json" -PathType Leaf)) {
    Write-Host "❌ Error: No se encuentra frontend/vercel.json" -ForegroundColor Red
    Write-Host "   Ejecuta este script desde la raíz del proyecto EvalAI" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Archivos de configuración encontrados" -ForegroundColor Green
Write-Host ""

# Verificar Git
try {
    $gitStatus = git status --porcelain 2>$null
    if ($gitStatus) {
        Write-Host "⚠️  Hay cambios sin commitear:" -ForegroundColor Yellow
        Write-Host $gitStatus -ForegroundColor Gray
        Write-Host ""
        $commit = Read-Host "¿Quieres hacer commit de los cambios? (y/n)"
        if ($commit -eq "y" -or $commit -eq "Y") {
            git add .
            git commit -m "🚀 Deploy: Preparar para despliegue en producción"
            git push origin main
            Write-Host "✅ Cambios commiteados y subidos" -ForegroundColor Green
        }
    } else {
        Write-Host "✅ No hay cambios pendientes" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error con Git: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    INSTRUCCIONES DE DESPLIEGUE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔧 PASO 1: DESPLEGAR BACKEND EN RENDER" -ForegroundColor Yellow
Write-Host "1. Ve a https://render.com" -ForegroundColor White
Write-Host "2. Crea una cuenta o inicia sesión" -ForegroundColor White
Write-Host "3. Haz clic en 'New +' > 'Web Service'" -ForegroundColor White
Write-Host "4. Conecta tu repositorio GitHub: rchellay/EvalAI2" -ForegroundColor White
Write-Host "5. Configura el servicio:" -ForegroundColor White
Write-Host "   - Name: evalai-backend" -ForegroundColor Gray
Write-Host "   - Environment: Python 3" -ForegroundColor Gray
Write-Host "   - Build Command: pip install -r backend_django/requirements.txt" -ForegroundColor Gray
Write-Host "   - Start Command: cd backend_django && gunicorn config.wsgi:application" -ForegroundColor Gray
Write-Host "6. En Environment Variables, agrega:" -ForegroundColor White
Write-Host "   - DEBUG: False" -ForegroundColor Gray
Write-Host "   - SECRET_KEY: [generar clave segura]" -ForegroundColor Gray
Write-Host "   - ALLOWED_HOSTS: evalai-backend.onrender.com" -ForegroundColor Gray
Write-Host "   - OPENROUTER_API_KEY: tu-clave-openrouter-aqui" -ForegroundColor Gray
Write-Host "   - HUGGINGFACE_API_KEY: tu-clave-huggingface-aqui" -ForegroundColor Gray
Write-Host "   - GOOGLE_CLOUD_PROJECT_ID: tu-proyecto-google-aqui" -ForegroundColor Gray
Write-Host "   - GOOGLE_CLOUD_API_KEY: tu-clave-google-cloud-aqui" -ForegroundColor Gray
Write-Host "   - CORS_ALLOWED_ORIGINS: https://evalai-frontend.vercel.app" -ForegroundColor Gray
Write-Host "7. Haz clic en 'Create Web Service'" -ForegroundColor White
Write-Host ""

Write-Host "🎨 PASO 2: DESPLEGAR FRONTEND EN VERCEL" -ForegroundColor Yellow
Write-Host "1. Ve a https://vercel.com" -ForegroundColor White
Write-Host "2. Crea una cuenta o inicia sesión" -ForegroundColor White
Write-Host "3. Haz clic en 'New Project'" -ForegroundColor White
Write-Host "4. Importa tu repositorio GitHub: rchellay/EvalAI2" -ForegroundColor White
Write-Host "5. Configura el proyecto:" -ForegroundColor White
Write-Host "   - Framework Preset: Vite" -ForegroundColor Gray
Write-Host "   - Root Directory: frontend" -ForegroundColor Gray
Write-Host "   - Build Command: npm run build" -ForegroundColor Gray
Write-Host "   - Output Directory: dist" -ForegroundColor Gray
Write-Host "6. En Environment Variables, agrega:" -ForegroundColor White
Write-Host "   - VITE_API_URL: https://evalai-backend.onrender.com" -ForegroundColor Gray
Write-Host "7. Haz clic en 'Deploy'" -ForegroundColor White
Write-Host ""

Write-Host "📊 PASO 3: CONFIGURAR BASE DE DATOS" -ForegroundColor Yellow
Write-Host "1. En Render, ve a tu servicio backend" -ForegroundColor White
Write-Host "2. Haz clic en 'Environment'" -ForegroundColor White
Write-Host "3. Agrega una nueva variable:" -ForegroundColor White
Write-Host "   - Key: DATABASE_URL" -ForegroundColor Gray
Write-Host "   - Value: [Render generará automáticamente una PostgreSQL]" -ForegroundColor Gray
Write-Host "4. Reinicia el servicio" -ForegroundColor White
Write-Host ""

Write-Host "🔗 PASO 4: ACTUALIZAR CORS" -ForegroundColor Yellow
Write-Host "1. Una vez que tengas la URL del frontend de Vercel" -ForegroundColor White
Write-Host "2. Actualiza CORS_ALLOWED_ORIGINS en Render con la URL real" -ForegroundColor White
Write-Host "3. Reinicia el servicio backend" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "    DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs del sistema:" -ForegroundColor White
Write-Host "   Backend: https://evalai-backend.onrender.com" -ForegroundColor Cyan
Write-Host "   Frontend: https://evalai-frontend.vercel.app" -ForegroundColor Cyan
Write-Host "   Admin: https://evalai-backend.onrender.com/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Funcionalidades disponibles:" -ForegroundColor White
Write-Host "   ✅ Generación de rúbricas con IA (Qwen3)" -ForegroundColor Green
Write-Host "   ✅ Análisis de evaluaciones (DeepSeek)" -ForegroundColor Green
Write-Host "   ✅ Mejora de comentarios (GLM 4.5 Air)" -ForegroundColor Green
Write-Host "   ✅ Transcripción de audio (Whisper)" -ForegroundColor Green
Write-Host "   ✅ OCR manuscrito con corrección automática" -ForegroundColor Green
Write-Host "   ✅ Sistema de evidencias de corrección" -ForegroundColor Green
Write-Host ""

Read-Host "Presiona Enter para continuar"
