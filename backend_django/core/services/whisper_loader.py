"""
Google Speech-to-Text Service
================================
60 minutos/mes GRATIS - Compatible con Render Free Tier
No requiere instalación de dependencias del sistema.

API gratuita de Google Cloud con límite generoso.
"""

import os
import sys
from typing import Optional
from django.conf import settings

try:
    from google.cloud import speech_v1 as speech
    from google.oauth2 import service_account
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False
    print("[SPEECH] WARNING: google-cloud-speech no está instalado", file=sys.stderr, flush=True)


class GoogleSpeechService:
    """
    Servicio de transcripción de audio usando Google Speech-to-Text.
    
    Ventajas:
    - 60 minutos/mes GRATIS
    - Pure Python (no requiere FFmpeg/compilación)
    - Compatible con Render Free Tier
    - Soporta 125+ idiomas
    - Alta precisión
    
    Límites gratuitos:
    - 60 minutos/mes de audio estándar
    - Archivos hasta 10MB (REST API)
    """
    
    def __init__(self):
        """
        Inicializa el servicio de Google Speech-to-Text.
        """
        self.client = None
        self.credentials_json = getattr(settings, 'GOOGLE_SPEECH_CREDENTIALS_JSON', None)
        
        print(f"[SPEECH] Inicializando GoogleSpeechService", file=sys.stderr, flush=True)
    
    def is_available(self) -> bool:
        """
        Verifica si el servicio está disponible.
        """
        if not GOOGLE_SPEECH_AVAILABLE:
            return False
        
        if not self.credentials_json:
            print("[SPEECH] ERROR: GOOGLE_SPEECH_CREDENTIALS_JSON no configurado", file=sys.stderr, flush=True)
            return False
        
        return True
    
    def _get_client(self):
        """
        Obtiene o crea el cliente de Google Speech.
        """
        if self.client is not None:
            return self.client
        
        try:
            # Cargar credenciales desde JSON string
            import json
            credentials_dict = json.loads(self.credentials_json)
            credentials = service_account.Credentials.from_service_account_info(credentials_dict)
            
            self.client = speech.SpeechClient(credentials=credentials)
            print("[SPEECH] ✅ Cliente de Google Speech inicializado", file=sys.stderr, flush=True)
            return self.client
            
        except Exception as e:
            print(f"[SPEECH] ❌ ERROR al inicializar cliente: {str(e)}", file=sys.stderr, flush=True)
            return None
    
    def transcribe_audio(self, audio_path: str, language: str = "es-ES") -> Optional[str]:
        """
        Transcribe un archivo de audio a texto.
        
        Args:
            audio_path: Ruta al archivo de audio
            language: Código de idioma (es-ES, en-US, ca-ES, etc.)
        
        Returns:
            Texto transcrito o None si falla
        """
        if not self.is_available():
            print("[SPEECH] ERROR: Servicio no disponible", file=sys.stderr, flush=True)
            return None
        
        client = self._get_client()
        if not client:
            return None
        
        try:
            print(f"[SPEECH] Transcribiendo audio: {audio_path}", file=sys.stderr, flush=True)
            print(f"[SPEECH] Idioma: {language}", file=sys.stderr, flush=True)
            
            # Leer archivo de audio
            with open(audio_path, 'rb') as audio_file:
                content = audio_file.read()
            
            # Configurar audio
            audio = speech.RecognitionAudio(content=content)
            
            # Configurar reconocimiento
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
                enable_automatic_punctuation=True,
                model="default"
            )
            
            # Realizar transcripción
            print("[SPEECH] Enviando audio a Google Speech API...", file=sys.stderr, flush=True)
            response = client.recognize(config=config, audio=audio)
            
            # Extraer texto
            transcription = ""
            for result in response.results:
                transcription += result.alternatives[0].transcript + " "
            
            transcription = transcription.strip()
            
            if not transcription:
                print("[SPEECH] ⚠️ No se detectó voz en el audio", file=sys.stderr, flush=True)
                return None
            
            print(f"[SPEECH] ✅ Transcripción completada", file=sys.stderr, flush=True)
            print(f"[SPEECH] Texto ({len(transcription)} caracteres): {transcription[:100]}...", file=sys.stderr, flush=True)
            
            return transcription
            
        except Exception as e:
            print(f"[SPEECH] ❌ ERROR al transcribir: {str(e)}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()
            return None


# Singleton global
_speech_service: Optional[GoogleSpeechService] = None


def get_whisper_service() -> GoogleSpeechService:
    """
    Obtiene la instancia global del servicio (singleton).
    NOTA: Mantiene el nombre 'get_whisper_service' por compatibilidad.
    
    Returns:
        Instancia de GoogleSpeechService
    """
    global _speech_service
    
    if _speech_service is None:
        _speech_service = GoogleSpeechService()
    
    return _speech_service


def transcribe_audio(audio_path: str, language: str = "es-ES") -> Optional[str]:
    """
    Función helper para transcribir audio directamente.
    
    Args:
        audio_path: Ruta al archivo de audio
        language: Código de idioma (por defecto "es-ES")
    
    Returns:
        Texto transcrito o None si falla
    """
    service = get_whisper_service()
    return service.transcribe_audio(audio_path, language=language)
