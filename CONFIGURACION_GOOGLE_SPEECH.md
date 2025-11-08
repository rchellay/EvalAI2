# 🎤 Configuración de Google Speech-to-Text (GRATIS)

## ✅ **60 minutos/mes GRATIS - Sin necesidad de tarjeta de crédito inicialmente**

Google Cloud ofrece **$300 USD en créditos gratuitos** durante 90 días, y después:
- **60 minutos/mes GRATIS** de transcripción de audio estándar
- Compatible con Render Free Tier (Pure Python, sin dependencias del sistema)

---

## 📋 **PASO 1: Crear proyecto en Google Cloud**

### 1.1 Ir a Google Cloud Console
```
https://console.cloud.google.com/
```

### 1.2 Crear nuevo proyecto
- Clic en **"Select a project"** (arriba izquierda)
- Clic en **"NEW PROJECT"**
- Nombre: `EvalAI-Speech`
- Clic en **"CREATE"**

---

## 📋 **PASO 2: Activar Speech-to-Text API**

### 2.1 Buscar la API
```
https://console.cloud.google.com/marketplace/product/google/speech.googleapis.com
```

### 2.2 Activar
- Clic en **"ENABLE"**
- Esperar 10-20 segundos

---

## 📋 **PASO 3: Crear Service Account (credenciales)**

### 3.1 Ir a IAM & Admin
```
https://console.cloud.google.com/iam-admin/serviceaccounts
```

### 3.2 Crear Service Account
- Clic en **"CREATE SERVICE ACCOUNT"**
- **Service account name**: `evalai-speech`
- **Service account ID**: `evalai-speech` (se genera automáticamente)
- Clic en **"CREATE AND CONTINUE"**

### 3.3 Asignar rol
- **Role**: Buscar y seleccionar `Cloud Speech Client`
- Clic en **"CONTINUE"**
- Clic en **"DONE"**

### 3.4 Generar clave JSON
- Clic en el service account recién creado (`evalai-speech@...`)
- Ir a pestaña **"KEYS"**
- Clic en **"ADD KEY"** → **"Create new key"**
- Tipo: **JSON**
- Clic en **"CREATE"**
- Se descargará un archivo `.json` (guardarlo en lugar seguro)

---

## 📋 **PASO 4: Configurar en Render**

### 4.1 Abrir el archivo JSON descargado
Debería verse algo así:
```json
{
  "type": "service_account",
  "project_id": "evalai-speech-123456",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "evalai-speech@evalai-speech-123456.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### 4.2 Convertir a una sola línea (importante)
**Opción A - PowerShell:**
```powershell
# Leer el archivo y convertirlo a una sola línea
$json = Get-Content "ruta/al/archivo-clave.json" -Raw | ConvertFrom-Json | ConvertTo-Json -Compress
Write-Host $json
# Copiar el resultado
```

**Opción B - Python:**
```python
import json

with open('ruta/al/archivo-clave.json', 'r') as f:
    data = json.load(f)

# Imprimir en una sola línea
print(json.dumps(data, separators=(',', ':')))
```

**Opción C - Manual (online):**
```
https://jsoncompressor.com/
```
- Pegar el JSON completo
- Clic en "Compress"
- Copiar el resultado

### 4.3 Agregar a Render
1. Ir a tu servicio en Render: https://dashboard.render.com/
2. Clic en tu servicio **"evalai-backend"**
3. Ir a **"Environment"**
4. Clic en **"Add Environment Variable"**
5. **Key**: `GOOGLE_SPEECH_CREDENTIALS_JSON`
6. **Value**: Pegar el JSON comprimido (una sola línea)
7. Clic en **"Save Changes"**

---

## 📋 **PASO 5: Verificar configuración local (opcional)**

### 5.1 Crear `.env` en `backend_django/`
```env
GOOGLE_SPEECH_CREDENTIALS_JSON={"type":"service_account","project_id":"evalai-speech-123456",...}
```

### 5.2 Probar transcripción
```bash
cd backend_django
python manage.py shell
```

```python
from core.services.whisper_loader import get_whisper_service

service = get_whisper_service()
print(f"Disponible: {service.is_available()}")

