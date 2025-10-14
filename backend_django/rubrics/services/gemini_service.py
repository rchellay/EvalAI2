"""
Servicio de integración con Google Gemini AI para generación de rúbricas educativas.
"""
import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional
import requests
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """Excepción personalizada para errores del servicio Gemini"""
    pass


class GeminiClient:
    """Cliente para interactuar con la API de Google Gemini"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.api_url = getattr(settings, 'GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models')
        self.model = getattr(settings, 'GEMINI_DEFAULT_MODEL', 'gemini-pro')
        self.timeout = getattr(settings, 'GEMINI_TIMEOUT', 30)
        self.max_tokens = getattr(settings, 'GEMINI_MAX_TOKENS', 2048)
        self.cache_ttl = getattr(settings, 'GEMINI_CACHE_TTL', 86400)  # 24 horas
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY no configurada")
    
    def _get_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Genera una clave de caché única basada en el prompt y parámetros"""
        cache_data = f"{prompt}:{json.dumps(params, sort_keys=True)}"
        return f"gemini_rubric_{hashlib.sha256(cache_data.encode()).hexdigest()}"
    
    def _validate_rubric_schema(self, data: Dict[str, Any]) -> bool:
        """Valida que la respuesta tenga la estructura correcta de rúbrica"""
        required_fields = ['title', 'description', 'criteria']
        
        if not all(field in data for field in required_fields):
            return False
        
        if not isinstance(data['criteria'], list) or len(data['criteria']) == 0:
            return False
        
        for criterion in data['criteria']:
            if not all(k in criterion for k in ['name', 'description', 'weight', 'levels']):
                return False
            if not isinstance(criterion['levels'], list) or len(criterion['levels']) == 0:
                return False
            for level in criterion['levels']:
                if not all(k in level for k in ['name', 'description', 'score']):
                    return False
        
        return True
    
    def generate_rubric(
        self,
        prompt: str,
        language: str = 'es',
        num_criteria: int = 4,
        num_levels: int = 4,
        max_score: int = 10
    ) -> Dict[str, Any]:
        """
        Genera una rúbrica educativa usando Gemini AI
        
        Args:
            prompt: Descripción de la rúbrica a generar
            language: Idioma de la rúbrica (es, en, ca, fr)
            num_criteria: Número de criterios (3-7)
            num_levels: Número de niveles por criterio (3-5)
            max_score: Puntuación máxima (4, 5, 10, 20)
        
        Returns:
            Dict con la estructura de la rúbrica generada
        """
        # Validar parámetros
        if not prompt or len(prompt.strip()) == 0:
            raise GeminiServiceError("El prompt no puede estar vacío")
        
        if num_criteria < 3 or num_criteria > 7:
            raise GeminiServiceError("El número de criterios debe estar entre 3 y 7")
        
        if num_levels < 3 or num_levels > 5:
            raise GeminiServiceError("El número de niveles debe estar entre 3 y 5")
        
        # Verificar caché
        params = {
            'language': language,
            'num_criteria': num_criteria,
            'num_levels': num_levels,
            'max_score': max_score
        }
        cache_key = self._get_cache_key(prompt, params)
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Rúbrica encontrada en caché: {cache_key}")
            cached_result['_from_cache'] = True
            return cached_result
        
        # Si no hay API key, devolver fallback
        if not self.api_key:
            logger.warning("No hay API key configurada, usando fallback")
            return self._get_fallback_rubric(prompt, num_criteria, num_levels, max_score)
        
        # Construir el prompt estructurado
        structured_prompt = self._build_prompt(prompt, language, num_criteria, num_levels, max_score)
        
        # Intentar generar con reintentos
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self._call_gemini_api(structured_prompt)
                
                # Validar estructura
                if self._validate_rubric_schema(result):
                    # Guardar en caché
                    cache.set(cache_key, result, self.cache_ttl)
                    result['_from_cache'] = False
                    logger.info(f"Rúbrica generada exitosamente y guardada en caché")
                    return result
                else:
                    logger.warning(f"Esquema inválido en intento {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"Error en intento {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
        
        # Si todos los intentos fallan, usar fallback
        logger.warning("Todos los intentos fallaron, usando fallback")
        return self._get_fallback_rubric(prompt, num_criteria, num_levels, max_score)
    
    def _build_prompt(
        self,
        user_prompt: str,
        language: str,
        num_criteria: int,
        num_levels: int,
        max_score: int
    ) -> str:
        """Construye el prompt estructurado para Gemini"""
        
        lang_names = {
            'es': 'español',
            'en': 'English',
            'ca': 'català',
            'fr': 'français'
        }
        
        lang_instructions = {
            'es': 'Responde en español.',
            'en': 'Respond in English.',
            'ca': 'Respon en català.',
            'fr': 'Répondez en français.'
        }
        
        prompt = f"""Eres un experto en diseño de rúbricas educativas. {lang_instructions.get(language, 'Responde en español.')}

Genera una rúbrica de evaluación basada en: {user_prompt}

REQUISITOS ESTRICTOS:
- Exactamente {num_criteria} criterios de evaluación
- Cada criterio debe tener exactamente {num_levels} niveles de desempeño
- La puntuación máxima por nivel debe ser {max_score} puntos
- Los pesos de los criterios deben sumar exactamente 100%
- Distribuye los pesos de forma equilibrada o según importancia

FORMATO DE RESPUESTA (JSON válido):
{{
    "title": "Título descriptivo de la rúbrica",
    "description": "Descripción del propósito y contexto de evaluación",
    "criteria": [
        {{
            "name": "Nombre del criterio",
            "description": "Descripción clara del criterio",
            "weight": 25.0,
            "levels": [
                {{
                    "name": "Excelente",
                    "description": "Descripción detallada del nivel excelente",
                    "score": {max_score},
                    "color": "#10b981"
                }},
                {{
                    "name": "Bueno",
                    "description": "Descripción detallada del nivel bueno",
                    "score": {max_score * 0.75},
                    "color": "#3b82f6"
                }}
                // ... más niveles según {num_levels}
            ]
        }}
        // ... más criterios según {num_criteria}
    ]
}}

COLORES SUGERIDOS (hex):
- Nivel más alto: #10b981 (verde)
- Nivel alto: #3b82f6 (azul)
- Nivel medio: #f59e0b (naranja)
- Nivel bajo: #ef4444 (rojo)

Responde ÚNICAMENTE con el JSON, sin texto adicional."""
        
        return prompt
    
    def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Realiza la llamada a la API de Gemini"""
        url = f"{self.api_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": self.max_tokens,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise GeminiServiceError(f"API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Extraer el texto de la respuesta
        try:
            text = data['candidates'][0]['content']['parts'][0]['text']
            # Limpiar el texto (quitar markdown si existe)
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # Parsear JSON
            result = json.loads(text)
            return result
            
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise GeminiServiceError(f"Error parsing API response: {str(e)}")
    
    def _get_fallback_rubric(
        self,
        prompt: str,
        num_criteria: int = 4,
        num_levels: int = 4,
        max_score: int = 10
    ) -> Dict[str, Any]:
        """Genera una rúbrica de respaldo cuando la API falla"""
        
        weight_per_criterion = round(100 / num_criteria, 1)
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
        level_names = ['Excelente', 'Bueno', 'Satisfactorio', 'Mejorable', 'Insuficiente']
        
        criteria = []
        for i in range(num_criteria):
            levels = []
            for j in range(num_levels):
                score = max_score * (1 - (j / num_levels))
                levels.append({
                    'name': level_names[j] if j < len(level_names) else f'Nivel {j+1}',
                    'description': f'Descripción del nivel {j+1}',
                    'score': round(score, 1),
                    'color': colors[j] if j < len(colors) else '#6b7280'
                })
            
            criteria.append({
                'name': f'Criterio {i+1}',
                'description': f'Descripción del criterio {i+1}',
                'weight': weight_per_criterion,
                'levels': levels
            })
        
        return {
            'title': f'Rúbrica: {prompt[:50]}',
            'description': 'Rúbrica generada automáticamente (modo fallback)',
            'criteria': criteria,
            '_is_fallback': True,
            '_from_cache': False
        }
