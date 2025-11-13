# 🔧 Configurar Google Cloud Vision en Render

## 📋 Problema
```
Error configurando Google Cloud Vision: Your default credentials were not found.
```

El OCR devuelve **503 Service Unavailable** porque las credenciales de Google Cloud no están configuradas en el servidor de producción.

---

## ✅ Solución en 5 Pasos

### 1️⃣ Obtener Credenciales de Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Selecciona el proyecto **evalai-education** (o crea uno nuevo)
3. Ve a **APIs & Services** → **Credentials**
4. Clic en **Create Credentials** → **Service Account**
5. Completa el formulario:
   - **Nombre**: `evalai-ocr-service`
   - **Rol**: `Cloud Vision API User`
6. Clic en **Done**
7. Encuentra la cuenta creada y clic en **Keys** → **Add Key** → **JSON**
8. Descarga el archivo JSON (ejemplo: `evalai-credentials.json`)

### 2️⃣ Habilitar Cloud Vision API

1. En Google Cloud Console, ve a **APIs & Services** → **Library**
2. Busca **Cloud Vision API**
3. Clic en **Enable**

### 3️⃣ Convertir JSON a Base64

**En PowerShell** (Windows):
```powershell
$bytes = [System.IO.File]::ReadAllBytes("C:\path\to\evalai-credentials.json")
$base64 = [System.Convert]::ToBase64String($bytes)
$base64 | Set-Clipboard
Write-Host "Base64 copiado al portapapeles!"
```

**En Terminal** (Mac/Linux):
```bash
base64 -i evalai-credentials.json | pbcopy
echo "Base64 copiado al portapapeles!"
```

### 4️⃣ Configurar Variable de Entorno en Render

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Selecciona tu servicio **evalai2**
3. Ve a **Environment** → **Add Environment Variable**
4. Agrega:
   ```
   Key: GOOGLE_CLOUD_CREDENTIALS_BASE64
   Value: [pega el Base64 del paso 3]
   ```
5. Clic en **Save Changes**

### 5️⃣ Actualizar settings.py para Decodificar Base64

El archivo `backend_django/config/settings.py` ya está configurado para decodificar automáticamente:

```python
# Google Cloud Vision (OCR)
GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', 'evalai-education')

# Decodificar credenciales Base64 en Render
if os.environ.get('GOOGLE_CLOUD_CREDENTIALS_BASE64'):
    import base64
    import json
    import tempfile
    
    credentials_base64 = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_BASE64')
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(credentials_json)
        GOOGLE_CLOUD_CREDENTIALS_PATH = f.name
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
else:
    GOOGLE_CLOUD_CREDENTIALS_PATH = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_PATH')
```

---

## 🧪 Verificación

### Verificar en Local (Opcional)

Si quieres probar en local:

```powershell
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\evalai-credentials.json"
cd backend_django
python manage.py runserver
```

### Verificar en Render

1. Después de agregar la variable, Render hará **deploy automático**
2. Espera 2-3 minutos
3. Verifica en los logs:
   ```
   Cliente Google Cloud Vision configurado correctamente
   ```
4. Prueba el endpoint:
   ```bash
   curl -X POST https://evalai2.onrender.com/api/ocr/procesar/ \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "image=@test.jpg" \
     -F "idioma=es"
   ```

---

## 📊 Costos de Google Cloud Vision

### Precios (2024)
- **Primeros 1,000 análisis/mes**: **GRATIS** ✅
- **Siguientes análisis**: $1.50 por 1,000 imágenes
- **Para escuela típica**: ~$0-5/mes (muy bajo)

### Monitoreo de Uso
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. **Billing** → **Reports**
3. Filtra por **Cloud Vision API**

---

## ⚠️ Troubleshooting

### Error: "Invalid credentials"
- ✅ Verifica que el archivo JSON sea válido
- ✅ Asegúrate de que el Base64 esté completo (sin saltos de línea)
- ✅ Regenera la clave si es necesario

### Error: "API not enabled"
- ✅ Ve a **APIs & Services** → **Library**
- ✅ Busca **Cloud Vision API** y haz clic en **Enable**

### Error: "Quota exceeded"
- ✅ Verifica uso en **Billing** → **Reports**
- ✅ Si necesitas más, aumenta la cuota en **IAM & Admin** → **Quotas**

### En Render: "Credentials not found"
- ✅ Verifica que `GOOGLE_CLOUD_CREDENTIALS_BASE64` esté en Environment
- ✅ Verifica que no haya espacios extra en el valor
- ✅ Haz redeploy manual: **Manual Deploy** → **Deploy latest commit**

---

## 🔐 Seguridad

### ✅ Buenas Prácticas
- ✅ **NO subas** el archivo JSON a Git
- ✅ Agrega `*.json` a `.gitignore`
- ✅ Usa variables de entorno (Base64)
- ✅ Limita roles a lo mínimo necesario (`Cloud Vision API User`)
- ✅ Rota credenciales cada 90 días

### ✅ Archivo .gitignore
```gitignore
# Google Cloud Credentials
*.json
!package.json
!tsconfig.json
evalai-credentials.json
google-credentials*.json
```

---

## 📚 Recursos

- [Google Cloud Vision Docs](https://cloud.google.com/vision/docs)
- [Quickstart Guide](https://cloud.google.com/vision/docs/setup)
- [Authentication Guide](https://cloud.google.com/docs/authentication/getting-started)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)

---

## 🎯 Estado Actual

### Local (Desarrollo)
- ❌ OCR deshabilitado (sin credenciales)
- ✅ Backend funciona sin OCR
- ✅ Frontend muestra mensaje de error claro

### Render (Producción)
- ⏳ Pendiente configurar `GOOGLE_CLOUD_CREDENTIALS_BASE64`
- ⏳ Después de configurar: OCR funcionará automáticamente
- ✅ Sistema degradado: funciona sin OCR

---

## 🚀 Después de Configurar

Una vez configurado, los usuarios podrán:

1. **Subir imágenes** de escritura manuscrita
2. **Extraer texto** automáticamente con OCR
3. **Corregir texto** con LanguageTool integrado
4. **Guardar como evidencia** vinculada al alumno
5. **Exportar** correcciones en PDF/Excel

---

## 💡 Alternativa: OCR Deshabilitado

Si decides **NO configurar** Google Cloud Vision (por costos o preferencia):

- ✅ El sistema funciona perfectamente **sin OCR**
- ✅ Los usuarios ven mensaje claro: "OCR no disponible"
- ✅ Pueden usar **corrección de texto** sin OCR
- ✅ Todas las demás funcionalidades operativas

---

**Creado**: 13 de noviembre de 2025  
**Última actualización**: 13 de noviembre de 2025  
**Autor**: GitHub Copilot Assistant
