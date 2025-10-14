# 🤖 Servicio de Generación de Rúbricas con IA (Gemini)

## 📋 Descripción

Este servicio integra **Google Gemini AI** para generar rúbricas educativas automáticamente a partir de descripciones en lenguaje natural. Incluye caché inteligente, manejo de errores, rate limiting y fallback a plantillas.

---

## 🚀 Configuración

### 1. Variables de Entorno

Agregar en `backend_django/config/settings.py`:

```python
# Gemini AI Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'tu-api-key-aqui')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
GEMINI_DEFAULT_MODEL = 'gemini-pro'
GEMINI_TIMEOUT = 30  # segundos
GEMINI_MAX_TOKENS = 2048
GEMINI_MAX_PROMPT_LENGTH = 2000
GEMINI_CACHE_TTL = 86400  # 24 horas

# Rate limiting
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'user': '10/minute',  # 10 solicitudes por minuto
}
```

### 2. Dependencias

Instalar las librerías necesarias:

```bash
pip install google-generativeai requests
```

### 3. Migración de Base de Datos

Aplicar las migraciones para los campos de auditoría AI:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🔧 Arquitectura

### Backend

#### **1. GeminiClient** (`rubrics/services/gemini_service.py`)

Cliente principal para interactuar con la API de Gemini.

**Métodos principales:**

- `generate_rubric()`: Genera una rúbrica a partir de un prompt
- `get_fallback_rubric()`: Devuelve plantilla genérica si Gemini falla
- `_call_api()`: Maneja llamadas HTTP con reintentos
- `_parse_json_response()`: Extrae y valida JSON de respuestas
- `_validate_rubric_schema()`: Valida estructura de datos

**Características:**

✅ Caché basado en hash SHA-256 del prompt  
✅ Reintentos automáticos (max 3)  
✅ Rate limiting con backoff exponencial  
✅ Validación de esquema JSON  
✅ Normalización de pesos (suma 100%)  
✅ Logging detallado

#### **2. API Endpoint** (`core/views.py`)

**Ruta:** `POST /api/rubrics/generate/`

**Body:**
```json
{
  "prompt": "rúbrica para comprensión oral 6º primaria, 4 criterios",
  "language": "es",
  "max_criteria": 4,
  "levels_per_criterion": 4,
  "max_score": 10,
  "use_cache": true,
  "subject_id": 1
}
```

**Response:**
```json
{
  "title": "Rúbrica de Comprensión Oral",
  "description": "Evalúa habilidades de comprensión oral...",
  "criteria": [
    {
      "name": "Claridad",
      "description": "Capacidad de expresarse claramente",
      "weight": 0.3,
      "levels": [
        {
          "level_name": "Excelente",
          "score": 10,
          "description": "Se expresa con total claridad..."
        }
      ]
    }
  ],
  "meta": {
    "model": "gemini-pro",
    "timestamp": "2025-10-14T02:20:00Z",
    "confidence": 0.85
  },
  "generation_meta": {
    "prompt_hash": "abc123...",
    "prompt_objective": "comprensión oral 6º primaria",
    "language": "es",
    "from_cache": false,
    "fallback": false
  }
}
```

**Códigos de respuesta:**

- `200 OK`: Rúbrica generada exitosamente
- `400 Bad Request`: Prompt inválido o parámetros fuera de rango
- `429 Too Many Requests`: Rate limit alcanzado
- `500 Internal Server Error`: Error en generación

#### **3. Rate Limiting**

```python
class GeminiGenerateThrottle(UserRateThrottle):
    rate = '10/min'  # 10 solicitudes por minuto por usuario
```

#### **4. Modelo de Auditoría**

Nuevos campos en el modelo `Rubric`:

```python
ai_generated = models.BooleanField(default=False)
ai_model = models.CharField(max_length=100, blank=True, null=True)
ai_prompt_hash = models.CharField(max_length=64, blank=True, null=True)
ai_confidence = models.FloatField(blank=True, null=True)
```

---

### Frontend

#### **AIGenerateModal.jsx**

Componente React para la interfaz de generación con IA.

**Props:**

- `isOpen`: Control de visibilidad
- `onClose`: Callback al cerrar
- `onGenerated`: Callback con datos generados

**Características:**

✨ Formulario con prompt libre (max 2000 chars)  
⚙️ Configuración avanzada (idioma, criterios, niveles, puntuación)  
👁️ Vista previa antes de aplicar  
💾 Integración con caché  
⚠️ Manejo de errores y rate limiting  
🎨 Indicadores visuales (IA, caché, fallback)

**Integración en RubricEditorPage:**

```jsx
import AIGenerateModal from '../components/AIGenerateModal';

const [showAIModal, setShowAIModal] = useState(false);

const handleAIGenerated = (aiData) => {
  // Poblar formulario con datos de IA
  setRubric({ ...rubric, title: aiData.title, description: aiData.description });
  setCriteria(/* convertir criterios de IA a formato interno */);
};

// Botón para abrir modal
<button onClick={() => setShowAIModal(true)}>
  <span className="material-symbols-outlined">auto_awesome</span>
  Generar con IA
</button>

// Render del modal
<AIGenerateModal
  isOpen={showAIModal}
  onClose={() => setShowAIModal(false)}
  onGenerated={handleAIGenerated}
/>
```

---

## 📖 Ejemplos de Uso

### Ejemplo 1: Comprensión Oral

**Prompt:**
```
rúbrica para evaluar comprensión oral en 6º de primaria, 
enfocada en claridad, vocabulario, argumentación y expresión
```

