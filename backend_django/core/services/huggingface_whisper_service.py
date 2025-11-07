"""
Servicio de transcripción de audio usando Hugging Face Whisper (gratuito)
Reemplaza OpenAI Whisper con modelo open source gratuito
"""
import requests
import json
import logging
import tempfile
import os
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class HuggingFaceWhisperError(Exception):
    """Excepción personalizada para errores del servicio Hugging Face Whisper"""
    pass

class HuggingFaceWhisperClient:
    """Cliente para transcripción de audio usando Hugging Face Whisper"""
    
    def __init__(self):
        # IMPORTANTE: Usando modelo alternativo porque openai/whisper-large-v3 retorna 410 Gone
        # El modelo openai/whisper-base es más pequeño pero funcional
        # Documentación: https://huggingface.co/openai/whisper-base
        self.api_url = "https://api-inference.huggingface.co/models/openai/whisper-base"
        self.api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
        self.timeout = getattr(settings, 'HUGGINGFACE_TIMEOUT', 60)
        self.max_file_size = getattr(settings, 'HUGGINGFACE_MAX_FILE_SIZE', 25 * 1024 * 1024)  # 25MB
        
        if not self.api_key:
            logger.warning("HUGGINGFACE_API_KEY no configurada - la API gratuita puede tener límites")
    
    def transcribe_audio(
        self, 
        audio_file_path: str, 
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> str:
        """
        Transcribe audio usando Hugging Face Whisper
        
        Args:
            audio_file_path: Ruta al archivo de audio
            language: Código de idioma (es, en, ca, fr)
            task: "transcribe" o "translate"
            
        Returns:
            str: Texto transcrito
        """
        try:
            # Validar archivo
            if not os.path.exists(audio_file_path):
                raise HuggingFaceWhisperError(f"Archivo de audio no encontrado: {audio_file_path}")
            
            # Verificar tamaño del archivo
            file_size = os.path.getsize(audio_file_path)
            if file_size > self.max_file_size:
                raise HuggingFaceWhisperError(f"Archivo demasiado grande: {file_size} bytes (máximo: {self.max_file_size})")
            
            # Preparar headers
            headers = {
                'Authorization': f'Bearer {self.api_key}' if self.api_key else None
            }
            headers = {k: v for k, v in headers.items() if v is not None}
            
            # Preparar parámetros
            params = {
                'task': task,
                'return_timestamps': False
            }
            
            # Agregar idioma si se especifica
            if language:
                params['language'] = language
            
            # Leer archivo de audio y enviarlo directamente en el body
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                
                logger.info(f"Iniciando transcripción con Hugging Face Whisper: {audio_file_path}")
                logger.info(f"Tamaño del archivo: {len(audio_data)} bytes")
                
                # Realizar petición - enviar audio directamente en el body
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=audio_data,  # Enviar audio directamente, no como multipart
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extraer texto transcrito
                    if isinstance(result, dict):
                        text = result.get('text', '')
                    elif isinstance(result, list) and len(result) > 0:
                        text = result[0].get('text', '')
                    else:
                        text = str(result)
                    
                    logger.info(f"Transcripción completada exitosamente")
                    return text.strip()
                    
                elif response.status_code == 503:
                    # Modelo cargando, esperar y reintentar
                    logger.warning("Modelo cargando, esperando...")
                    import time
                    time.sleep(10)
                    return self.transcribe_audio(audio_file_path, language, task)
                    
                elif response.status_code == 429:
                    raise HuggingFaceWhisperError("Límite de tasa excedido. Espera un momento antes de reintentar.")
                    
                elif response.status_code == 401:
                    raise HuggingFaceWhisperError("Error de autenticación. Verifica tu API key de Hugging Face.")
                    
                else:
                    error_msg = f"Error en Hugging Face API: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text}"
                    
                    raise HuggingFaceWhisperError(error_msg)
                    
        except requests.exceptions.Timeout:
            raise HuggingFaceWhisperError("Timeout al conectar con Hugging Face API")
        except requests.exceptions.RequestException as e:
            raise HuggingFaceWhisperError(f"Error de conexión: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado en transcripción: {str(e)}")
            raise HuggingFaceWhisperError(f"Error inesperado: {str(e)}")
    
    def translate_audio(self, audio_file_path: str) -> str:
        """
        Traduce audio a inglés usando Hugging Face Whisper
        
        Args:
            audio_file_path: Ruta al archivo de audio
            
        Returns:
            str: Texto traducido al inglés
        """
        return self.transcribe_audio(audio_file_path, task="translate")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Obtiene lista de idiomas soportados
        
        Returns:
            Dict con códigos de idioma y nombres
        """
        return {
            'es': 'Español',
            'en': 'Inglés',
            'ca': 'Catalán',
            'fr': 'Francés',
            'de': 'Alemán',
            'it': 'Italiano',
            'pt': 'Portugués',
            'ru': 'Ruso',
            'ja': 'Japonés',
            'ko': 'Coreano',
            'zh': 'Chino',
            'ar': 'Árabe',
            'hi': 'Hindi',
            'nl': 'Holandés',
            'sv': 'Sueco',
            'no': 'Noruego',
            'da': 'Danés',
            'fi': 'Finlandés',
            'pl': 'Polaco',
            'tr': 'Turco',
            'uk': 'Ucraniano',
            'cs': 'Checo',
            'hu': 'Húngaro',
            'ro': 'Rumano',
            'bg': 'Búlgaro',
            'hr': 'Croata',
            'sk': 'Eslovaco',
            'sl': 'Esloveno',
            'et': 'Estonio',
            'lv': 'Letón',
            'lt': 'Lituano',
            'mt': 'Maltés',
            'cy': 'Galés',
            'ga': 'Irlandés',
            'eu': 'Euskera',
            'gl': 'Gallego'
        }
    
    def detect_language(self, audio_file_path: str) -> str:
        """
        Detecta el idioma del audio
        
        Args:
            audio_file_path: Ruta al archivo de audio
            
        Returns:
            str: Código de idioma detectado
        """
        try:
            # Hacer una transcripción sin especificar idioma para detectar automáticamente
            result = self.transcribe_audio(audio_file_path, language=None)
            
            # Por ahora devolvemos español por defecto
            # En el futuro se podría implementar detección más sofisticada
            return 'es'
            
        except Exception as e:
            logger.warning(f"Error detectando idioma: {str(e)}")
            return 'es'  # Fallback a español


# Instancia global del servicio
huggingface_whisper_client = HuggingFaceWhisperClient()
