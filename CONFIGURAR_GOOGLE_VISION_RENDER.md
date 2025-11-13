# 🔧 Configurar Google Cloud Vision en Render

## 📋 Problema
```
Error configurando Google Cloud Vision: Your default credentials were not found.
```

El OCR devuelve **503 Service Unavailable** porque las credenciales de Google Cloud no están configuradas en el servidor de producción.

---

## ✅ Solución en 5 Pasos

### 1️⃣ Obtener Credenciales de Google Cloud


5️⃣ Actualizar settings.py para Decodificar Base64

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
    
    credentials_base64 = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_BASE64')
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    
        GOOGLE_CLOUD_CREDENTIALS_PATH = f.name
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
else:
    GOOGLE_CLOUD_CREDENTIALS_PATH = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_PATH')
```


## 🧪 Verificación

### Verificar en Local (Opcional)
```powershell
# Windows PowerShell
python manage.py runserver
```

1. Después de agregar la variable, Render hará **deploy automático**
   Cliente Google Cloud Vision configurado correctamente
4. Prueba el endpoint:
   ```bash
   curl -X POST https://evalai2.onrender.com/api/ocr/procesar/ \
     -H "Authorization: Bearer YOUR_TOKEN" \

## 📊 Costos de Google Cloud Vision

### Precios (2024)
- **Primeros 1,000 análisis/mes**: **GRATIS** ✅
- **Siguientes análisis**: $1.50 por 1,000 imágenes
- **Para escuela típica**: ~$0-5/mes (muy bajo)

### Monitoreo de Uso
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. **Billing** → **Reports**

---

- ✅ Regenera la clave si es necesario
### Error: "API not enabled"
- ✅ Ve a **APIs & Services** → **Library**
- ✅ Busca **Cloud Vision API** y haz clic en **Enable**


### En Render: "Credentials not found"


## 🔐 Seguridad

### ✅ Buenas Prácticas
- ✅ **NO subas** el archivo JSON a Git
- ✅ Agrega `*.json` a `.gitignore`
- ✅ Usa variables de entorno (Base64)
- ✅ Limita roles a lo mínimo necesario (`Cloud Vision API User`)
- ✅ Rota credenciales cada 90 días

### ✅ Archivo .gitignore
# Google Cloud Credentials
*.json
!package.json
!tsconfig.json
evalai-credentials.json


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
