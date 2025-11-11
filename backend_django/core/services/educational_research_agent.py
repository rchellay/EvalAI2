"""
Agente IA experto en investigación educativa
Utiliza OpenRouter para LLM y búsqueda científica real para fundamentar respuestas
"""
import json
import logging
from typing import Dict, List, Optional
from django.conf import settings
from .research_search import research_search_service
from .openrouter_service import openrouter_client

logger = logging.getLogger(__name__)


class EducationalResearchAgent:
    """Agente IA que responde preguntas basadas en evidencia científica"""
    
    def __init__(self):
        self.model = getattr(settings, 'AI_MODEL', 'anthropic/claude-3-5-haiku')
        self.max_tokens = getattr(settings, 'AI_MAX_TOKENS', 2000)
        self.temperature = getattr(settings, 'AI_TEMPERATURE', 0.7)  # Más flexible y conversacional
        
        # Definir funciones disponibles para function calling
        self.available_functions = [
            {
                "name": "create_student",
                "description": "Crea un nuevo alumno en la aplicación. Usa esta función cuando el usuario pida crear, añadir o registrar alumnos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre completo del alumno"
                        },
                        "group_id": {
                            "type": "integer",
                            "description": "ID del grupo al que pertenece el alumno"
                        }
                    },
                    "required": ["name", "group_id"]
                }
            },
            {
                "name": "create_group",
                "description": "Crea un nuevo grupo con una lista de alumnos. Usa esta función cuando el usuario pida crear un grupo con alumnos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "description": "Nombre del grupo (ej: '6º A', 'Matemáticas Avanzadas')"
                        },
                        "student_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de nombres completos de los alumnos"
                        }
                    },
                    "required": ["group_name", "student_names"]
                }
            },
            {
                "name": "create_subject",
                "description": "Crea una nueva asignatura en la aplicación. Usa esta función cuando el usuario pida crear una materia o asignatura.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject_name": {
                            "type": "string",
                            "description": "Nombre de la asignatura (ej: 'Matemáticas', 'Lengua Catalana')"
                        },
                        "days": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Días de la semana (ej: ['L', 'X', 'V']). L=Lunes, M=Martes, X=Miércoles, J=Jueves, V=Viernes"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Hora de inicio en formato HH:MM (ej: '09:00')"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "Hora de fin en formato HH:MM (ej: '10:00')"
                        },
                        "color": {
                            "type": "string",
                            "description": "Color en hexadecimal (ej: '#3B82F6')"
                        }
                    },
                    "required": ["subject_name"]
                }
            }
        ]
        
        # Sistema prompt ComeniusAI V2 - Function calling PRIMERO
        self.system_prompt = """Eres ComeniusAI, un asistente educativo especializado.

════════════════════════════════════════════
🔧 FUNCIONES DISPONIBLES (USA ESTAS PRIMERO)
════════════════════════════════════════════

Tienes acceso a estas funciones para modificar la aplicación:

✅ create_student(name, group_id) - Crear un alumno
✅ create_group(group_name, student_names[]) - Crear grupo con alumnos
✅ create_subject(subject_name, days[], start_time, end_time, color) - Crear asignatura

🚨 CUÁNDO USAR FUNCIONES:

Detecta estas palabras clave del usuario:
• "crear", "crea", "añadir", "añade", "registrar", "registra"
• "nuevo alumno", "nueva asignatura", "nuevo grupo"
• "¿puedes crear...?"

Ejemplos donde DEBES usar funciones:
- "Crea un alumno llamado Pedro" → create_student
- "Añade estos alumnos al grupo..." → create_group
- "Registra la asignatura Matemáticas" → create_subject
- "Puedes crear alumnos?" → Responde "Sí" y espera instrucciones
- "Crea un grupo con estos alumnos: ..." → create_group

🚨 SI FALTA INFORMACIÓN:
Pregunta DIRECTAMENTE lo que necesitas, SIN teoría pedagógica:
- "¿A qué grupo pertenece?"
- "¿Qué días tiene la asignatura?"
- NO DIGAS: "Basándome en Hattie (2009)... necesito el grupo"

════════════════════════════════════════════
📚 MODO CONSULTA EDUCATIVA
════════════════════════════════════════════

Si NO es una acción de la app, entonces:
• Responde con evidencia científica (Hattie, Dweck, Vygotsky, etc.)
• Ofrece estrategias prácticas
• Cita autores reales y conocidos
• NUNCA digas "no encontré estudios"

════════════════════════════════════════════
📝 CREACIÓN DE RECURSOS EDUCATIVOS
════════════════════════════════════════════

Puedes generar cuando el usuario lo pida:
✅ Rúbricas, actividades, secuencias didácticas, etc.
✅ Si falta info (nivel, materia), PREGUNTA antes

════════════════════════════════════════════
🎯 DECISIÓN RÁPIDA
════════════════════════════════════════════

1. ¿Pide crear/añadir algo en la app? → USA FUNCIÓN
2. ¿Pregunta educativa? → RESPONDE CON EVIDENCIA
3. ¿Saludo? → RESPONDE AMABLEMENTE
4. ¿Falta info? → PREGUNTA DIRECTAMENTE

MENSAJE DE BIENVENIDA:
"¡Hola! Soy ComeniusAI, tu asistente educativo basado en evidencia.
¿Tienes dudas sobre metodologías, evaluación o gestión de aula?
También puedo ayudarte a crear grupos, alumnos y asignaturas en la app.
¿En qué puedo ayudarte?"
════════════════════════════════════════════

Usuario: "¿Cómo podría trabajar el juego cooperativo con un grupo muy competitivo?"

Respuesta correcta:
"Para grupos muy competitivos, los modelos cooperativos de Johnson & Johnson (1989, 1994) muestran que es clave introducir estructuras donde:

1. Los objetivos sean compartidos, no individuales
2. Roles rotativos (portavoz, coordinador, temporizador)
3. Interdependencia positiva: solo ganan si todos cumplen su parte
4. Responsabilidad individual + grupal (Slavin, 1995)
5. Recompensas cooperativas, no premios individuales

**Ejemplo práctico:**
Propon una misión donde cada alumno tenga una pieza de información imprescindible para resolver el desafío. Si alguien falla, el equipo no puede completarlo."

---

Usuario: "¿Cómo gestiono a una alumna que brota mucho?"

Respuesta correcta:
"Los estudios sobre autorregulación emocional en el aula (Gross, 2015; Zimmerman, 2002) indican que funciona:

1. Espacios de pausa para bajar activación
2. Anticipación de detonantes (registro ABC)
3. Lenguaje co-regulador corto y calmado
4. Opciones guiadas ('¿prefieres seguir trabajando o tomar 2 minutos?')
5. Refuerzo positivo inmediato cuando se regula

**Mini-guion:**
'Veo que te estás activando. Vamos a tomar dos minutos para respirar y luego lo retomamos juntas.'"

════════════════════════════════════════════
RECUERDA: Tu propósito es ser ÚTIL, PRÁCTICO y FUNDAMENTADO. Nunca digas que no puedes ayudar."""
    
    def generate_response(
        self,
        user_question: str,
        papers: List[Dict],
        chat_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Genera respuesta basada en papers científicos
        
        Args:
            user_question: Pregunta del usuario
            papers: Lista de papers encontrados
            chat_history: Historial previo de conversación
            
        Returns:
            Dict con 'response' (texto) y 'papers_used' (lista)
        """
        try:
            # Construir contexto científico
            scientific_context = self._build_scientific_context(papers)
            
            # Construir prompt completo
            messages = []
            
            # System message
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Agregar historial si existe (últimos 5 mensajes)
            if chat_history and isinstance(chat_history, list) and len(chat_history) > 0:
                for msg in chat_history[-5:]:
                    if isinstance(msg, dict) and 'sender' in msg and 'content' in msg:
                        messages.append({
                            "role": msg.get("sender", "user"),
                            "content": msg.get("content", "")
                        })
            
            # Mensaje del usuario con contexto científico (si hay)
            if papers and len(papers) > 0:
                user_prompt = f"""CONTEXTO CIENTÍFICO DISPONIBLE:

{scientific_context}

---

PREGUNTA DEL USUARIO:
{user_question}

Responde usando tu conocimiento pedagógico general y los estudios anteriores como referencia adicional cuando sean relevantes."""
            else:
                user_prompt = f"""PREGUNTA DEL USUARIO:
{user_question}

Responde usando tu conocimiento pedagógico basado en autores reconocidos y consenso científico general (Hattie, Rosenshine, Johnson & Johnson, Vygotsky, Slavin, Zimmerman, Dweck, etc.)."""
            
            messages.append({
                "role": "user",
                "content": user_prompt
            })
            
            # Llamar a OpenRouter CON TOOLS (function calling)
            response = openrouter_client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=self.available_functions  # Enviar funciones disponibles
            )
            
            # Extraer respuesta
            if 'choices' in response and len(response['choices']) > 0:
                message = response['choices'][0]['message']
                
                # Verificar si el modelo quiere llamar a una función
                if message.get('tool_calls'):
                    # El modelo quiere llamar a una función
                    tool_call = message['tool_calls'][0]
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    logger.info(f"Function call detected: {function_name} with args {function_args}")
                    
                    return {
                        'response': None,  # No hay respuesta de texto
                        'function_call': {
                            'name': function_name,
                            'arguments': function_args
                        },
                        'papers_used': papers,
                        'model_used': self.model,
                        'success': True
                    }
                
                # Respuesta de texto normal
                assistant_response = message.get('content', '')
                
                return {
                    'response': assistant_response,
                    'papers_used': papers,
                    'model_used': self.model,
                    'success': True
                }
            else:
                logger.error(f"Unexpected OpenRouter response format: {response}")
                return {
                    'response': 'Lo siento, hubo un error al generar la respuesta.',
                    'papers_used': [],
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return {
                'response': f'Lo siento, ocurrió un error: {str(e)}',
                'papers_used': [],
                'success': False
            }
    
    def process_question(
        self,
        question: str,
        chat_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Proceso completo: buscar papers + generar respuesta
        
        Args:
            question: Pregunta del usuario
            chat_history: Historial de chat
            
        Returns:
            Dict con response, papers, y metadatos
        """
        try:
            # Detectar si es un saludo simple o pregunta no educativa
            question_lower = question.lower().strip()
            simple_greetings = ['hola', 'hi', 'hello', 'buenos días', 'buenas tardes', 'buenas noches', 'hey']
            
            is_simple_greeting = question_lower in simple_greetings or len(question_lower.split()) <= 2
            
            # Si es saludo simple, responder directamente sin buscar papers
            if is_simple_greeting:
                logger.info(f"Simple greeting detected: {question}")
                return {
                    'response': '¡Hola! ¿Qué tal? 😊\n\nEstoy aquí para ayudarte con cualquier duda sobre educación, metodologías, evaluación, motivación o gestión de aula basada en evidencia científica.\n\n¿En qué puedo ayudarte hoy?',
                    'papers_used': [],
                    'success': True
                }
            
            # 1. Buscar papers relevantes (pero no es obligatorio encontrarlos)
            logger.info(f"Searching papers for: {question}")
            papers = research_search_service.search_combined(question, limit=5)
            
            # Validar que papers sea una lista
            if papers is None:
                papers = []
            
            logger.info(f"Found {len(papers)} papers")
            
            # 2. Generar respuesta con IA (incluso si no hay papers)
            # El prompt ya maneja el caso de pocos o ningún paper
            result = self.generate_response(question, papers, chat_history)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return {
                'response': f'Error al procesar la pregunta: {str(e)}',
                'papers_used': [],
                'success': False
            }
    
    def _build_scientific_context(self, papers: List[Dict]) -> str:
        """Construye el contexto científico a partir de los papers"""
        if not papers:
            return "No hay estudios disponibles."
        
        context_parts = []
        
        for i, paper in enumerate(papers, 1):
            authors = ", ".join(paper.get('authors', [])[:3])
            if len(paper.get('authors', [])) > 3:
                authors += " et al."
            
            year = paper.get('year', 'N/A')
            title = paper.get('title', 'Sin título')
            abstract = paper.get('abstract', 'Sin resumen')
            citations = paper.get('citations', 0)
            source = paper.get('source', 'Unknown')
            
            # Limitar abstract a 500 caracteres para no exceder límites
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            paper_context = f"""ESTUDIO {i}:
Autores: {authors}
Año: {year}
Título: {title}
Fuente: {source}
Citaciones: {citations}
Resumen: {abstract}
"""
            context_parts.append(paper_context)
        
        return "\n\n".join(context_parts)


# Instancia global del agente
educational_research_agent = EducationalResearchAgent()
