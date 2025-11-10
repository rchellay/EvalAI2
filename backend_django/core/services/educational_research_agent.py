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
        self.temperature = getattr(settings, 'AI_TEMPERATURE', 0.3)  # Más determinista para respuestas científicas
        
        # Sistema prompt enfocado en evidencia
        self.system_prompt = """Eres un asesor experto en educación basado EXCLUSIVAMENTE en evidencia científica.

REGLAS ESTRICTAS:
1. SOLO puedes usar información de los estudios proporcionados en el contexto
2. NUNCA inventes referencias o estudios que no estén en el contexto
3. Si algo no está respaldado por los estudios dados, di claramente "No hay evidencia suficiente en los estudios proporcionados"
4. Siempre cita los estudios específicos: (Autor, Año)
5. Proporciona recomendaciones prácticas cuando sea posible
6. Mantén un tono profesional pero accesible para docentes

FORMATO DE RESPUESTA:
- Resumen de la evidencia
- Hallazgos clave de cada estudio
- Recomendaciones prácticas basadas en evidencia
- Lista de estudios citados al final

Tu función principal es ayudar a maestros a tomar decisiones informadas basadas en investigación real."""
    
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
            
            # Mensaje del usuario con contexto científico
            user_prompt = f"""CONTEXTO CIENTÍFICO DISPONIBLE:

{scientific_context}

---

PREGUNTA DEL USUARIO:
{user_question}

Responde basándote ÚNICAMENTE en los estudios proporcionados arriba. Cita específicamente cada estudio que uses."""
            
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
            # 1. Buscar papers relevantes
            logger.info(f"Searching papers for: {question}")
            papers = research_search_service.search_combined(question, limit=5)
            
            if not papers:
                return {
                    'response': 'No encontré estudios relevantes para tu pregunta. Intenta reformularla o ser más específico.',
                    'papers_used': [],
                    'success': False
                }
            
            logger.info(f"Found {len(papers)} papers")
            
            # 2. Generar respuesta con IA
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
