# 🤖 Configuración de DeepSeek R1T2 Chimera para EvalAI

## 📋 Descripción

EvalAI ahora usa **DeepSeek R1T2 Chimera** via OpenRouter para generar rúbricas educativas. Este modelo es:
- ✅ **Gratuito** ($0/M tokens)
- ✅ **Más rápido** que Gemini (20% más rápido que R1)
- ✅ **Mejor rendimiento** de razonamiento
- ✅ **Contexto largo** (hasta 60k tokens)

---

## 🔑 Configuración de la Clave API

### 1. Obtener Clave API de OpenRouter

1. **Ve a**: https://openrouter.ai/
2. **Regístrate** o inicia sesión
3. **Ve a**: https://openrouter.ai/keys
4. **Crea una nueva clave API**
5. **Copia la clave** (formato: `sk-or-v1-...`)

### 2. Configurar en EvalAI

**Opción A: Archivo .env (Recomendado)**
```bash
# Crear archivo .env en backend_django/
OPENROUTER_API_KEY=sk-or-v1-tu-clave-aqui
```

**Opción B: Configuración directa**
Editar `backend_django/config/settings.py`:
```python
OPENROUTER_API_KEY = config('OPENROUTER_API_KEY', default='sk-or-v1-tu-clave-aqui')
```

### 3. Reiniciar Servidor

```bash
# Detener servidor Django
Ctrl+C

# Reiniciar servidor
python manage.py runserver 8000
```

---

## 🚀 Características del Nuevo Sistema

### ✅ Ventajas de DeepSeek R1T2 Chimera:
- **Gratuito**: Sin costos por tokens
- **Rápido**: 20% más rápido que modelos anteriores
- **Inteligente**: Mejor razonamiento y análisis
- **Contexto largo**: Hasta 60k tokens de contexto
- **Estable**: Menos errores y fallos

### 🎯 Criterios Específicos por Materia:
- **Geografía**: Conocimiento geográfico, análisis territorial, organización espacial
- **Historia**: Conocimiento histórico, análisis histórico, interpretación de fuentes
- **Ciencias**: Conocimiento científico, metodología científica, análisis de datos
- **Matemáticas**: Comprensión conceptual, resolución de problemas, precisión
- **Presentaciones**: Contenido y conocimiento, comunicación oral, estructura
- **Escritura**: Contenido y desarrollo, estructura, expresión y estilo
- **Proyectos**: Planificación y metodología, investigación y fuentes, creatividad

---

## 🔧 Configuración Avanzada

### Variables de Entorno Disponibles:
```python
OPENROUTER_API_KEY = "sk-or-v1-..."           # Clave API de OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"  # URL base
DEEPSEEK_MODEL = "tngtech/deepseek-r1t2-chimera:free"  # Modelo específico
DEEPSEEK_TIMEOUT = 60                          # Timeout en segundos
DEEPSEEK_MAX_TOKENS = 4096                     # Tokens máximos
DEEPSEEK_CACHE_TTL = 86400                     # Cache TTL (24 horas)
```

### Fallback Inteligente:
Si la API de DeepSeek no está disponible, el sistema usa criterios específicos basados en el tema del prompt, no criterios genéricos.

---

## 📞 Soporte

Si tienes problemas:
1. **Verifica la clave API** en https://openrouter.ai/keys
2. **Revisa los logs** del servidor Django
3. **Comprueba la conexión** a internet
4. **Reinicia el servidor** después de cambios

---

## 🎉 ¡Listo!

Una vez configurado, EvalAI generará rúbricas más inteligentes y específicas usando DeepSeek R1T2 Chimera.