**Resultado:**
- 4 criterios con pesos equilibrados (25% cada uno)
- 4 niveles por criterio (Excelente, Bueno, Suficiente, Insuficiente)
- Descripciones específicas y observables

### Ejemplo 2: Proyecto de Investigación

**Prompt:**
```
rúbrica para evaluar proyectos de investigación científica en secundaria,
5 criterios: planteamiento, metodología, análisis, conclusiones y presentación
```

**Resultado:**
- 5 criterios con pesos personalizados
- Descripciones técnicas apropiadas para nivel secundaria
- Niveles de desempeño claros y medibles

### Ejemplo 3: Trabajo en Equipo

**Prompt:**
```
rúbrica para trabajo colaborativo en proyectos grupales de primaria,
evaluar participación, comunicación y responsabilidad
```

**Resultado:**
- 3 criterios socio-emocionales
- Descripciones con indicadores conductuales
- Adaptado a nivel cognitivo de primaria

---

## 🔐 Seguridad

### Medidas Implementadas

1. **API Key Protection:**
   - Clave almacenada en variables de entorno
   - No se registra en logs (logging configuration)
   - Nunca se expone al frontend

2. **Rate Limiting:**
   - 10 solicitudes/minuto por usuario autenticado
   - Respuesta `429 Too Many Requests` al exceder
   - Mensaje claro al usuario en frontend

3. **Validación de Inputs:**
   - Max 2000 caracteres en prompt
   - Rangos válidos para parámetros numéricos
   - Autenticación JWT obligatoria

4. **Sanitización:**
   - Validación de esquema JSON con estructura esperada
   - Normalización de pesos para evitar inconsistencias
   - Limpieza de caracteres especiales

---

## 💾 Sistema de Caché

### Estrategia

**Clave de caché:**
```python
cache_key = f"rubric_gen:{sha256(prompt|language|max_criteria|levels|model)}"
```

**TTL:** 24 horas (86400 segundos)

**Ventajas:**

- ✅ Reduce llamadas a API (ahorro de costos)
- ✅ Respuestas instantáneas para prompts repetidos
- ✅ Hash único evita colisiones
- ✅ TTL configurable por entorno

### Backend de Caché

Por defecto usa **LocMemCache** (memoria local). Para producción, configurar Redis:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## 🛡️ Manejo de Errores

### Estrategias de Fallback

1. **Reintentos automáticos** (max 3 con backoff exponencial)
2. **Fallback a plantilla genérica** si API falla completamente
3. **Mensajes de error descriptivos** al usuario

### Tipos de Error

| Error | Código | Acción |
|-------|--------|--------|
| API key inválida | 401 | Reintentar con clave correcta |
| Rate limit Gemini | 429 | Esperar 2^n segundos |
| Timeout | 408 | Reintentar hasta 3 veces |
| Respuesta malformada | 500 | Usar fallback |
| Ninguna API disponible | 503 | Usar plantilla stub |

---

## 🧪 Testing

### Tests Recomendados

```python
# test_gemini_service.py

def test_generate_rubric_valid_prompt():
    """Test generación con prompt válido"""
    client = GeminiClient(api_key='test-key')
    result = client.generate_rubric("rúbrica para lectura primaria")
    assert 'title' in result
    assert 'criteria' in result

def test_cache_hit():
    """Test que caché funciona"""
    # Primera llamada
    result1 = client.generate_rubric("test prompt")
    # Segunda llamada (debe venir de caché)
    result2 = client.generate_rubric("test prompt")
    assert result2['from_cache'] == True

def test_fallback_on_api_failure():
    """Test fallback cuando API falla"""
    # Simular fallo de API
    result = client.get_fallback_rubric("test")
    assert result['generation_meta']['fallback'] == True

def test_rate_limiting():
    """Test que rate limit funciona"""
    for i in range(11):  # Exceder límite de 10/min
        response = client.post('/api/rubrics/generate/', {})
    assert last_response.status_code == 429
```

---

## 📊 Métricas y Monitoreo

### Logs Importantes

```python
logger.info(f"Generando rúbrica con prompt: {prompt[:50]}...")
logger.info(f"Rúbrica obtenida de cache: {cache_key}")
logger.warning("Usando rúbrica de fallback")
logger.error(f"Error de Gemini: {str(e)}")
```

### Métricas a Monitorear

- ✅ Tasa de aciertos de caché (cache hit rate)
- ✅ Tiempo promedio de generación
- ✅ Tasa de errores vs éxitos
- ✅ Uso de fallback vs IA real
- ✅ Rate limiting triggers

---

## 🎯 Próximos Pasos

### Mejoras Futuras

1. **Streaming de respuesta** para feedback en tiempo real
2. **Refinamiento iterativo** (usuario puede pedir ajustes)
3. **Templates personalizados** por materia/nivel
4. **Multi-idioma avanzado** (detección automática)
5. **Análisis de sentimiento** del prompt para sugerir configuración
6. **Exportación directa a PDF** de rúbricas generadas
7. **Historial de generaciones** del usuario
8. **Comparación lado a lado** de múltiples generaciones

---

## 📞 Soporte

Para problemas o preguntas:

1. Verificar logs del servicio: `backend_django/logs/`
2. Revisar configuración de API key en settings.py
3. Comprobar rate limiting si hay errores 429
4. Validar formato de prompt (max 2000 chars)

**Contacto:** Ver documentación principal del proyecto

---

## 📄 Licencia

Parte del proyecto EvalAI - Sistema de Evaluación Educativa  
© 2025 - Todos los derechos reservados
