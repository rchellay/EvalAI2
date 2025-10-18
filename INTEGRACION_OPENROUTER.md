# 🤖 Integración OpenRouter AI - Modelos Open Source Gratuitos

## 📋 Descripción

EvalAI ahora utiliza **OpenRouter** como plataforma unificada para acceder a múltiples modelos de IA open source gratuitos de alta calidad, reemplazando completamente la dependencia de Gemini.

---

## 🚀 Modelos Implementados

### 🥇 **Qwen3-235B-A22B (Modelo Principal)**
- **Uso**: Generación de rúbricas detalladas y criterios personalizados
- **Fortalezas**: 
  - Excelente comprensión multilingüe (español, catalán, inglés)
  - Sigue instrucciones con precisión
  - Modo razonamiento estructurado
  - Razonamiento tipo Claude/GPT-4
- **Ideal para**: 
  - ✅ Generación de rúbricas educativas
  - ✅ Criterios de evaluación personalizados
  - ✅ Análisis de textos de estudiantes
  - ✅ Adaptaciones de evaluación

### 🥈 **DeepSeek R1T2 Chimera (Análisis Avanzado)**
- **Uso**: Análisis profundo y feedback educativo
- **Fortalezas**:
  - Excelente razonamiento lógico y analítico
  - Contexto enorme (164K tokens)
  - Rápido y consistente
- **Ideal para**:
  - ✅ Resumir portafolios de estudiantes
  - ✅ Analizar evidencias de aprendizaje
  - ✅ Generar feedback educativo estructurado
  - ✅ Recomendaciones personalizadas

### 🥉 **GLM 4.5 Air (Tareas Rápidas)**
- **Uso**: Respuestas rápidas y tareas ligeras
- **Fortalezas**:
  - Modelo balanceado y rápido
  - Razonamiento controlable
  - Muy eficiente
- **Ideal para**:
  - ✅ Evaluaciones rápidas
  - ✅ Checklists simples
  - ✅ Mejora de comentarios
  - ✅ Respuestas inmediatas

---

## 🔧 Configuración

### Variables de Entorno

```python
# OpenRouter AI Configuration
OPENROUTER_API_KEY = "tu-clave-openrouter-aqui"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_TIMEOUT = 60
OPENROUTER_CACHE_TTL = 86400  # 24 horas

# Modelos específicos
QWEN_MODEL = "qwen/qwen3-235b-a22b:free"
DEEPSEEK_MODEL = "tngtech/deepseek-r1t2-chimera:free"
GLM_MODEL = "z-ai/glm-4.5-air:free"
```

### Dependencias

```bash
pip install requests openai
```

---

## 🏗️ Arquitectura

### Backend

#### **OpenRouterClient** (`core/services/openrouter_service.py`)

**Métodos principales:**
- `generate_rubric()`: Genera rúbricas usando Qwen3-235B
- `generate_analysis()`: Análisis detallado usando DeepSeek R1T2
- `generate_quick_response()`: Respuestas rápidas usando GLM 4.5 Air
- `_call_openrouter_api()`: Maneja llamadas HTTP con reintentos
- `_parse_rubric_response()`: Extrae y valida JSON de respuestas
- `_validate_rubric_schema()`: Valida estructura de datos

**Características:**
- ✅ Caché inteligente basado en hash SHA-256
- ✅ Reintentos automáticos (max 3) con backoff exponencial
- ✅ Rate limiting integrado
- ✅ Validación de esquema JSON
- ✅ Normalización de pesos (suma 100%)
- ✅ Logging detallado
- ✅ Fallback a plantillas cuando la IA no está disponible

#### **Endpoints API Actualizados**

- `POST /api/rubrics/generate/` - Generación de rúbricas con Qwen3-235B
- `POST /api/evaluaciones/mejorar-comentario/` - Mejora de comentarios con GLM 4.5 Air
- `POST /api/evaluaciones/audio/` - Análisis de audio con DeepSeek R1T2
- `GET /api/students/{id}/recommendations/` - Recomendaciones con DeepSeek R1T2

### Frontend

#### **Componentes Actualizados**

- **AIGenerateModal**: Actualizado para mostrar "Powered by OpenRouter AI (Qwen3-235B)"
- **WidgetIA**: Usa nuevos endpoints de análisis
- **WidgetComentariosRapidos**: Integrado con GLM 4.5 Air para mejora de comentarios

