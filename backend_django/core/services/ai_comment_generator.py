"""
Servicio para generar comentarios educativos formales usando IA.
Genera comentarios personalizados para informes trimestrales basados en datos reales del estudiante.
"""

import os
import requests
from typing import Dict, List, Any

class AICommentGeneratorService:
    """
    Genera comentarios educativos formales para informes trimestrales.
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat"
        
    def get_system_prompt(self) -> str:
        """
        Prompt del sistema para generar comentarios educativos formales.
        """
        return """Eres un generador de comentarios educativos formales destinados a informes de evaluación trimestral para familias. 
Tu tarea es crear mensajes profesionales, claros, respetuosos y constructivos basados en los datos proporcionados. 

--- DATOS IMPORTANTES ---
- Usa SOLO la información del trimestre seleccionado por el usuario.
- No inventes datos.
- Identifica FORTALEZAS reales basadas en los registros.
- Identifica ÁREAS DE MEJORA posibles siempre desde una perspectiva pedagógica positiva.
- Tono: formal, amable, profesional, orientado a la mejora.
- Evita juicios personales, etiquetas ("vago", "conflictivo", "distraído"...).
- Incluye sugerencias concretas para el próximo trimestre.
- Si hay autoevaluación del alumno, intégrala en la reflexión.
- Si hay datos de asistencia, menciona la importancia de la continuidad.
- Si no hay datos suficientes, crea un comentario breve indicando que el trimestre tiene pocos registros.

--- FORMATOS ---
1. Comentario general del alumno (3–5 líneas)
2. Comentario por asignatura (2–4 líneas por cada asignatura con datos)
3. Comentario sobre la autoevaluación del alumno (si existe)
4. Observaciones sobre asistencia (si procede)

--- ENTREGA ---
Devuelve siempre el texto en formato listo para poner en un informe.
Usa un lenguaje claro, sin tecnicismos excesivos.
Sé específico pero no repitas información redundante."""

    def generar_comentarios_estudiante(
        self, 
        estudiante_data: Dict[str, Any],
        trimestre: str
    ) -> Dict[str, Any]:
        """
        Genera comentarios completos para un estudiante basados en sus datos del trimestre.
        
        Args:
            estudiante_data: Datos completos del estudiante (evaluaciones, asistencia, autoevaluación)
            trimestre: Trimestre (T1, T2, T3)
            
        Returns:
            Dict con comentarios generados
        """
        
        # Construir el prompt con los datos del estudiante
        user_prompt = self._construir_prompt_estudiante(estudiante_data, trimestre)
        
        # Llamar a la API de OpenRouter
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "EvalAI - Informes Inteligentes"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.get_system_prompt()},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parsear la respuesta
            comentarios_text = result['choices'][0]['message']['content']
            comentarios = self._parsear_comentarios(comentarios_text, estudiante_data)
            
            return comentarios
            
        except Exception as e:
            print(f"Error generando comentarios con IA: {e}")
            return self._generar_comentarios_fallback(estudiante_data)
    
    def _construir_prompt_estudiante(
        self, 
        estudiante_data: Dict[str, Any],
        trimestre: str
    ) -> str:
        """
        Construye el prompt con los datos específicos del estudiante.
        """
        
        nombre = estudiante_data.get('nombre', 'Estudiante')
        grupo = estudiante_data.get('grupo', '')
        
        prompt = f"""Genera comentarios educativos formales para el informe trimestral de {nombre} ({grupo}) - {trimestre}.

--- DATOS DEL ESTUDIANTE ---

