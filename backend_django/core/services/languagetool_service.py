"""
Servicio de LanguageTool para corrección gramatical y ortográfica
"""
import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class LanguageToolService:
    """Servicio para integración con LanguageTool API"""
    
    BASE_URL = "https://api.languagetool.org/v2"
    
    def __init__(self):
        self.timeout = getattr(settings, 'LANGUAGETOOL_TIMEOUT', 10)
        self.max_text_length = getattr(settings, 'LANGUAGETOOL_MAX_TEXT_LENGTH', 20000)
    
    def corregir_texto(self, texto: str, idioma: str = "es") -> Dict:
        """
        Corrige texto usando LanguageTool API
        
        Args:
            texto: Texto a corregir
            idioma: Código de idioma (por defecto 'es' para español)
            
        Returns:
            Dict con los errores encontrados y sugerencias
        """
        try:
            # Validar longitud del texto
            if len(texto) > self.max_text_length:
                return {
                    'error': f'El texto es demasiado largo. Máximo {self.max_text_length} caracteres.',
                    'matches': []
                }
            
            # Mapear códigos de idioma a formato LanguageTool
            language_map = {
                'ca': 'ca-ES',  # Catalán
                'es': 'es',     # Español
                'en': 'en-US'   # Inglés
            }
            language_code = language_map.get(idioma, idioma)
            
            # Preparar datos para la API (SOLO los necesarios)
            data = {
                "text": texto,
                "language": language_code,
                "enabledOnly": "false"
            }
            
            # Realizar petición a LanguageTool
            response = requests.post(
                f"{self.BASE_URL}/check",
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._procesar_resultado(result)
            else:
                logger.error(f"Error en LanguageTool API: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                logger.error(f"Request data: {data}")
                return {
                    'error': 'Error al conectar con el servicio de corrección',
                    'matches': []
                }
                
        except requests.exceptions.Timeout:
            logger.error("Timeout en LanguageTool API")
            return {
                'error': 'Timeout al conectar con el servicio de corrección',
                'matches': []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con LanguageTool: {e}")
            return {
                'error': 'Error de conexión con el servicio de corrección',
                'matches': []
            }
        except Exception as e:
            logger.error(f"Error inesperado en LanguageTool: {e}")
            return {
                'error': 'Error interno del servidor',
                'matches': []
            }
    
    def _procesar_resultado(self, resultado: Dict) -> Dict:
        """
        Procesa el resultado de LanguageTool para formato educativo
        
        Args:
            resultado: Resultado crudo de LanguageTool
            
        Returns:
            Dict procesado con información educativa
        """
        matches = resultado.get('matches', [])
        errores_procesados = []
        
        for match in matches:
            error_info = {
                'offset': match.get('offset', 0),
                'length': match.get('length', 0),
                'message': match.get('message', ''),
                'short_message': match.get('shortMessage', ''),
                'rule_id': match.get('rule', {}).get('id', ''),
                'rule_description': match.get('rule', {}).get('description', ''),
                'rule_category': match.get('rule', {}).get('category', {}).get('id', ''),
                'suggestions': [],
                'context': match.get('context', {}),
                'severity': self._determinar_severidad(match)
            }
            
            # Procesar sugerencias
            replacements = match.get('replacements', [])
            for replacement in replacements[:3]:  # Máximo 3 sugerencias
                error_info['suggestions'].append({
                    'value': replacement.get('value', ''),
                    'description': replacement.get('description', '')
                })
            
            errores_procesados.append(error_info)
        
        return {
            'matches': errores_procesados,
            'total_errors': len(errores_procesados),
            'language': resultado.get('language', {}).get('name', 'Español'),
            'detected_language': resultado.get('language', {}).get('detectedLanguage', {}).get('name', 'Español')
        }
    
    def _determinar_severidad(self, match: Dict) -> str:
        """
        Determina la severidad del error para fines educativos
        
        Args:
            match: Información del error
            
        Returns:
            str: 'alta', 'media', 'baja'
        """
        rule_id = match.get('rule', {}).get('id', '')
        category = match.get('rule', {}).get('category', {}).get('id', '')
        
        # Errores de alta severidad (ortografía básica)
        alta_severidad = [
            'SPELLING', 'SPELLING_SPANISH', 'SPELLING_ES', 
            'MORFOLOGIK_RULE_ES', 'HUNSPELL_RULE'
        ]
        
        # Errores de media severidad (gramática)
        media_severidad = [
            'GRAMMAR', 'TYPOGRAPHY', 'PUNCTUATION',
            'STYLE', 'CONFUSED_WORDS'
        ]
        
        if any(rule in rule_id for rule in alta_severidad) or category in alta_severidad:
            return 'alta'
        elif any(rule in rule_id for rule in media_severidad) or category in media_severidad:
            return 'media'
        else:
            return 'baja'
    
    def obtener_estadisticas_texto(self, texto: str) -> Dict:
        """
        Obtiene estadísticas básicas del texto
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Dict con estadísticas del texto
        """
        palabras = texto.split()
        caracteres = len(texto)
        caracteres_sin_espacios = len(texto.replace(' ', ''))
        oraciones = len([s for s in texto.split('.') if s.strip()])
        
        return {
            'total_palabras': len(palabras),
            'total_caracteres': caracteres,
            'caracteres_sin_espacios': caracteres_sin_espacios,
            'total_oraciones': oraciones,
            'promedio_palabras_por_oracion': round(len(palabras) / max(oraciones, 1), 2),
            'promedio_caracteres_por_palabra': round(caracteres_sin_espacios / max(len(palabras), 1), 2)
        }


# Instancia global del servicio
languagetool_service = LanguageToolService()
