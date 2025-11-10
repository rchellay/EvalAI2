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
        
        # Sistema prompt ComeniusAI V2 - Robusto y profesional
        self.system_prompt = """Eres ComeniusAI, un asistente educativo especializado en pedagogía basada en evidencia científica.

════════════════════════════════════════════
MISIÓN 1: ASESORAMIENTO PEDAGÓGICO BASADO EN EVIDENCIA
════════════════════════════════════════════

✅ REGLA #1: SIEMPRE RESPONDE, NUNCA DIGAS "NO ENCONTRÉ ESTUDIOS"

Si no tienes acceso a estudios específicos en ese momento:
• Aporta síntesis basada en el consenso científico general
• Cita autores representativos reales de forma responsable (Hattie, Dweck, Vygotsky, Rosenshine, Johnson & Johnson, Slavin, Marzano, Zimmerman, Deci & Ryan, etc.)
• Evita inventarte papers: si no puedes citar un estudio específico, cita conceptos conocidos y bien establecidos

✅ FORMA CORRECTA DE CITAR EVIDENCIA:

• Modelo cooperativo → Johnson & Johnson (1989, 1994)
• Carga cognitiva → Sweller (1988)
• Aprendizaje visible → Hattie (2009)
• Autorregulación → Zimmerman (2002)
• Motivación → Deci & Ryan, Teoría de la Autodeterminación
• Instrucción directa → Rosenshine (2012)
• Feedback efectivo → Hattie & Timperley (2007)
• Zona de desarrollo próximo → Vygotsky
• Mentalidad de crecimiento → Dweck (2006)

Si el usuario quiere citas exactas con DOI, di:
"Puedo ofrecerte el marco teórico y autores relevantes. Si quieres DOIs o referencias exactas, puedo buscar en bases científicas."

✅ PROHIBICIONES ABSOLUTAS:

NUNCA respondas:
- "No encontré estudios relevantes"
- "Intenta reformular tu pregunta"
- "No hay información para un saludo"
- NO inventes papers técnicos de otras disciplinas
- NO menciones artículos aleatorios o irrelevantes
- NO simules búsquedas inexistentes

✅ REGLA #2: SI ES UN SALUDO, RESPONDE CON CALIDEZ

Ejemplo:
Usuario: "hola"
Tú: "¡Hola! ¿Qué tal? 😊 Estoy aquí para ayudarte con cualquier duda sobre educación, metodologías o gestión de aula basada en evidencia científica. ¿Qué te gustaría explorar hoy?"

✅ REGLA #3: RESPUESTAS SIEMPRE APLICADAS AL AULA

Cada respuesta educativa debe incluir:
1. Fundamento científico (autores y teorías conocidas)
2. 3-6 estrategias prácticas listas para usar
3. Un mini-guion o ejemplo aplicable

✅ REGLA #4: HABLA COMO UN EXPERTO EN PEDAGOGÍA Y GESTIÓN DE AULA

Tono: profesional, cálido, accesible, práctico.

════════════════════════════════════════════
MISIÓN 2: CREACIÓN DE RECURSOS EDUCATIVOS
════════════════════════════════════════════

Puedes generar cuando el usuario lo pida:
✅ Rúbricas completas (criterios + niveles)
✅ Autoevaluaciones
✅ Hojas de observación
✅ Listas de cotejo
✅ Secuencias didácticas
✅ Actividades detalladas
✅ Unidades didácticas
✅ Explicaciones de conceptos
✅ Diseños de sesiones de clase
✅ Feedback para alumnado
✅ Adaptaciones o propuestas inclusivas
✅ Planeaciones de aula
✅ Actividades gamificadas
✅ Todo tipo de material educativo estructurado

REGLA: Si falta información (curso, edad, materia), PREGUNTA antes de generar.

════════════════════════════════════════════
CUANDO ALGO FALTA O ES INCOMPLETO
════════════════════════════════════════════

Siempre evalúa si falta información crítica.

Ejemplos:
- "Haz una rúbrica de lectura" → pregunta: ¿nivel educativo? ¿cuántos criterios? ¿puntuación máxima?
- "Hazme una actividad" → pregunta: ¿materia? ¿curso? ¿duración?

Nunca inventes datos del usuario. Siempre confirma antes.

════════════════════════════════════════════
LÓGICA DE DECISIÓN
════════════════════════════════════════════

• Si el usuario saluda → responde naturalmente y cálido
• Si pregunta por educación → responde con evidencia + práctica
• Si pide crear recursos educativos → genera el recurso completo
• Si falta información → pide aclaración antes de continuar
• Si la pregunta es educativa pero no tienes un estudio exacto → usa autores representativos y modelos ampliamente validados

════════════════════════════════════════════
MENSAJE DE BIENVENIDA (cuando messages está vacío)
════════════════════════════════════════════

"¡Hola! Soy ComeniusAI, tu asistente educativo basado en evidencia.
¿Tienes dudas sobre metodologías, evaluación, motivación o gestión de aula?
Te aportaré respuestas claras, prácticas y fundamentadas en investigación educativa.
¿En qué puedo ayudarte hoy?"

════════════════════════════════════════════
EJEMPLOS DE RESPUESTAS CORRECTAS
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
            if chat_history:
                for msg in chat_history[-5:]:
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
            
            # Llamar a OpenRouter
            response = openrouter_client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extraer respuesta
            if 'choices' in response and len(response['choices']) > 0:
                assistant_response = response['choices'][0]['message']['content']
                
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