**Rendimiento Académico:**
"""
        
        # Agregar evaluaciones por asignatura
        evaluaciones = estudiante_data.get('evaluaciones_por_asignatura', [])
        if evaluaciones:
            for eval in evaluaciones:
                prompt += f"\n- {eval['nombre']}: {eval.get('nota_trimestral', 'N/A')}"
                if eval.get('tendencia'):
                    tendencia_text = "mejora" if eval['tendencia'] > 0 else "descenso" if eval['tendencia'] < 0 else "estable"
                    prompt += f" (tendencia: {tendencia_text})"
        else:
            prompt += "\n- No hay evaluaciones registradas para este trimestre."
        
        # Agregar autoevaluación
        autoevaluacion = estudiante_data.get('autoevaluacion')
        if autoevaluacion:
            prompt += f"\n\n**Autoevaluación del Alumno:**\n{autoevaluacion.get('texto', 'No disponible')}"
            
            competencias = autoevaluacion.get('competencias', [])
            if competencias:
                prompt += "\n\nCompetencias autoevaluadas:"
                for comp in competencias:
                    prompt += f"\n- {comp['nombre']}: {comp['valor']}/10"
        
        # Agregar asistencia
        total_ausencias = estudiante_data.get('total_horas_ausencia', 0)
        if total_ausencias > 0:
            prompt += f"\n\n**Asistencia:**\n- Total de horas de ausencia: {total_ausencias}h"
            if total_ausencias > 20:
                prompt += " (absentismo significativo)"
            elif total_ausencias > 10:
                prompt += " (ausencias moderadas)"
        else:
            prompt += "\n\n**Asistencia:**\n- Asistencia regular sin ausencias significativas"
        
        # Agregar registros de aula si existen
        registros = estudiante_data.get('registros_aula', [])
        if registros:
            prompt += "\n\n**Observaciones del Profesor:**"
            for registro in registros[:5]:  # Máximo 5 registros
                prompt += f"\n- {registro}"
        
        prompt += "\n\n--- INSTRUCCIONES ---\n"
        prompt += "Genera los siguientes comentarios en formato estructurado:\n"
        prompt += "1. COMENTARIO_GENERAL: (3-5 líneas sobre el rendimiento general del trimestre)\n"
        prompt += "2. COMENTARIOS_ASIGNATURAS: (Un comentario de 2-4 líneas para cada asignatura con datos)\n"
        
        if autoevaluacion:
            prompt += "3. COMENTARIO_AUTOEVALUACION: (2-3 líneas integrando la reflexión del alumno)\n"
        
        if total_ausencias > 10:
            prompt += "4. COMENTARIO_ASISTENCIA: (2-3 líneas sobre la importancia de la asistencia regular)\n"
        
        return prompt
    
    def _parsear_comentarios(
        self, 
        comentarios_text: str,
        estudiante_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parsea el texto generado por la IA en un diccionario estructurado.
        """
        
        comentarios = {
            'comentario_general': '',
            'comentarios_asignaturas': {},
            'comentario_autoevaluacion': '',
            'comentario_asistencia': ''
        }
        
        # Dividir el texto en secciones
        lines = comentarios_text.split('\n')
        current_section = None
        current_subject = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Detectar secciones
            if 'COMENTARIO_GENERAL' in line.upper() or line.startswith('1.'):
                current_section = 'general'
                current_subject = None
                continue
            elif 'COMENTARIOS_ASIGNATURAS' in line.upper() or 'COMENTARIO POR ASIGNATURA' in line.upper() or line.startswith('2.'):
                current_section = 'asignaturas'
                current_subject = None
                continue
            elif 'COMENTARIO_AUTOEVALUACION' in line.upper() or 'AUTOEVALUACIÓN' in line.upper() or line.startswith('3.'):
                current_section = 'autoevaluacion'
                current_subject = None
                continue
            elif 'COMENTARIO_ASISTENCIA' in line.upper() or 'ASISTENCIA' in line.upper() or line.startswith('4.'):
                current_section = 'asistencia'
                current_subject = None
                continue
            
            # Detectar nombre de asignatura (suele estar en negrita o seguido de :)
            evaluaciones = estudiante_data.get('evaluaciones_por_asignatura', [])
            for eval in evaluaciones:
                asignatura_nombre = eval['nombre']
                if asignatura_nombre in line and ':' in line:
                    current_subject = asignatura_nombre
                    # Extraer el comentario después de los :
                    comentario_asignatura = line.split(':', 1)[1].strip()
                    if comentario_asignatura:
                        comentarios['comentarios_asignaturas'][asignatura_nombre] = comentario_asignatura
                    continue
            
            # Agregar contenido a la sección actual
            if current_section == 'general':
                if line and not line.startswith('-'):
                    comentarios['comentario_general'] += line + ' '
            elif current_section == 'asignaturas' and current_subject:
                comentarios['comentarios_asignaturas'][current_subject] += line + ' '
            elif current_section == 'asignaturas' and not current_subject:
                # Buscar si la línea menciona alguna asignatura
                for eval in evaluaciones:
                    if eval['nombre'].lower() in line.lower():
                        comentarios['comentarios_asignaturas'][eval['nombre']] = line
                        break
            elif current_section == 'autoevaluacion':
                if line and not line.startswith('-'):
                    comentarios['comentario_autoevaluacion'] += line + ' '
            elif current_section == 'asistencia':
                if line and not line.startswith('-'):
                    comentarios['comentario_asistencia'] += line + ' '
        
        # Limpiar espacios extras
        comentarios['comentario_general'] = comentarios['comentario_general'].strip()
        comentarios['comentario_autoevaluacion'] = comentarios['comentario_autoevaluacion'].strip()
        comentarios['comentario_asistencia'] = comentarios['comentario_asistencia'].strip()
        
        for key in comentarios['comentarios_asignaturas']:
            comentarios['comentarios_asignaturas'][key] = comentarios['comentarios_asignaturas'][key].strip()
        
        return comentarios
    
    def _generar_comentarios_fallback(
        self, 
        estudiante_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera comentarios básicos si falla la llamada a la IA.
        """
        
        nombre = estudiante_data.get('nombre', 'Estudiante')
        
        return {
            'comentario_general': f"Durante este trimestre, {nombre} ha participado en las actividades del grupo. Se recomienda revisar las evaluaciones específicas por asignatura para un análisis más detallado.",
            'comentarios_asignaturas': {
                eval['nombre']: f"Nota del trimestre: {eval.get('nota_trimestral', 'N/A')}. Comentarios adicionales pendientes."
                for eval in estudiante_data.get('evaluaciones_por_asignatura', [])
            },
            'comentario_autoevaluacion': '',
            'comentario_asistencia': ''
        }


# Instancia global del servicio
ai_comment_service = AICommentGeneratorService()
