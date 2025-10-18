"""
Servicio Google Cloud Vision OCR para transcripción de escritura manuscrita
Integrado con corrección automática usando LanguageTool
"""
import os
import logging
import tempfile
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from google.cloud import vision_v1p3beta1 as vision
from google.api_core import exceptions as gcp_exceptions

logger = logging.getLogger(__name__)

class GoogleVisionOCRError(Exception):
    """Excepción personalizada para errores del servicio Google Cloud Vision OCR"""
    pass

class GoogleVisionOCRClient:
    """Cliente para OCR de escritura manuscrita usando Google Cloud Vision"""
    
    def __init__(self):
        self.client = None
        self.project_id = getattr(settings, 'GOOGLE_CLOUD_PROJECT_ID', None)
        self.credentials_path = getattr(settings, 'GOOGLE_CLOUD_CREDENTIALS_PATH', None)
        self.max_file_size = getattr(settings, 'GOOGLE_VISION_MAX_FILE_SIZE', 20 * 1024 * 1024)  # 20MB
        
        # Configurar cliente
        self._setup_client()
    
    def _setup_client(self):
        """Configura el cliente de Google Cloud Vision"""
        try:
            # Si hay ruta de credenciales, usarla
            if self.credentials_path and os.path.exists(self.credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
                logger.info(f"Usando credenciales desde: {self.credentials_path}")
            
            # Crear cliente
            self.client = vision.ImageAnnotatorClient()
            logger.info("Cliente Google Cloud Vision configurado correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando Google Cloud Vision: {str(e)}")
            self.client = None
    
    def detect_handwritten_text(
        self, 
        image_path: str, 
        language_hint: str = "es-t-i0-handwrit"
    ) -> Dict[str, any]:
        """
        Detecta texto manuscrito en una imagen
        
        Args:
            image_path: Ruta al archivo de imagen
            language_hint: Hint de idioma para manuscrito
            
        Returns:
            Dict con texto extraído y metadatos
        """
        if not self.client:
            raise GoogleVisionOCRError("Cliente Google Cloud Vision no configurado")
        
        try:
            # Validar archivo
            if not os.path.exists(image_path):
                raise GoogleVisionOCRError(f"Archivo de imagen no encontrado: {image_path}")
            
            # Verificar tamaño
            file_size = os.path.getsize(image_path)
            if file_size > self.max_file_size:
                raise GoogleVisionOCRError(f"Archivo demasiado grande: {file_size} bytes (máximo: {self.max_file_size})")
            
            # Leer imagen
            with open(image_path, "rb") as img_file:
                content = img_file.read()
            
            # Crear objeto imagen
            image = vision.Image(content=content)
            
            # Configurar contexto con hint de manuscrito
            image_context = vision.ImageContext(
                language_hints=[language_hint]
            )
            
            logger.info(f"Procesando imagen manuscrita: {image_path}")
            
            # Detectar texto manuscrito
            response = self.client.document_text_detection(
                image=image, 
                image_context=image_context
            )
            
            # Verificar errores
            if response.error.message:
                raise GoogleVisionOCRError(f"Error de Google Cloud Vision: {response.error.message}")
            
            # Extraer texto y metadatos
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Extraer información detallada de palabras
            words_info = self._extract_words_info(response)
            
            # Calcular confianza promedio
            confidence_scores = [word.get('confidence', 0) for word in words_info]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            result = {
                'text': full_text.strip(),
                'words': words_info,
                'confidence': avg_confidence,
                'word_count': len(words_info),
                'language_hint': language_hint,
                'processing_info': {
                    'file_size': file_size,
                    'success': True,
                    'error': None
                }
            }
            
            logger.info(f"OCR completado exitosamente. Palabras detectadas: {len(words_info)}")
            return result
            
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Error de API de Google Cloud: {str(e)}")
            raise GoogleVisionOCRError(f"Error de API de Google Cloud: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado en OCR: {str(e)}")
            raise GoogleVisionOCRError(f"Error inesperado: {str(e)}")
    
    def _extract_words_info(self, response) -> List[Dict]:
        """Extrae información detallada de cada palabra detectada"""
        words_info = []
        
        if not response.full_text_annotation:
            return words_info
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        # Extraer texto de la palabra
                        word_text = ""
                        for symbol in word.symbols:
                            word_text += symbol.text
                        
                        # Calcular confianza promedio de los símbolos
                        symbol_confidences = [symbol.confidence for symbol in word.symbols]
                        avg_confidence = sum(symbol_confidences) / len(symbol_confidences) if symbol_confidences else 0
                        
                        # Obtener bounding box
                        vertices = word.bounding_box.vertices
                        bounding_box = {
                            'x1': vertices[0].x if len(vertices) > 0 else 0,
                            'y1': vertices[0].y if len(vertices) > 0 else 0,
                            'x2': vertices[2].x if len(vertices) > 2 else 0,
                            'y2': vertices[2].y if len(vertices) > 2 else 0,
                        }
                        
                        words_info.append({
                            'text': word_text,
                            'confidence': avg_confidence,
                            'bounding_box': bounding_box,
                            'is_low_confidence': avg_confidence < 0.7  # Marcar palabras con baja confianza
                        })
        
        return words_info
    
    def detect_printed_text(self, image_path: str, language_hint: str = "es") -> Dict[str, any]:
        """
        Detecta texto impreso (fallback si no es manuscrito)
        
        Args:
            image_path: Ruta al archivo de imagen
            language_hint: Hint de idioma
            
        Returns:
            Dict con texto extraído y metadatos
        """
        if not self.client:
            raise GoogleVisionOCRError("Cliente Google Cloud Vision no configurado")
        
        try:
            with open(image_path, "rb") as img_file:
                content = img_file.read()
            
            image = vision.Image(content=content)
            image_context = vision.ImageContext(language_hints=[language_hint])
            
            # Usar text_detection en lugar de document_text_detection
            response = self.client.text_detection(image=image, image_context=image_context)
            
            if response.error.message:
                raise GoogleVisionOCRError(f"Error de Google Cloud Vision: {response.error.message}")
            
            # Extraer texto
            texts = response.text_annotations
            full_text = texts[0].description if texts else ""
            
            result = {
                'text': full_text.strip(),
                'words': [],  # Simplificado para texto impreso
                'confidence': 0.9,  # Asumir alta confianza para texto impreso
                'word_count': len(full_text.split()),
                'language_hint': language_hint,
                'processing_info': {
                    'file_size': os.path.getsize(image_path),
                    'success': True,
                    'error': None,
                    'type': 'printed'
                }
            }
            
            logger.info(f"OCR de texto impreso completado")
            return result
            
        except Exception as e:
            logger.error(f"Error en OCR de texto impreso: {str(e)}")
            raise GoogleVisionOCRError(f"Error en OCR de texto impreso: {str(e)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Obtiene idiomas soportados para manuscrito
        
        Returns:
            Dict con códigos de idioma y nombres
        """
        return {
            'es-t-i0-handwrit': 'Español manuscrito',
            'en-t-i0-handwrit': 'Inglés manuscrito',
            'ca-t-i0-handwrit': 'Catalán manuscrito',
            'fr-t-i0-handwrit': 'Francés manuscrito',
            'de-t-i0-handwrit': 'Alemán manuscrito',
            'it-t-i0-handwrit': 'Italiano manuscrito',
            'pt-t-i0-handwrit': 'Portugués manuscrito',
            'es': 'Español impreso',
            'en': 'Inglés impreso',
            'ca': 'Catalán impreso',
            'fr': 'Francés impreso',
            'de': 'Alemán impreso',
            'it': 'Italiano impreso',
            'pt': 'Portugués impreso'
        }
    
    def validate_image(self, image_path: str) -> Dict[str, any]:
        """
        Valida si una imagen es adecuada para OCR
        
        Args:
            image_path: Ruta al archivo de imagen
            
        Returns:
            Dict con información de validación
        """
        try:
            if not os.path.exists(image_path):
                return {
                    'valid': False,
                    'error': 'Archivo no encontrado',
                    'suggestions': []
                }
            
            file_size = os.path.getsize(image_path)
            
            # Verificar tamaño
            if file_size > self.max_file_size:
                return {
                    'valid': False,
                    'error': f'Archivo demasiado grande ({file_size} bytes)',
                    'suggestions': ['Comprime la imagen o reduce la resolución']
                }
            
            # Verificar extensión
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(image_path)[1].lower()
            
            if file_ext not in allowed_extensions:
                return {
                    'valid': False,
                    'error': f'Formato no soportado: {file_ext}',
                    'suggestions': [f'Usa uno de estos formatos: {", ".join(allowed_extensions)}']
                }
            
            return {
                'valid': True,
                'error': None,
                'suggestions': [
                    'Asegúrate de que la imagen esté bien iluminada',
                    'Evita sombras y reflejos',
                    'La escritura debe ser clara y legible',
                    'Mantén la imagen estable (sin movimiento)'
                ]
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validando imagen: {str(e)}',
                'suggestions': []
            }


# Instancia global del servicio
google_vision_ocr_client = GoogleVisionOCRClient()
