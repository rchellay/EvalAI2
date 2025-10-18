# Script de Verificación de Claves API - EvalAI
# Verifica que todas las claves API estén configuradas correctamente

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    VERIFICACIÓN DE CLAVES API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar archivo .env
if (-not (Test-Path ".env" -PathType Leaf)) {
    Write-Host "❌ Error: No se encuentra el archivo .env" -ForegroundColor Red
    Write-Host "   Copia .env.example a .env y configura tus claves API" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Comando: cp .env.example .env" -ForegroundColor Gray
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Archivo .env encontrado" -ForegroundColor Green
Write-Host ""

# Leer archivo .env
$envContent = Get-Content ".env"

# Verificar OpenRouter API Key
$openrouterKey = $envContent | Where-Object { $_ -match "^OPENROUTER_API_KEY=" }
if ($openrouterKey) {
    $key = $openrouterKey -replace "OPENROUTER_API_KEY=", ""
    if ($key -and $key -ne "tu-clave-openrouter-aqui") {
        Write-Host "✅ OpenRouter API Key: Configurada" -ForegroundColor Green
        Write-Host "   Clave: $($key.Substring(0, [Math]::Min(20, $key.Length)))..." -ForegroundColor Gray
    } else {
        Write-Host "❌ OpenRouter API Key: No configurada" -ForegroundColor Red
        Write-Host "   Configura OPENROUTER_API_KEY en .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ OpenRouter API Key: No encontrada en .env" -ForegroundColor Red
}

# Verificar Hugging Face API Key
$hfKey = $envContent | Where-Object { $_ -match "^HUGGINGFACE_API_KEY=" }
if ($hfKey) {
    $key = $hfKey -replace "HUGGINGFACE_API_KEY=", ""
    if ($key -and $key -ne "tu-clave-huggingface-aqui") {
        Write-Host "✅ Hugging Face API Key: Configurada" -ForegroundColor Green
        Write-Host "   Clave: $($key.Substring(0, [Math]::Min(20, $key.Length)))..." -ForegroundColor Gray
    } else {
        Write-Host "❌ Hugging Face API Key: No configurada" -ForegroundColor Red
        Write-Host "   Configura HUGGINGFACE_API_KEY en .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Hugging Face API Key: No encontrada en .env" -ForegroundColor Red
}

# Verificar Google Cloud API Key
$googleKey = $envContent | Where-Object { $_ -match "^GOOGLE_CLOUD_API_KEY=" }
if ($googleKey) {
    $key = $googleKey -replace "GOOGLE_CLOUD_API_KEY=", ""
    if ($key -and $key -ne "tu-clave-google-aqui") {
        Write-Host "✅ Google Cloud API Key: Configurada" -ForegroundColor Green
        Write-Host "   Clave: $($key.Substring(0, [Math]::Min(20, $key.Length)))..." -ForegroundColor Gray
    } else {
        Write-Host "❌ Google Cloud API Key: No configurada" -ForegroundColor Red
        Write-Host "   Configura GOOGLE_CLOUD_API_KEY en .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Google Cloud API Key: No encontrada en .env" -ForegroundColor Red
}

# Verificar Google Cloud Project ID
$googleProject = $envContent | Where-Object { $_ -match "^GOOGLE_CLOUD_PROJECT_ID=" }
if ($googleProject) {
    $project = $googleProject -replace "GOOGLE_CLOUD_PROJECT_ID=", ""
    if ($project -and $project -ne "tu-proyecto-id-aqui") {
        Write-Host "✅ Google Cloud Project ID: Configurado" -ForegroundColor Green
        Write-Host "   Proyecto: $project" -ForegroundColor Gray
    } else {
        Write-Host "❌ Google Cloud Project ID: No configurado" -ForegroundColor Red
        Write-Host "   Configura GOOGLE_CLOUD_PROJECT_ID en .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Google Cloud Project ID: No encontrado en .env" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    RESUMEN DE CONFIGURACIÓN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Contar claves configuradas
$totalKeys = 4
$configuredKeys = 0

if ($openrouterKey -and ($openrouterKey -replace "OPENROUTER_API_KEY=", "") -ne "tu-clave-openrouter-aqui") { $configuredKeys++ }
if ($hfKey -and ($hfKey -replace "HUGGINGFACE_API_KEY=", "") -ne "tu-clave-huggingface-aqui") { $configuredKeys++ }
if ($googleKey -and ($googleKey -replace "GOOGLE_CLOUD_API_KEY=", "") -ne "tu-clave-google-aqui") { $configuredKeys++ }
if ($googleProject -and ($googleProject -replace "GOOGLE_CLOUD_PROJECT_ID=", "") -ne "tu-proyecto-id-aqui") { $configuredKeys++ }

Write-Host "Claves configuradas: $configuredKeys/$totalKeys" -ForegroundColor $(if ($configuredKeys -eq $totalKeys) { "Green" } else { "Yellow" })

if ($configuredKeys -eq $totalKeys) {
    Write-Host ""
    Write-Host "🎉 ¡Todas las claves API están configuradas!" -ForegroundColor Green
    Write-Host "   El sistema EvalAI debería funcionar correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para iniciar el sistema:" -ForegroundColor White
    Write-Host "   .\INICIAR_EVALAI_SEGURO.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠️  Configuración incompleta" -ForegroundColor Yellow
    Write-Host "   Edita el archivo .env con tus claves reales" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Archivo .env:" -ForegroundColor White
    Write-Host "   OPENROUTER_API_KEY=tu-clave-real" -ForegroundColor Gray
    Write-Host "   HUGGINGFACE_API_KEY=tu-clave-real" -ForegroundColor Gray
    Write-Host "   GOOGLE_CLOUD_API_KEY=tu-clave-real" -ForegroundColor Gray
    Write-Host "   GOOGLE_CLOUD_PROJECT_ID=tu-proyecto-real" -ForegroundColor Gray
}

Write-Host ""
Read-Host "Presiona Enter para continuar"