# Probar con audio de prueba
result = service.transcribe_audio('ruta/al/audio.wav', language='es-ES')
print(f"Transcripción: {result}")
```

---

## 🎯 **Códigos de idioma soportados**

| Idioma | Código | Ejemplo |
|--------|--------|---------|
| **Español (España)** | `es-ES` | Hola, buenos días |
| **Español (México)** | `es-MX` | ¿Qué onda? |
| **Español (Argentina)** | `es-AR` | ¿Cómo andás? |
| **Catalán** | `ca-ES` | Bon dia |
| **Inglés (US)** | `en-US` | Hello, good morning |
| **Inglés (UK)** | `en-GB` | Good morning, mate |
| **Francés** | `fr-FR` | Bonjour |
| **Alemán** | `de-DE` | Guten Tag |
| **Italiano** | `it-IT` | Buongiorno |
| **Portugués** | `pt-BR` | Olá, bom dia |

Ver lista completa: https://cloud.google.com/speech-to-text/docs/languages

---

## 📊 **Límites y costos**

### **Nivel gratuito (siempre gratis)**
- ✅ **60 minutos/mes** de transcripción estándar
- ✅ Sin necesidad de tarjeta después de créditos iniciales
- ✅ Se renueva cada mes

### **Después de 60 minutos**
Si superas los 60 minutos/mes:
- **$0.006 USD/15 segundos** = ~$1.44 USD/hora
- **Ejemplo:** 100 minutos/mes = 40 minutos extras = ~$3.84 USD

### **Monitoreo de uso**
Ver uso actual:
```
https://console.cloud.google.com/billing/
```

---

## ⚠️ **Solución de problemas**

### Error: "API Speech-to-Text is not enabled"
```bash
# Activar manualmente:
gcloud services enable speech.googleapis.com --project=TU_PROJECT_ID
```

### Error: "Invalid credentials"
- Verificar que el JSON esté en **una sola línea** (sin saltos de línea)
- Verificar que no haya espacios extra al inicio/final
- Regenerar la clave si es necesario

### Error: "RESOURCE_EXHAUSTED: Quota exceeded"
- Has superado los 60 minutos/mes gratuitos
- Opciones:
  1. Esperar al próximo mes
  2. Agregar método de pago (se cobrará el excedente)
  3. Usar otra cuenta de Google Cloud (nueva cuota de 60 min)

---

## 🚀 **Deploy completo**

```bash
# 1. Commit cambios
git add .
git commit -m "FEAT: Migración a Google Speech-to-Text (60 min/mes gratis)"
git push

# 2. Configurar credenciales en Render (ver PASO 4)

# 3. Render auto-despliega en ~2-3 minutos

# 4. Probar transcripción en tu app
```

---

## 📝 **Ventajas de Google Speech-to-Text**

✅ **60 minutos/mes gratis** (suficiente para uso educativo)  
✅ **Pure Python** (no requiere FFmpeg/compilación)  
✅ **Compatible con Render Free Tier**  
✅ **Alta precisión** (mejor que Whisper small)  
✅ **125+ idiomas soportados**  
✅ **Puntuación automática**  
✅ **Sin instalación de modelos** (sin descargas de 500MB+)  
✅ **Latencia baja** (~2-3 segundos)  

---

## 🆚 **Comparación final de opciones**

| Característica | Google Speech | OpenAI Whisper (local) | faster-whisper |
|----------------|---------------|------------------------|----------------|
| **Costo** | 60 min/mes gratis | Gratis | Gratis |
| **Render Free Tier** | ✅ Sí | ❌ No (RAM) | ❌ No (FFmpeg) |
| **Compilación** | ❌ No | ❌ No | ✅ Sí (falla) |
| **Dependencias sistema** | ❌ No | ❌ No | ✅ Sí (libav) |
| **RAM requerida** | ~50MB | ~2GB | ~200MB |
| **Primera ejecución** | Instantánea | 5-10 min | N/A |
| **Latencia** | 2-3s | 10-30s | 2-5s |
| **Precisión** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recomendación:** Google Speech-to-Text es la mejor opción para Render Free Tier.
