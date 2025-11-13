"""
Servicio OpenRouter para integración con múltiples modelos de IA open source
Reemplaza Gemini y DeepSeek con modelos gratuitos de alta calidad
"""
import requests
import json
import hashlib
import time
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class OpenRouterServiceError(Exception):
    """Excepción personalizada para errores del servicio OpenRouter"""
    pass

class OpenRouterClient:
    """Cliente para interactuar con múltiples modelos IA via OpenRouter"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        self.base_url = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.timeout = getattr(settings, 'OPENROUTER_TIMEOUT', 60)
        self.cache_ttl = getattr(settings, 'OPENROUTER_CACHE_TTL', 86400)  # 24 horas
        
        # Modelos disponibles (orden de fallback personalizado)
        self.rubric_model_candidates = [
            'meta-llama/llama-3.3-8b-instruct:free',
            'openai/gpt-oss-20b:free',
            'nvidia/nemotron-nano-9b-v2:free',
            'meta-llama/llama-4-maverick:free',
            'google/gemma-3n-e4b-it:free',
            'google/gemma-3-27b-it:free',
        ]
        self.models = {
            'qwen_rubrics': self.rubric_model_candidates[0],  # Usar el primero por defecto
            'deepseek_analysis': self.rubric_model_candidates[0],
            'glm_quick': self.rubric_model_candidates[0],
        }
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY no configurada")
    
    def _get_cache_key(self, prompt: str, model: str, params: Dict[str, Any]) -> str:
        """Genera una clave de caché única basada en el prompt, modelo y parámetros"""
        cache_data = f"{prompt}:{model}:{json.dumps(params, sort_keys=True)}"
        return f"openrouter_{hashlib.sha256(cache_data.encode()).hexdigest()}"
    
    def _call_openrouter_api(self, prompt: str, model: str, max_tokens: int = 2048) -> str:
        """
        Realiza llamada a OpenRouter API
        
        Args:
            prompt: Prompt a enviar
            model: Modelo a usar
            max_tokens: Máximo de tokens en la respuesta
            
        Returns:
            str: Respuesta del modelo
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://evalai.education',  # Para rankings en OpenRouter
            'X-Title': 'EvalAI Education Platform'
        }
        
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7,
            'top_p': 0.9
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Error en OpenRouter API: {response.status_code} - {response.text}")
                raise OpenRouterServiceError(f"Error en API: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise OpenRouterServiceError("Timeout en OpenRouter API")
        except requests.exceptions.RequestException as e:
            raise OpenRouterServiceError(f"Error de conexión: {str(e)}")
    
    def generate_rubric(
        self,
        prompt: str,
        language: str = 'es',
        num_criteria: int = 4,
        num_levels: int = 4,
        max_score: int = 10
    ) -> Dict[str, Any]:
        """
        Genera una rúbrica educativa usando Qwen3-235B (modelo principal)
        
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
            raise OpenRouterServiceError("El prompt no puede estar vacío")
        
        if num_criteria < 3 or num_criteria > 7:
            raise OpenRouterServiceError("El número de criterios debe estar entre 3 y 7")
        
        if num_levels < 3 or num_levels > 5:
            raise OpenRouterServiceError("El número de niveles debe estar entre 3 y 5")
        
        # Verificar caché
        params = {
            'language': language,
            'num_criteria': num_criteria,
            'num_levels': num_levels,
            'max_score': max_score
        }
        cache_key = self._get_cache_key(prompt, 'qwen_rubrics', params)
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Rúbrica encontrada en caché: {cache_key}")
            cached_result['_from_cache'] = True
            return cached_result
        
        # Si no hay API key, devolver fallback
        if not self.api_key:
            logger.warning("No hay API key configurada, usando fallback")
            return self._get_fallback_rubric(prompt, num_criteria, num_levels, max_score)
        
        # Intentar con cada modelo en orden hasta éxito
        structured_prompt = self._build_rubric_prompt(prompt, language, num_criteria, num_levels, max_score)
        max_retries = 3
        for model_name in self.rubric_model_candidates:
            logger.info(f"Intentando generar rúbrica con modelo: {model_name} para: {prompt[:50]}...")
            for attempt in range(max_retries):
                try:
                    result_text = self._call_openrouter_api(structured_prompt, model_name, 4096)
                    result = self._parse_rubric_response(result_text)
                    # Validar estructura
                    if self._validate_rubric_schema(result):
                        cache.set(cache_key, result, self.cache_ttl)
                        result['_from_cache'] = False
                        result['_model_used'] = model_name
                        logger.info(f"Rúbrica generada exitosamente con {model_name} y guardada en caché")
                        return result
                    else:
                        logger.warning(f"Esquema inválido en intento {attempt + 1} con {model_name}")
                except Exception as e:
                    logger.error(f"Error en intento {attempt + 1} con {model_name}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
            logger.warning(f"Modelo {model_name} falló, probando siguiente en la lista...")
        # Si todos los modelos fallan, usar fallback mejorado
        logger.warning("Todos los modelos fallaron, usando fallback mejorado")
        fallback_result = self._get_fallback_rubric(prompt, num_criteria, num_levels, max_score)
        fallback_result['_is_fallback'] = True
        fallback_result['_fallback_reason'] = "Ningún modelo IA disponible"
        return fallback_result
    
    def generate_analysis(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> str:
        """
        Genera análisis detallado usando DeepSeek R1T2 Chimera
        
        Args:
            prompt: Prompt para el análisis
            context: Contexto adicional
            
        Returns:
            str: Análisis generado
        """
        if not self.api_key:
            return "Análisis no disponible - API key no configurada"
        
        # Construir prompt completo
        full_prompt = prompt
        if context:
            full_prompt = f"Contexto: {context}\n\nAnálisis solicitado: {prompt}"
        
        try:
            logger.info(f"Generando análisis con DeepSeek R1T2 Chimera")
            result = self._call_openrouter_api(full_prompt, self.models['deepseek_analysis'], 4096)
            return result
        except Exception as e:
            logger.error(f"Error generando análisis: {str(e)}")
            return f"Error generando análisis: {str(e)}"
    
    def generate_quick_response(
        self,
        prompt: str,
        max_tokens: int = 512
    ) -> str:
        """
        Genera respuesta rápida usando GLM 4.5 Air
        
        Args:
            prompt: Prompt para la respuesta rápida
            max_tokens: Máximo de tokens
            
        Returns:
            str: Respuesta generada
        """
        if not self.api_key:
            return "Respuesta rápida no disponible - API key no configurada"
        
        try:
            logger.info(f"Generando respuesta rápida con GLM 4.5 Air")
            result = self._call_openrouter_api(prompt, self.models['glm_quick'], max_tokens)
            return result
        except Exception as e:
            logger.error(f"Error generando respuesta rápida: {str(e)}")
            return f"Error generando respuesta rápida: {str(e)}"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Genera respuesta de chat usando mensajes estructurados (para chatbot educativo)
        
        Args:
            messages: Lista de mensajes con formato [{"role": "system/user/assistant", "content": "..."}]
            model: Modelo a usar
            max_tokens: Máximo de tokens
            temperature: Temperatura para generación (0.0-1.0)
            tools: Lista de funciones disponibles para function calling (opcional)
            
        Returns:
            Dict: Respuesta completa de OpenRouter con estructura choices
        """
        if not self.api_key:
            raise OpenRouterServiceError("Chat completion no disponible - API key no configurada")
        
        try:
            logger.info(f"Chat completion con modelo {model}, {len(messages)} mensajes")
            if tools:
                logger.info(f"Tools disponibles: {[t['name'] for t in tools]}")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://evalai.education',
                'X-Title': 'EvalAI Education Platform'
            }
            
            data = {
                'model': model,
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'top_p': 0.9
            }
            
            # Añadir tools si están disponibles (function calling)
            if tools and len(tools) > 0:
                data['tools'] = [{"type": "function", "function": tool} for tool in tools]
                data['tool_choice'] = 'auto'
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error en OpenRouter API: {response.status_code} - {response.text}")
                raise OpenRouterServiceError(f"Error en API: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise OpenRouterServiceError("Timeout en OpenRouter API")
        except requests.exceptions.RequestException as e:
            raise OpenRouterServiceError(f"Error de conexión: {str(e)}")
    
    def _build_rubric_prompt(
        self,
        user_prompt: str,
        language: str,
        num_criteria: int,
        num_levels: int,
        max_score: int
    ) -> str:
        """Construye el prompt estructurado para generar rúbricas"""
        
        language_names = {
            'es': 'español',
            'en': 'inglés',
            'ca': 'catalán',
            'fr': 'francés'
        }
        
        lang_name = language_names.get(language, 'español')
        
        prompt = f"""Eres un experto en evaluación educativa. Genera una rúbrica detallada en {lang_name} basada en esta descripción:

DESCRIPCIÓN: {user_prompt}

REQUISITOS:
- {num_criteria} criterios de evaluación
- {num_levels} niveles de desempeño por criterio
- Puntuación máxima: {max_score}
- Idioma: {lang_name}

ESTRUCTURA REQUERIDA (responde SOLO con JSON válido):
{{
    "title": "Título de la rúbrica",
    "description": "Descripción breve",
    "criteria": [
        {{
            "name": "Nombre del criterio",
            "description": "Descripción del criterio",
            "weight": 25,
            "levels": [
                {{
                    "name": "Nivel 1",
                    "description": "Descripción del nivel",
                    "score": 0
                }},
                {{
                    "name": "Nivel 2", 
                    "description": "Descripción del nivel",
                    "score": {max_score // num_levels}
                }},
                {{
                    "name": "Nivel 3",
                    "description": "Descripción del nivel", 
                    "score": {(max_score // num_levels) * 2}
                }},
                {{
                    "name": "Nivel 4",
                    "description": "Descripción del nivel",
                    "score": {max_score}
                }}
            ]
        }}
    ]
}}

IMPORTANTE:
- Los pesos deben sumar 100%
- Los scores deben ser progresivos (0, {max_score // num_levels}, {(max_score // num_levels) * 2}, {max_score})
- Usa descripciones claras y específicas
- Adapta el contenido al nivel educativo apropiado
- Responde ÚNICAMENTE con el JSON, sin texto adicional"""
        
        return prompt
    
    def _parse_rubric_response(self, response_text: str) -> Dict[str, Any]:
        """Parsea la respuesta del modelo para extraer la rúbrica"""
        try:
            # Limpiar la respuesta
            cleaned_response = response_text.strip()
            
            # Buscar JSON en la respuesta
            if '```json' in cleaned_response:
                json_start = cleaned_response.find('```json') + 7
                json_end = cleaned_response.find('```', json_start)
                cleaned_response = cleaned_response[json_start:json_end].strip()
            elif '```' in cleaned_response:
                json_start = cleaned_response.find('```') + 3
                json_end = cleaned_response.find('```', json_start)
                cleaned_response = cleaned_response[json_start:json_end].strip()
            
            # Parsear JSON
            result = json.loads(cleaned_response)
            
            # Normalizar pesos
            total_weight = sum(criterion.get('weight', 0) for criterion in result.get('criteria', []))
            if total_weight > 0:
                for criterion in result.get('criteria', []):
                    criterion['weight'] = round((criterion.get('weight', 0) / total_weight) * 100, 1)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {str(e)}")
            raise OpenRouterServiceError("Error parseando respuesta del modelo")
        except Exception as e:
            logger.error(f"Error procesando respuesta: {str(e)}")
            raise OpenRouterServiceError("Error procesando respuesta del modelo")
    
    def _validate_rubric_schema(self, data: Dict[str, Any]) -> bool:
        """Valida que la estructura de la rúbrica sea correcta"""
        try:
            # Validar estructura básica
            if not isinstance(data, dict):
                return False
            
            if 'title' not in data or 'criteria' not in data:
                return False
            
            criteria = data.get('criteria', [])
            if not isinstance(criteria, list) or len(criteria) == 0:
                return False
            
            # Validar cada criterio
            for criterion in criteria:
                if not isinstance(criterion, dict):
                    return False
                
                if 'name' not in criterion or 'levels' not in criterion:
                    return False
                
                levels = criterion.get('levels', [])
                if not isinstance(levels, list) or len(levels) == 0:
                    return False
                
                # Validar cada nivel
                for level in levels:
                    if not isinstance(level, dict):
                        return False
                    
                    if 'name' not in level or 'score' not in level:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _get_fallback_rubric(
        self,
        prompt: str,
        num_criteria: int,
        num_levels: int,
        max_score: int
    ) -> Dict[str, Any]:
        """Genera una rúbrica de fallback cuando la IA no está disponible"""
        
        # Criterios genéricos basados en el prompt
        criteria_names = [
            "Comprensión del contenido",
            "Aplicación de conceptos", 
            "Comunicación y expresión",
            "Creatividad e innovación"
        ]
        
        # Ajustar según el número de criterios solicitados
        if num_criteria <= len(criteria_names):
            criteria_names = criteria_names[:num_criteria]
        else:
            # Añadir criterios adicionales
            additional = [
                "Organización y estructura",
                "Uso de recursos",
                "Reflexión y autoevaluación"
            ]
            criteria_names.extend(additional[:num_criteria - len(criteria_names)])
        
        # Generar niveles
        score_step = max_score / (num_levels - 1)
        levels = []
        level_names = ["Insuficiente", "En desarrollo", "Satisfactorio", "Excelente"]
        
        for i in range(num_levels):
            score = round(i * score_step, 1)
            level_name = level_names[i] if i < len(level_names) else f"Nivel {i + 1}"
            levels.append({
                "name": level_name,
                "description": f"Descripción del nivel {i + 1}",
                "score": score
            })
        
        # Generar criterios
        criteria = []
        weight_per_criterion = 100 / num_criteria
        
        for i, name in enumerate(criteria_names):
            criteria.append({
                "name": name,
                "description": f"Evaluación de {name.lower()}",
                "weight": round(weight_per_criterion, 1),
                "levels": levels.copy()
            })
        
        return {
            "title": f"Rúbrica: {prompt[:50]}...",
            "description": f"Rúbrica generada para: {prompt}",
            "criteria": criteria,
            "_is_fallback": True,
            "_fallback_reason": "Modelo IA no disponible"
        }


# Instancia global del servicio
openrouter_client = OpenRouterClient()
