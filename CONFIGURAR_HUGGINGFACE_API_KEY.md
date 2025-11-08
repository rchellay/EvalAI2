# Configurar HuggingFace API Key para Transcripción de Audio

## Problema
El error `500 Internal Server Error` en `/api/evaluaciones/audio/` se debe a que **no hay una API key de HuggingFace configurada** en Render.

Sin API key, la API gratuita de HuggingFace tiene límites muy estrictos y rechaza la mayoría de peticiones.

## Solución: Obtener y Configurar API Key (GRATIS)

### Paso 1: Crear cuenta y obtener API key (2 minutos)

1. Ve a https://huggingface.co/join
2. Crea una cuenta gratuita (puedes usar Google/GitHub)
3. Ve a https://huggingface.co/settings/tokens
4. Click en **"New token"**
5. Nombre: `EvalAI Whisper`
6. Tipo: **Read** (solo lectura es suficiente)
7. Click **"Generate"**
8. **COPIA EL TOKEN** (empieza con `hf_...`)

### Paso 2: Configurar en Render (1 minuto)

1. Ve al dashboard de Render: https://dashboard.render.com/
2. Selecciona tu servicio **evalai2**
3. Ve a **Environment** en el menú lateral
4. Click **"Add Environment Variable"**
5. Agrega:
   - **Key**: `HUGGINGFACE_API_KEY`
   - **Value**: `hf_xxxxxxxxxxxxxxxxxxxxxxxxx` (el token que copiaste)
6. Click **"Save Changes"**

### Paso 3: Redesplegar

Render redesplegará automáticamente después de guardar la variable de entorno.

Espera ~2-3 minutos y prueba de nuevo la transcripción de audio.

## Verificación

Después de configurar, verás en los logs de Render:
- ✅ Sin el warning `HUGGINGFACE_API_KEY no configurada`
- ✅ La transcripción funciona correctamente

## Límites de la API Gratuita

**CON API key (gratis)**:
- ✅ 1000 requests/hora
- ✅ Suficiente para uso normal de EvalAI
- ✅ Sin costo

**SIN API key**:
- ❌ ~10 requests/día
- ❌ Muy lento
- ❌ Rechaza mayoría de peticiones

## Alternativa: Usar OpenAI Whisper (De pago)

Si prefieres usar OpenAI Whisper en lugar de HuggingFace:

1. Obtén API key de OpenAI: https://platform.openai.com/api-keys
2. Configura en Render:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: `sk-xxxxxxxxxxxxxxxxxxxxxxxxx`
3. Cambia el código para usar OpenAI en lugar de HuggingFace

**Costo**: ~$0.006 por minuto de audio (~$0.36 por hora)
