# Migración de HuggingFace API a Whisper.cpp Local

**Fecha:** 2025-11-08  
**Commit:** e6bcf4c5  
**Razón:** HuggingFace Inference API deprecated (HTTP 410/404), APIs inestables

---

## ✅ Cambios Realizados

### 1. Eliminaciones (HuggingFace)
- ❌ `huggingface_whisper_service.py` (ya no se importa)
- ❌ `HUGGINGFACE_API_KEY` de settings.py
- ❌ `HUGGINGFACE_TIMEOUT`, `HUGGINGFACE_MAX_FILE_SIZE`
- ❌ Import: `from .services.huggingface_whisper_service import ...`

### 2. Nuevos Archivos
- ✅ `backend_django/core/services/whisper_cpp_service.py`
  - `WhisperCppService`: Ejecuta whisper.cpp localmente vía subprocess
  - `get_whisper_client()`: Singleton factory
  - Método: `transcribe_audio(file_path, language='es')`

- ✅ `backend_django/install_whisper.sh`
  - Instala: `build-essential`, `cmake`, `curl`, `git`
  - Clone: `whisper.cpp` → `/opt/whisper.cpp`
  - Compila: `make -j4`
  - Descarga: modelo `medium` (~1.5GB)

### 3. Configuración

**settings.py:**
```python
WHISPER_CPP_PATH = config('WHISPER_CPP_PATH', default='/opt/whisper.cpp')
WHISPER_MODEL_PATH = config('WHISPER_MODEL_PATH', default='/opt/whisper.cpp/models/ggml-medium.bin')
WHISPER_TIMEOUT = config('WHISPER_TIMEOUT', default=120, cast=int)
WHISPER_MAX_FILE_SIZE = config('WHISPER_MAX_FILE_SIZE', default=25 * 1024 * 1024, cast=int)
```

**render.yaml:**
```yaml
buildCommand: |
  cd backend_django
  chmod +x install_whisper.sh
  bash install_whisper.sh          # ← Instala Whisper.cpp
  pip install -r requirements.txt
  python manage.py collectstatic --noinput

envVars:
  - key: WHISPER_CPP_PATH
    value: /opt/whisper.cpp
  - key: WHISPER_MODEL_PATH
    value: /opt/whisper.cpp/models/ggml-medium.bin
```

### 4. Backend (views.py)

**Antes:**
```python
from .services.huggingface_whisper_service import huggingface_whisper_client, HuggingFaceWhisperError

whisper_client = huggingface_whisper_client
if not whisper_client:
    raise Exception("Verifica HUGGINGFACE_API_KEY")
transcription = whisper_client.transcribe_audio(temp_file_path, language='es')
```

**Después:**
```python
from .services.whisper_cpp_service import get_whisper_client, WhisperCppError

whisper_client = get_whisper_client()
if not whisper_client.is_available():
    raise Exception("Verifica instalación de Whisper.cpp")
transcription = whisper_client.transcribe_audio(temp_file_path, language='es')
```

---

## 🔧 Comando Ejecutado

```bash
./whisper.cpp/main \
  -m /opt/whisper.cpp/models/ggml-medium.bin \
  -f /tmp/audio.wav \
  -l es \
  -otxt \
  -of /tmp/output \
  --no-timestamps \
  -t 4
```

**Salida:** Lee `/tmp/output.txt` con transcripción

---

## 📊 Ventajas del Cambio

| Aspecto | HuggingFace API | Whisper.cpp Local |
|---------|----------------|-------------------|
| **Dependencia Externa** | ✅ Sí (API calls) | ❌ No (100% local) |
| **Estabilidad** | ❌ Errores 410/404 | ✅ Siempre disponible |
| **Latencia** | 🐌 3-15s (red) | ⚡ 2-5s (CPU) |
| **Costo** | 💰 Gratis pero limitado | 💰 $0 (solo CPU) |
| **Rate Limits** | ❌ Sí | ✅ No |
| **Privacidad** | ⚠️ Datos salen del servidor | ✅ Todo local |

---

## 🚨 Posibles Problemas

### 1. Timeout en Build (Render Free Tier)
**Síntoma:** Build excede 15 minutos  
**Solución:**
```bash
# En install_whisper.sh cambiar:
bash ./models/download-ggml-model.sh small  # En lugar de medium
```

### 2. Modelo No Descarga
**Síntoma:** `❌ ERROR: Model not found!`  
**Solución:**
- Verificar conectividad en Render
- Usar `curl` directo:
```bash
curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin \
  -o /opt/whisper.cpp/models/ggml-medium.bin
```

### 3. Falta Espacio en Disco
**Síntoma:** `No space left on device`  
**Solución:** Modelo `small` (461MB) en lugar de `medium` (1.5GB)

---

## 🧪 Testing

### Logs Esperados (Éxito)
```
🎙️  Installing Whisper.cpp
========================================
📦 Installing build dependencies...
✅ Dependencies installed
📥 Cloning whisper.cpp repository...
✅ Repository cloned
🔨 Compiling whisper.cpp...
✅ Compilation complete
📥 Downloading medium model...
✅ Model downloaded: ggml-medium.bin
🔍 Verifying installation...
✅ Executable found: /opt/whisper.cpp/main
✅ Model found: /opt/whisper.cpp/models/ggml-medium.bin
   Size: 1532MB
✅ Whisper.cpp installation complete!
```

### Logs de Transcripción (Runtime)
```
[AUDIO] Iniciando transcripción para estudiante 7
[AUDIO] Whisper.cpp disponible: True
[WHISPER.CPP] Transcribing audio: /tmp/tmpb9rlz4cr.wav
[WHISPER.CPP] File size: 209918 bytes
[WHISPER.CPP] Language: es
[WHISPER.CPP] Running command: ./whisper.cpp/main -m ...
[WHISPER.CPP] Return code: 0
[WHISPER.CPP] Transcription length: 45 characters
[WHISPER.CPP] Preview: Hola, esto es una prueba de transcripción...
[AUDIO] Transcripción completada: Hola, esto es una prueba...
```

---

## 🔄 Rollback (Si Necesario)

```bash
git revert e6bcf4c5
git push
```

Restaurar variables en Render Dashboard:
- `HUGGINGFACE_API_KEY`
- Quitar `WHISPER_CPP_PATH`, `WHISPER_MODEL_PATH`

---

## 📚 Referencias

- **Whisper.cpp GitHub:** https://github.com/ggerganov/whisper.cpp
- **Modelos disponibles:** https://huggingface.co/ggerganov/whisper.cpp
- **Documentación Render Build:** https://render.com/docs/deploys
