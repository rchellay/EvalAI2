# 🎓 Asistente de Investigación Educativa con IA

## Descripción

Chatbot inteligente que responde preguntas sobre educación basándose **exclusivamente en evidencia científica real**. No inventa referencias: busca estudios reales de Semantic Scholar y OpenAlex, y solo responde con lo que dicen esos estudios.

## ✨ Características

### 🔬 Búsqueda Científica Real
- **Semantic Scholar API**: Base de datos con millones de papers académicos
- **OpenAlex API**: Fuente alternativa de literatura científica
- **Deduplicación inteligente**: Elimina papers duplicados entre APIs
- **Ranking por relevancia**: Ordena por citas + año de publicación

### 🤖 IA con Grounded Prompting
- **Modelo**: Claude 3.5 Haiku (rápido y preciso) vía OpenRouter
- **Temperature**: 0.3 (respuestas deterministas)
- **Sistema prompt estricto**: 
  - SOLO usa estudios proporcionados
  - NUNCA inventa referencias
  - Cita con formato (Autor, Año)
  - Si no hay evidencia, lo dice claramente

### 💬 Chat Persistente
- Historial de conversaciones guardado en base de datos
- Cada sesión tiene UUID único
- Contexto conversacional (últimos 10 mensajes)
- Título automático desde primera pregunta

### 📚 Presentación de Papers
- Tarjetas con título, autores, año
- Abstract resumido
- Enlace directo al paper
- Contador de citas
- Fuente (Semantic Scholar / OpenAlex)

## 🏗️ Arquitectura

### Backend (Django)

#### Modelos
```python
ChatSession
- id: UUID (primary key)
- user: ForeignKey(User)
- title: CharField (auto from first message)
- created_at, updated_at: DateTimeField

ChatMessage
- chat: ForeignKey(ChatSession)
- sender: CharField (choices: 'user', 'assistant')
- content: TextField
- papers: JSONField (cited papers metadata)
- timestamp: DateTimeField
```

#### Servicios

**ResearchSearchService** (`core/services/research_search.py`)
- `search_semantic_scholar(query, limit)`: Busca en Semantic Scholar
- `search_openalex(query, per_page)`: Busca en OpenAlex
- `search_combined(query, limit)`: Combina ambas APIs, deduplica, rankea
- `_deduplicate_papers(papers)`: Elimina duplicados por similitud de título
- `_normalize_*()`: Normaliza respuestas de diferentes APIs

**EducationalResearchAgent** (`core/services/educational_research_agent.py`)
- `process_question(question, chat_history)`: Flujo completo
  1. Busca papers relevantes
  2. Construye contexto científico
  3. Llama a LLM con grounded prompt
  4. Retorna respuesta + papers citados
- `generate_response(question, papers, chat_history)`: Genera respuesta del LLM
- `_build_scientific_context(papers)`: Formatea papers para el prompt

#### Endpoints

```
GET    /api/ai/chat/                       # Lista sesiones del usuario
POST   /api/ai/chat/start_new/             # Crea chat y envía primer mensaje
GET    /api/ai/chat/{id}/                  # Obtiene chat con todos los mensajes
POST   /api/ai/chat/{id}/send_message/    # Envía mensaje a chat existente
POST   /api/ai/test-search/                # Prueba búsqueda sin chat (debug)
```

**Ejemplo request a `start_new`:**
```json
POST /api/ai/chat/start_new/
Authorization: Bearer {token}
{
  "message": "¿Qué dice la evidencia sobre aprendizaje cooperativo?"
}
```