---

## 🎯 Casos de Uso

### 1. **Generación de Rúbricas** (Qwen3-235B)
```python
# Ejemplo de uso
rubric = openrouter_client.generate_rubric(
    prompt="Evaluación de participación en clase",
    language="es",
    num_criteria=4,
    num_levels=4,
    max_score=10
)
```

### 2. **Análisis de Evaluaciones** (DeepSeek R1T2)
```python
# Ejemplo de uso
analysis = openrouter_client.generate_analysis(
    prompt="Analiza estas evaluaciones y genera recomendaciones",
    context="Matemáticas: 8/10, Ciencias: 6/10, Lengua: 9/10"
)
```

### 3. **Mejora de Comentarios** (GLM 4.5 Air)
```python
# Ejemplo de uso
improved_comment = openrouter_client.generate_quick_response(
    prompt="Mejora este comentario: 'Buen trabajo' haciéndolo más constructivo"
)
```

---

## 📊 Ventajas de la Nueva Integración

### ✅ **Costos**
- **Gratuito**: Todos los modelos son completamente gratuitos
- **Sin límites**: No hay restricciones de uso diario
- **Escalable**: Puede manejar múltiples usuarios simultáneos

### ✅ **Calidad**
- **Modelos de última generación**: Qwen3-235B, DeepSeek R1T2, GLM 4.5 Air
- **Especialización**: Cada modelo optimizado para su tarea específica
- **Multilingüe**: Soporte nativo para español, catalán e inglés

### ✅ **Confiabilidad**
- **Fallback inteligente**: Plantillas de respaldo cuando la IA no está disponible
- **Caché**: Respuestas frecuentes se almacenan para mejorar rendimiento
- **Reintentos**: Manejo robusto de errores de red

### ✅ **Flexibilidad**
- **Multi-modelo**: Diferentes modelos para diferentes tareas
- **Configurable**: Fácil cambio de modelos o parámetros
- **Extensible**: Fácil añadir nuevos modelos en el futuro

---

## 🔄 Migración desde Gemini

### Cambios Realizados

1. **Servicios**:
   - ❌ Eliminado: `gemini_service.py`
   - ❌ Eliminado: `deepseek_service.py`
   - ✅ Nuevo: `openrouter_service.py`

2. **Configuración**:
   - ❌ Eliminado: Variables `GEMINI_*`
   - ❌ Eliminado: Variables `DEEPSEEK_*`
   - ✅ Nuevo: Variables `OPENROUTER_*`

3. **Vistas**:
   - ✅ Actualizado: Todas las referencias a `DeepSeekClient` → `openrouter_client`
   - ✅ Actualizado: Todas las referencias a `GeminiServiceError` → `OpenRouterServiceError`
   - ✅ Actualizado: Métodos de IA para usar nuevos endpoints

4. **Frontend**:
   - ✅ Actualizado: Referencias visuales a "Powered by Google Gemini"
   - ✅ Actualizado: Componentes para usar nuevos endpoints

---

## 🧪 Testing

### Pruebas Realizadas

- ✅ **Qwen3-235B**: Generación de rúbricas funcional
- ✅ **DeepSeek R1T2**: Análisis de evaluaciones funcional
- ✅ **GLM 4.5 Air**: Mejora de comentarios funcional
- ✅ **Backend**: Endpoints protegidos correctamente
- ✅ **Frontend**: Componentes actualizados

### Scripts de Prueba

```bash
# Probar integración completa
python test_openrouter_integration.py
```

---

## 🚀 Próximos Pasos

### Mejoras Futuras

1. **Modelos Adicionales**:
   - Añadir más modelos especializados
   - Implementar selección automática de modelo

2. **Optimizaciones**:
   - Caché más inteligente
   - Compresión de respuestas
   - Streaming de respuestas largas

3. **Monitoreo**:
   - Métricas de uso por modelo
   - Análisis de rendimiento
   - Alertas de fallos

---

## 📞 Soporte

Para problemas o preguntas sobre la integración de OpenRouter:

1. **Verificar configuración**: Revisar variables de entorno
2. **Revisar logs**: Comprobar logs de Django para errores
3. **Probar conectividad**: Verificar acceso a OpenRouter API
4. **Fallback**: El sistema funciona con plantillas si la IA no está disponible

---

**🎉 ¡La migración a OpenRouter está completa y funcionando!**
