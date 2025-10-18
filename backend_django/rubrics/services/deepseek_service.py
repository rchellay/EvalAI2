import requests
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class DeepSeekServiceError(Exception):
    """Excepción personalizada para errores del servicio DeepSeek"""
    pass


class DeepSeekClient:
    """Cliente para interactuar con DeepSeek R1T2 Chimera via OpenRouter"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        self.base_url = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.model = getattr(settings, 'DEEPSEEK_MODEL', 'tngtech/deepseek-r1t2-chimera:free')
        self.timeout = getattr(settings, 'DEEPSEEK_TIMEOUT', 60)  # Más tiempo para modelos grandes
        self.max_tokens = getattr(settings, 'DEEPSEEK_MAX_TOKENS', 4096)
        self.cache_ttl = getattr(settings, 'DEEPSEEK_CACHE_TTL', 86400)  # 24 horas
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY no configurada")
    
    def _get_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Genera una clave de caché única basada en el prompt y parámetros"""
        cache_data = f"{prompt}:{json.dumps(params, sort_keys=True)}"
        return f"deepseek_rubric_{hashlib.sha256(cache_data.encode()).hexdigest()}"
    
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
        Genera una rúbrica educativa usando DeepSeek R1T2 Chimera
        
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
            raise DeepSeekServiceError("El prompt no puede estar vacío")
        
        if num_criteria < 3 or num_criteria > 7:
            raise DeepSeekServiceError("El número de criterios debe estar entre 3 y 7")
        
        if num_levels < 3 or num_levels > 5:
            raise DeepSeekServiceError("El número de niveles debe estar entre 3 y 5")
        
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
        
        # Generar con DeepSeek
        logger.info(f"Generando rúbrica con DeepSeek R1T2 Chimera para: {prompt[:50]}...")
        
        # Construir el prompt estructurado
        structured_prompt = self._build_prompt(prompt, language, num_criteria, num_levels, max_score)
        
        # Intentar generar con reintentos
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self._call_deepseek_api(structured_prompt)
                
                # Validar estructura
                if self._validate_rubric_schema(result):
                    # Guardar en caché
                    cache.set(cache_key, result, self.cache_ttl)
                    result['_from_cache'] = False
                    logger.info(f"Rúbrica generada exitosamente con DeepSeek y guardada en caché")
                    return result
                else:
                    logger.warning(f"Esquema inválido en intento {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"Error en intento {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
        
        # Si todos los intentos fallan, usar fallback mejorado
        logger.warning("Todos los intentos fallaron con DeepSeek, usando fallback mejorado")
        fallback_result = self._get_fallback_rubric(prompt, num_criteria, num_levels, max_score)
        fallback_result['_is_fallback'] = True
        fallback_result['_fallback_reason'] = "API de DeepSeek no disponible"
        return fallback_result
    
    def _build_prompt(
        self,
        user_prompt: str,
        language: str,
        num_criteria: int,
        num_levels: int,
        max_score: int
    ) -> str:
        """Construye el prompt estructurado para DeepSeek"""
        
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

REQUISITOS:
- Idioma: {lang_names.get(language, 'español')}
- Número de criterios: {num_criteria}
- Número de niveles por criterio: {num_levels}
- Puntuación máxima: {max_score}

ESTRUCTURA REQUERIDA (responde SOLO con JSON válido):
{{
  "title": "Título de la rúbrica",
  "description": "Descripción breve de la rúbrica",
  "criteria": [
    {{
      "name": "Nombre del criterio",
      "description": "Descripción del criterio",
      "weight": 25.0,
      "levels": [
        {{
          "name": "Excelente",
          "description": "Descripción del nivel excelente",
          "score": {max_score},
          "color": "#10b981"
        }},
        {{
          "name": "Bueno", 
          "description": "Descripción del nivel bueno",
          "score": {max_score * 0.75},
          "color": "#3b82f6"
        }},
        {{
          "name": "Satisfactorio",
          "description": "Descripción del nivel satisfactorio", 
          "score": {max_score * 0.5},
          "color": "#f59e0b"
        }},
        {{
          "name": "Necesita mejorar",
          "description": "Descripción del nivel que necesita mejorar",
          "score": {max_score * 0.25},
          "color": "#ef4444"
        }}
      ]
    }}
  ]
}}

IMPORTANTE:
- Los criterios deben ser específicos al tema: {user_prompt}
- Los pesos deben sumar 100%
- Las descripciones deben ser detalladas y específicas
- Usa colores apropiados para cada nivel
- Responde ÚNICAMENTE con el JSON, sin texto adicional"""

        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> Dict[str, Any]:
        """Llama a la API de DeepSeek via OpenRouter"""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5173',
            'X-Title': 'EvalAI'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': self.max_tokens,
            'temperature': 0.7,
            'top_p': 0.9
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise DeepSeekServiceError(f"API error: {response.status_code} - {response.text}")
            
            # Debug: mostrar respuesta completa
            logger.info(f"Respuesta de la API: {response.text[:500]}...")
            
            data = response.json()
            
            if 'choices' not in data or len(data['choices']) == 0:
                raise DeepSeekServiceError("No se recibió respuesta válida de la API")
            
            content = data['choices'][0]['message']['content']
            
            # Debug: mostrar contenido
            logger.info(f"Contenido recibido: {content[:200]}...")
            
            # Limpiar el contenido (remover markdown si existe)
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            # Parsear JSON
            result = json.loads(content.strip())
            
            # Normalizar pesos para que sumen 100%
            self._normalize_weights(result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise DeepSeekServiceError(f"Error de conexión: {str(e)}")
        except json.JSONDecodeError as e:
            raise DeepSeekServiceError(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            raise DeepSeekServiceError(f"Error inesperado: {str(e)}")
    
    def _normalize_weights(self, rubric_data: Dict[str, Any]) -> None:
        """Normaliza los pesos para que sumen 100%"""
        if 'criteria' not in rubric_data:
            return
        
        criteria = rubric_data['criteria']
        if not criteria:
            return
        
        # Calcular suma actual
        total_weight = sum(criterion.get('weight', 0) for criterion in criteria)
        
        if total_weight == 0:
            # Si no hay pesos, asignar pesos iguales
            weight_per_criterion = 100.0 / len(criteria)
            for criterion in criteria:
                criterion['weight'] = round(weight_per_criterion, 1)
        else:
            # Normalizar para que sume 100%
            for criterion in criteria:
                current_weight = criterion.get('weight', 0)
                normalized_weight = (current_weight / total_weight) * 100
                criterion['weight'] = round(normalized_weight, 1)
    
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
        level_names = ['Excelente', 'Bueno', 'Satisfactorio', 'Necesita mejorar', 'Insuficiente']
        
        # Generar criterios específicos basados en el prompt
        criteria = self._generate_specific_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        
        return {
            'title': f'Rúbrica: {prompt[:50]}',
            'description': 'Rúbrica generada automáticamente (modo fallback)',
            'criteria': criteria,
            '_is_fallback': True,
            '_from_cache': False
        }
    
    def _generate_specific_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                  num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos basados en el prompt"""
        
        # Analizar el prompt para generar criterios específicos
        prompt_lower = prompt.lower()
        
        # Detectar tipo de contenido
        if any(word in prompt_lower for word in ['presentación', 'oral', 'exposición', 'hablar']):
            return self._generate_presentation_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        elif any(word in prompt_lower for word in ['escrito', 'redacción', 'composición', 'texto']):
            return self._generate_writing_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        elif any(word in prompt_lower for word in ['proyecto', 'investigación', 'trabajo']):
            return self._generate_project_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        elif any(word in prompt_lower for word in ['geografía', 'comarques', 'catalunya', 'región', 'territorio', 'países', 'europa', 'espanya']):
            return self._generate_geography_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        elif any(word in prompt_lower for word in ['historia', 'histórico', 'época', 'siglo']):
            return self._generate_history_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        elif any(word in prompt_lower for word in ['ciencia', 'científico', 'experimento', 'laboratorio']):
            return self._generate_science_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        elif any(word in prompt_lower for word in ['matemática', 'matemáticas', 'cálculo', 'problema']):
            return self._generate_math_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
        else:
            return self._generate_general_criteria(prompt, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_geography_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                   num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos para geografía"""
        criteria_templates = [
            {
                'name': 'Conocimiento geográfico',
                'description': 'Demuestra conocimiento preciso de la ubicación, características físicas y datos geográficos',
                'levels': [
                    'Conocimiento exhaustivo y preciso de todos los elementos geográficos',
                    'Conocimiento sólido con algunos detalles menores',
                    'Conocimiento básico con algunas imprecisiones',
                    'Conocimiento limitado con errores significativos',
                    'Conocimiento insuficiente o incorrecto'
                ]
            },
            {
                'name': 'Análisis territorial',
                'description': 'Analiza correctamente las características socioeconómicas y culturales del territorio',
                'levels': [
                    'Análisis profundo y bien fundamentado con múltiples perspectivas',
                    'Análisis sólido con buena fundamentación',
                    'Análisis básico con fundamentación limitada',
                    'Análisis superficial con poca fundamentación',
                    'Análisis insuficiente o sin fundamentación'
                ]
            },
            {
                'name': 'Organización espacial',
                'description': 'Presenta la información de manera clara y organizada espacialmente',
                'levels': [
                    'Organización excelente con estructura lógica y clara',
                    'Organización buena con estructura coherente',
                    'Organización aceptable con algunas inconsistencias',
                    'Organización básica con estructura confusa',
                    'Organización deficiente sin estructura clara'
                ]
            },
            {
                'name': 'Uso de recursos cartográficos',
                'description': 'Utiliza mapas, gráficos y recursos visuales de manera efectiva',
                'levels': [
                    'Uso excelente de recursos visuales con interpretación precisa',
                    'Uso bueno de recursos con interpretación adecuada',
                    'Uso básico de recursos con interpretación limitada',
                    'Uso mínimo de recursos con interpretación deficiente',
                    'Uso insuficiente o incorrecto de recursos'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_presentation_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                      num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos para presentaciones orales"""
        criteria_templates = [
            {
                'name': 'Contenido y conocimiento',
                'description': 'Demuestra dominio del tema y presenta información relevante y precisa',
                'levels': [
                    'Dominio excepcional con información completa y precisa',
                    'Buen dominio con información relevante',
                    'Dominio básico con información adecuada',
                    'Dominio limitado con información insuficiente',
                    'Dominio insuficiente con información incorrecta'
                ]
            },
            {
                'name': 'Comunicación oral',
                'description': 'Se expresa con claridad, fluidez y uso apropiado del lenguaje',
                'levels': [
                    'Comunicación excelente con fluidez y claridad excepcional',
                    'Comunicación buena con fluidez y claridad adecuada',
                    'Comunicación aceptable con algunas dificultades',
                    'Comunicación básica con dificultades evidentes',
                    'Comunicación deficiente con problemas graves'
                ]
            },
            {
                'name': 'Estructura y organización',
                'description': 'Organiza la presentación de manera lógica y coherente',
                'levels': [
                    'Estructura excelente con organización lógica perfecta',
                    'Estructura buena con organización coherente',
                    'Estructura aceptable con organización básica',
                    'Estructura limitada con organización confusa',
                    'Estructura deficiente sin organización clara'
                ]
            },
            {
                'name': 'Recursos y apoyo visual',
                'description': 'Utiliza recursos visuales y de apoyo de manera efectiva',
                'levels': [
                    'Uso excelente de recursos con gran impacto visual',
                    'Uso bueno de recursos con impacto adecuado',
                    'Uso básico de recursos con impacto limitado',
                    'Uso mínimo de recursos con poco impacto',
                    'Uso insuficiente o inadecuado de recursos'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_writing_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                 num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos para escritura"""
        criteria_templates = [
            {
                'name': 'Contenido y desarrollo',
                'description': 'Desarrolla ideas de manera coherente y con profundidad',
                'levels': [
                    'Desarrollo excepcional con ideas profundas y bien desarrolladas',
                    'Desarrollo sólido con ideas bien estructuradas',
                    'Desarrollo básico con ideas adecuadas',
                    'Desarrollo limitado con ideas superficiales',
                    'Desarrollo insuficiente con ideas confusas'
                ]
            },
            {
                'name': 'Estructura y organización',
                'description': 'Organiza el texto de manera lógica y coherente',
                'levels': [
                    'Estructura excelente con organización perfecta',
                    'Estructura buena con organización coherente',
                    'Estructura aceptable con organización básica',
                    'Estructura limitada con organización confusa',
                    'Estructura deficiente sin organización clara'
                ]
            },
            {
                'name': 'Expresión y estilo',
                'description': 'Utiliza un lenguaje apropiado y variado',
                'levels': [
                    'Expresión excelente con lenguaje rico y variado',
                    'Expresión buena con lenguaje apropiado',
                    'Expresión aceptable con lenguaje básico',
                    'Expresión limitada con lenguaje pobre',
                    'Expresión deficiente con lenguaje inadecuado'
                ]
            },
            {
                'name': 'Ortografía y gramática',
                'description': 'Maneja correctamente la ortografía y gramática',
                'levels': [
                    'Ortografía y gramática perfectas',
                    'Ortografía y gramática correctas con errores menores',
                    'Ortografía y gramática aceptables con algunos errores',
                    'Ortografía y gramática limitadas con errores frecuentes',
                    'Ortografía y gramática deficientes con muchos errores'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_project_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                  num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos para proyectos"""
        criteria_templates = [
            {
                'name': 'Planificación y metodología',
                'description': 'Demuestra una planificación adecuada y metodología clara',
                'levels': [
                    'Planificación excelente con metodología perfecta',
                    'Planificación buena con metodología adecuada',
                    'Planificación básica con metodología simple',
                    'Planificación limitada con metodología confusa',
                    'Planificación deficiente sin metodología clara'
                ]
            },
            {
                'name': 'Investigación y fuentes',
                'description': 'Utiliza fuentes apropiadas y realiza investigación adecuada',
                'levels': [
                    'Investigación exhaustiva con fuentes excelentes',
                    'Investigación sólida con fuentes apropiadas',
                    'Investigación básica con fuentes limitadas',
                    'Investigación superficial con fuentes inadecuadas',
                    'Investigación insuficiente sin fuentes apropiadas'
                ]
            },
            {
                'name': 'Creatividad e innovación',
                'description': 'Muestra originalidad y enfoque innovador',
                'levels': [
                    'Creatividad excepcional con enfoque muy innovador',
                    'Creatividad buena con enfoque original',
                    'Creatividad básica con algunos elementos nuevos',
                    'Creatividad limitada con enfoque convencional',
                    'Creatividad insuficiente sin elementos innovadores'
                ]
            },
            {
                'name': 'Presentación y comunicación',
                'description': 'Presenta el proyecto de manera clara y efectiva',
                'levels': [
                    'Presentación excelente con comunicación perfecta',
                    'Presentación buena con comunicación clara',
                    'Presentación aceptable con comunicación básica',
                    'Presentación limitada con comunicación confusa',
                    'Presentación deficiente sin comunicación clara'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_history_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                 num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos para historia"""
        criteria_templates = [
            {
                'name': 'Conocimiento histórico',
                'description': 'Demuestra conocimiento preciso de hechos, fechas y contextos históricos',
                'levels': [
                    'Conocimiento exhaustivo y preciso de todos los elementos históricos',
                    'Conocimiento sólido con algunos detalles menores',
                    'Conocimiento básico con algunas imprecisiones',
                    'Conocimiento limitado con errores significativos',
                    'Conocimiento insuficiente o incorrecto'
                ]
            },
            {
                'name': 'Análisis histórico',
                'description': 'Analiza causas, consecuencias y relaciones históricas',
                'levels': [
                    'Análisis profundo con comprensión de múltiples causas y efectos',
                    'Análisis sólido con buena comprensión de relaciones',
                    'Análisis básico con comprensión limitada',
                    'Análisis superficial con poca comprensión',
                    'Análisis insuficiente sin comprensión clara'
                ]
            },
            {
                'name': 'Interpretación de fuentes',
                'description': 'Utiliza y analiza fuentes históricas de manera crítica',
                'levels': [
                    'Interpretación excelente con análisis crítico profundo',
                    'Interpretación buena con análisis crítico adecuado',
                    'Interpretación básica con análisis limitado',
                    'Interpretación superficial con análisis deficiente',
                    'Interpretación insuficiente sin análisis crítico'
                ]
            },
            {
                'name': 'Contextualización temporal',
                'description': 'Ubica los hechos en su contexto temporal y espacial',
                'levels': [
                    'Contextualización excelente con ubicación perfecta',
                    'Contextualización buena con ubicación adecuada',
                    'Contextualización básica con ubicación limitada',
                    'Contextualización superficial con ubicación confusa',
                    'Contextualización insuficiente sin ubicación clara'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_science_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                  num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos para ciencias"""
        criteria_templates = [
            {
                'name': 'Conocimiento científico',
                'description': 'Demuestra comprensión de conceptos, principios y teorías científicas',
                'levels': [
                    'Conocimiento exhaustivo con comprensión profunda de conceptos',
                    'Conocimiento sólido con buena comprensión',
                    'Conocimiento básico con comprensión limitada',
                    'Conocimiento superficial con comprensión deficiente',
                    'Conocimiento insuficiente sin comprensión clara'
                ]
            },
            {
                'name': 'Metodología científica',
                'description': 'Aplica correctamente el método científico y procedimientos',
                'levels': [
                    'Metodología excelente con aplicación perfecta del método científico',
                    'Metodología buena con aplicación adecuada',
                    'Metodología básica con aplicación limitada',
                    'Metodología superficial con aplicación deficiente',
                    'Metodología insuficiente sin aplicación clara'
                ]
            },
            {
                'name': 'Análisis de datos',
                'description': 'Analiza datos, resultados y evidencia de manera crítica',
                'levels': [
                    'Análisis excelente con interpretación precisa de datos',
                    'Análisis bueno con interpretación adecuada',
                    'Análisis básico con interpretación limitada',
                    'Análisis superficial con interpretación deficiente',
                    'Análisis insuficiente sin interpretación clara'
                ]
            },
            {
                'name': 'Comunicación científica',
                'description': 'Comunica hallazgos científicos de manera clara y precisa',
                'levels': [
                    'Comunicación excelente con precisión científica perfecta',
                    'Comunicación buena con precisión adecuada',
                    'Comunicación básica con precisión limitada',
                    'Comunicación superficial con precisión deficiente',
                    'Comunicación insuficiente sin precisión científica'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_math_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                               num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios específicos para matemáticas"""
        criteria_templates = [
            {
                'name': 'Comprensión conceptual',
                'description': 'Demuestra comprensión de conceptos y principios matemáticos',
                'levels': [
                    'Comprensión excepcional con dominio completo de conceptos',
                    'Comprensión sólida con buen dominio',
                    'Comprensión básica con dominio limitado',
                    'Comprensión superficial con dominio mínimo',
                    'Comprensión insuficiente sin dominio de conceptos'
                ]
            },
            {
                'name': 'Resolución de problemas',
                'description': 'Aplica estrategias apropiadas para resolver problemas',
                'levels': [
                    'Resolución excelente con estrategias múltiples y efectivas',
                    'Resolución buena con estrategias apropiadas',
                    'Resolución básica con estrategias limitadas',
                    'Resolución superficial con estrategias inadecuadas',
                    'Resolución insuficiente sin estrategias claras'
                ]
            },
            {
                'name': 'Precisión y exactitud',
                'description': 'Realiza cálculos y operaciones con precisión',
                'levels': [
                    'Precisión perfecta en todos los cálculos',
                    'Precisión buena con errores menores',
                    'Precisión básica con algunos errores',
                    'Precisión limitada con errores frecuentes',
                    'Precisión deficiente con muchos errores'
                ]
            },
            {
                'name': 'Comunicación matemática',
                'description': 'Explica procesos y resultados de manera clara',
                'levels': [
                    'Comunicación excelente con explicaciones perfectas',
                    'Comunicación buena con explicaciones claras',
                    'Comunicación básica con explicaciones limitadas',
                    'Comunicación superficial con explicaciones confusas',
                    'Comunicación insuficiente sin explicaciones claras'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _generate_general_criteria(self, prompt: str, num_criteria: int, weight_per_criterion: float, 
                                 num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Genera criterios generales cuando no se puede determinar el tipo específico"""
        criteria_templates = [
            {
                'name': 'Comprensión del contenido',
                'description': f'Demuestra comprensión profunda del tema: {prompt[:30]}...',
                'levels': [
                    'Comprensión excepcional con dominio completo del tema',
                    'Comprensión sólida con buen dominio del tema',
                    'Comprensión básica con dominio limitado',
                    'Comprensión superficial con dominio mínimo',
                    'Comprensión insuficiente sin dominio del tema'
                ]
            },
            {
                'name': 'Organización y estructura',
                'description': 'Presenta la información de manera clara y organizada',
                'levels': [
                    'Organización excelente con estructura perfecta',
                    'Organización buena con estructura coherente',
                    'Organización aceptable con estructura básica',
                    'Organización limitada con estructura confusa',
                    'Organización deficiente sin estructura clara'
                ]
            },
            {
                'name': 'Creatividad e innovación',
                'description': 'Muestra originalidad y pensamiento creativo en el enfoque',
                'levels': [
                    'Creatividad excepcional con enfoque innovador',
                    'Creatividad buena con enfoque original',
                    'Creatividad básica con algunos elementos nuevos',
                    'Creatividad limitada con enfoque convencional',
                    'Creatividad insuficiente sin elementos innovadores'
                ]
            },
            {
                'name': 'Comunicación efectiva',
                'description': 'Comunica ideas de forma clara y persuasiva',
                'levels': [
                    'Comunicación excelente con gran claridad y persuasión',
                    'Comunicación buena con claridad y persuasión adecuada',
                    'Comunicación aceptable con claridad básica',
                    'Comunicación limitada con claridad deficiente',
                    'Comunicación insuficiente sin claridad'
                ]
            }
        ]
        
        return self._build_criteria_from_templates(criteria_templates, num_criteria, weight_per_criterion, num_levels, max_score, colors, level_names)
    
    def _build_criteria_from_templates(self, templates: list, num_criteria: int, weight_per_criterion: float, 
                                     num_levels: int, max_score: int, colors: list, level_names: list) -> list:
        """Construye criterios a partir de plantillas"""
        criteria = []
        
        for i in range(num_criteria):
            template = templates[i] if i < len(templates) else templates[0]
            
            levels = []
            for j in range(num_levels):
                score = max_score * (1 - (j / num_levels))
                level_description = template['levels'][j] if j < len(template['levels']) else template['levels'][-1]
                
                levels.append({
                    'name': level_names[j] if j < len(level_names) else f'Nivel {j+1}',
                    'description': level_description,
                    'score': round(score, 1),
                    'color': colors[j] if j < len(colors) else '#6b7280'
                })
            
            criteria.append({
                'name': template['name'],
                'description': template['description'],
                'weight': weight_per_criterion,
                'levels': levels
            })
        
        return criteria