**Ejemplo response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user": 1,
  "title": "¿Qué dice la evidencia sobre aprendizaje cooperativo?",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:05Z",
  "message_count": 2,
  "messages": [
    {
      "id": 1,
      "sender": "user",
      "content": "¿Qué dice la evidencia sobre aprendizaje cooperativo?",
      "papers": [],
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "sender": "assistant",
      "content": "Según la evidencia científica, el aprendizaje cooperativo...\n\n(Johnson & Johnson, 2009) encontraron que...",
      "papers": [
        {
          "title": "Cooperative Learning: Improving University Instruction...",
          "authors": ["David W. Johnson", "Roger T. Johnson"],
          "year": 2009,
          "abstract": "Cooperative learning is the instructional use of small groups...",
          "url": "https://www.semanticscholar.org/paper/abc123",
          "citations": 1543,
          "source": "Semantic Scholar"
        }
      ],
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ]
}
```

### Frontend (React)

#### Componentes

**AIExpertPage** (`pages/AIExpertPage.jsx`)
- Container principal del chat
- Gestión de estado: currentChat, messages, chatSessions, isLoading
- Scroll automático al final
- Sidebar de conversaciones
- Pantalla de bienvenida con ejemplos

**ChatBubble** (`components/chat/ChatBubble.jsx`)
- Renderiza mensaje individual
- Estilos diferentes para user/assistant
- Muestra timestamp
- Renderiza PaperCards para mensajes del assistant

**PaperCard** (`components/chat/PaperCard.jsx`)
- Tarjeta de paper científico
- Título, autores (máx 3 + "et al."), año
- Abstract (line-clamp-3)
- Contador de citas
- Badge de fuente (Semantic Scholar/OpenAlex)
- Enlace "Ver paper" con icono externo

**MessageInput** (`components/chat/MessageInput.jsx`)
- Textarea con auto-resize
- Submit con Enter (Shift+Enter para nueva línea)
- Disabled durante carga
- Placeholder con tip

**ChatSidebar** (`components/chat/ChatSidebar.jsx`)
- Lista de conversaciones
- Botón "Nueva Conversación"
- Muestra message_count y fecha
- Highlight en conversación activa
- Responsive con overlay móvil
- Footer con fuentes científicas

#### Routing
```jsx
<Route path="/teacher/ai-expert" element={<ProtectedRoute><AIExpertPage /></ProtectedRoute>} />
```

#### Sidebar Navigation
```jsx
{ 
  path: '/teacher/ai-expert', 
  icon: BrainCircuit, 
  label: 'Asistente IA', 
  highlight: true  // Badge "NUEVO" + gradiente azul-morado
}
```

## 🚀 Instalación y Configuración

### 1. Backend Setup

#### Variables de Entorno
Añade a `.env`:
```env
# OpenRouter (ya configurado)
OPENROUTER_API_KEY=tu_api_key_aqui

# Configuración del Chatbot
AI_MODEL=anthropic/claude-3-5-haiku
AI_MAX_TOKENS=2000
AI_TEMPERATURE=0.3

# Email para OpenAlex (opcional, mejora rate limit)
OPENALEX_EMAIL=tu_email@example.com
```

**Modelos disponibles en OpenRouter (gratuitos):**
- `anthropic/claude-3-5-haiku` (recomendado: rápido, preciso)
- `x-ai/grok-2-1212` (gratis, buena calidad)
- `cohere/command-r-plus` (gratis, multilingüe)
- `openai/gpt-4o-mini` (gratis, OpenAI)

#### Migraciones
```bash
cd backend_django
python manage.py makemigrations
python manage.py migrate
```

#### Verificar Instalación
```bash
# Test búsqueda de papers
curl -X POST http://localhost:8000/api/ai/test-search/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "cooperative learning"}'
```

### 2. Frontend Setup

Ya está integrado en el proyecto. Solo asegúrate de:
```bash
cd frontend
npm install  # Si no tienes lucide-react: npm install lucide-react
npm run dev
```

Navega a: `http://localhost:5173/teacher/ai-expert`

## 📖 Uso

### 1. Inicio de Sesión
Inicia sesión como profesor en EvalAI

### 2. Acceso al Chatbot
Desde el sidebar, haz clic en **"Asistente IA"** (icono cerebro con badge "NUEVO")

### 3. Primera Pregunta
Escribe una pregunta sobre educación. Ejemplos:
- "¿Qué dice la evidencia sobre el aprendizaje cooperativo?"
- "¿Cómo puedo mejorar la comprensión lectora en primaria?"
- "Estrategias para motivar estudiantes desmotivados según estudios"

### 4. Respuesta del Asistente
- 🔍 Aparece "Buscando artículos científicos..."
- 📚 Se muestran los papers encontrados
- 💬 Respuesta basada SOLO en esos papers
- 🔗 Puedes hacer clic en "Ver paper" para leer el estudio completo

### 5. Conversación Continua
- Haz preguntas de seguimiento
- El contexto se mantiene (últimos 10 mensajes)
- Puedes iniciar nueva conversación con botón "+ Nueva Conversación"

### 6. Historial
- Tus conversaciones se guardan automáticamente
- Accede desde el sidebar izquierdo
- Cada conversación muestra número de mensajes y fecha

## 🔍 Cómo Funciona (Flow Técnico)

### Flujo de Mensaje

```
Usuario escribe pregunta
        ↓
Frontend envía POST /api/ai/chat/{id}/send_message/
        ↓
Backend guarda mensaje del usuario
        ↓
ChatSessionViewSet.send_message() llama a:
  educational_research_agent.process_question()
        ↓
Agent busca papers:
  research_search_service.search_combined()
        ↓
ResearchSearchService:
  1. search_semantic_scholar(query)
  2. search_openalex(query)
  3. _deduplicate_papers()
  4. Sort by relevance
        ↓
Agent construye contexto científico:
  _build_scientific_context(papers)
        ↓
Agent llama a OpenRouter:
  openrouter_client.generate(
    model=AI_MODEL,
    messages=[system_prompt, context, history, question],
    temperature=0.3
  )
        ↓
OpenRouter retorna respuesta citando papers
        ↓
Backend guarda respuesta + papers en ChatMessage
        ↓
Frontend recibe:
  - user_message (confirmación)
  - assistant_message (respuesta + papers)
        ↓
ChatBubble renderiza respuesta
PaperCard muestra cada paper citado
```

