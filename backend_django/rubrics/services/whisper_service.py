"""
Servicio de integración con OpenAI Whisper para transcripción de audio.
"""
import logging
import os
from typing import Optional
import openai
from django.conf import settings

logger = logging.getLogger(__name__)


class WhisperServiceError(Exception):
    """Excepción personalizada para errores del servicio Whisper"""
    pass


class WhisperClient:
    """Cliente para interactuar con la API de OpenAI Whisper"""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.model = getattr(settings, 'WHISPER_MODEL', 'whisper-1')
        self.language = getattr(settings, 'WHISPER_LANGUAGE', None)  # None = auto-detect

        if not self.api_key:
            logger.warning("OPENAI_API_KEY no configurada")
            return

        # Configurar el cliente de OpenAI
        self.client = openai.OpenAI(api_key=self.api_key)

    def transcribe_audio(self, audio_file_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe un archivo de audio usando Whisper API.

        Args:
            audio_file_path: Ruta al archivo de audio
            language: Código de idioma (opcional, ej: 'es', 'en')

        Returns:
            str: Texto transcrito

        Raises:
            WhisperServiceError: Si hay error en la transcripción
        """
        if not self.api_key:
            raise WhisperServiceError("OPENAI_API_KEY no configurada")

        if not os.path.exists(audio_file_path):
            raise WhisperServiceError(f"Archivo de audio no encontrado: {audio_file_path}")

        try:
            with open(audio_file_path, "rb") as audio_file:
                # Preparar parámetros de transcripción
                transcription_params = {
                    "file": audio_file,
                    "model": self.model,
                    "response_format": "text",  # Solo texto plano
                }

                # Agregar idioma si se especifica
                if language or self.language:
                    transcription_params["language"] = language or self.language

                # Realizar transcripción
                transcript = self.client.audio.transcriptions.create(**transcription_params)

                logger.info(f"Transcripción completada para archivo: {audio_file_path}")
                return transcript.strip()

        except openai.APIError as e:
            logger.error(f"Error de API de OpenAI: {str(e)}")
            raise WhisperServiceError(f"Error en la API de OpenAI: {str(e)}")
        except openai.AuthenticationError as e:
            logger.error(f"Error de autenticación de OpenAI: {str(e)}")
            raise WhisperServiceError("Error de autenticación con OpenAI")
        except openai.RateLimitError as e:
            logger.error(f"Error de límite de tasa de OpenAI: {str(e)}")
            raise WhisperServiceError("Límite de tasa de OpenAI excedido")
        except Exception as e:
            logger.error(f"Error inesperado en transcripción: {str(e)}")
            raise WhisperServiceError(f"Error inesperado: {str(e)}")

    def translate_audio(self, audio_file_path: str) -> str:
        """
        Traduce un archivo de audio al inglés usando Whisper API.

        Args:
            audio_file_path: Ruta al archivo de audio

        Returns:
            str: Texto traducido al inglés

        Raises:
            WhisperServiceError: Si hay error en la traducción
        """
        if not self.api_key:
            raise WhisperServiceError("OPENAI_API_KEY no configurada")

        if not os.path.exists(audio_file_path):
            raise WhisperServiceError(f"Archivo de audio no encontrado: {audio_file_path}")

        try:
            with open(audio_file_path, "rb") as audio_file:
                # Realizar traducción
                translation = self.client.audio.translations.create(
                    file=audio_file,
                    model=self.model,
                    response_format="text"
                )

                logger.info(f"Traducción completada para archivo: {audio_file_path}")
                return translation.strip()

        except openai.APIError as e:
            logger.error(f"Error de API de OpenAI en traducción: {str(e)}")
            raise WhisperServiceError(f"Error en la API de OpenAI: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado en traducción: {str(e)}")
            raise WhisperServiceError(f"Error inesperado: {str(e)}")