### Deduplicación de Papers

```python
def _deduplicate_papers(self, papers):
    # Usa SequenceMatcher para comparar títulos
    # Threshold: 0.85 (85% similitud)
    # Mantiene paper con más citas
```

### Relevance Ranking

```python
score = (citations * 0.7) + (normalized_year * 0.3)
# 70% peso en citas
# 30% peso en año (papers recientes suben)
```

## 🛡️ Prevención de Alucinaciones

### 1. Sistema Prompt Restrictivo
```
REGLAS ESTRICTAS:
1. SOLO usa información de estudios proporcionados
2. NUNCA inventes referencias
3. Si no hay evidencia, dilo claramente
4. Siempre cita: (Autor, Año)
```

### 2. Contexto Científico Explícito
```
CONTEXTO CIENTÍFICO:

Estudio 1:
Título: ...
Autores: ...
Año: ...
Abstract: ...

[Solo responde basándote en estos estudios]
```

### 3. Temperature Baja (0.3)
Reduce creatividad, aumenta adherencia al contexto

### 4. Papers en JSONField
Guardamos los papers citados para verificación posterior

## 📊 Admin Interface

Accede a `/admin` para:
- Ver todas las sesiones de chat (ChatSessionAdmin)
- Leer mensajes completos (ChatMessageAdmin)
- Filtrar por usuario, fecha
- Verificar papers citados (JSON preview)
- Monitorear uso del sistema

**Campos mostrados:**
- ChatSession: ID, usuario, título, # mensajes, created_at, updated_at
- ChatMessage: Sender, timestamp, content preview (100 chars), chat ID

## 🔧 Troubleshooting

### Error: "No se encontraron estudios relevantes"
- **Causa**: APIs no retornaron resultados para esa query
- **Solución**: Reformula la pregunta con términos más específicos

### Error: "Error al buscar en Semantic Scholar/OpenAlex"
- **Causa**: Rate limit o timeout de API
- **Solución**: Espera 1 minuto y reintenta. Si persiste, verifica logs.

### Papers duplicados en respuesta
- **Causa**: Fallo en deduplicación (títulos muy diferentes pero mismo paper)
- **Solución**: Ajusta threshold en `_deduplicate_papers()` (línea 135)

### Respuesta inventada (sin citar papers)
- **Causa**: LLM alucina a pesar de grounded prompt
- **Solución**: 
  1. Verifica que `papers` se envía en contexto
  2. Revisa logs para ver prompt completo
  3. Aumenta peso del system prompt
  4. Cambia modelo (prueba claude-3-5-sonnet)

### Frontend no carga conversaciones
- **Causa**: Error de autenticación o CORS
- **Solución**: 
  ```bash
  # Verifica token en localStorage
  localStorage.getItem('token')
  
  # Verifica CORS en settings.py
  CORS_ALLOWED_ORIGINS
  ```

## 📈 Mejoras Futuras

### Fase 1 (Actual) ✅
- [x] Búsqueda en Semantic Scholar + OpenAlex
- [x] Grounded prompting con Claude
- [x] Chat persistente
- [x] UI con paper cards
- [x] Admin interface

### Fase 2 (Próximas)
- [ ] **Filtros avanzados**: Año, # citas mínimas, tipo de estudio
- [ ] **Multiidioma**: Traducción automática de abstracts
- [ ] **Export**: Descargar conversación como PDF con referencias
- [ ] **Favoritos**: Guardar papers útiles en biblioteca personal
- [ ] **Compartir**: Share chat URL con otros profes

### Fase 3 (Futuras)
- [ ] **RAG avanzado**: Vectorización de papers para búsqueda semántica
- [ ] **Análisis de tendencias**: "¿Qué se ha investigado más en 2024?"
- [ ] **Alertas**: Notificar cuando salgan papers sobre tema seguido
- [ ] **Resúmenes automáticos**: TL;DR de papers largos
- [ ] **Integración con curriculum**: "Papers relevantes para esta unidad"

## 🤝 Contribución

Si encuentras bugs o tienes ideas:
1. Abre issue en GitHub
2. Describe el problema/mejora
3. Incluye logs relevantes
4. Si es fix, envía PR

## 📝 Licencia

Este módulo es parte de EvalAI, sujeto a su licencia principal.

---

**Desarrollado con ❤️ para maestros que quieren enseñar basándose en evidencia real**
