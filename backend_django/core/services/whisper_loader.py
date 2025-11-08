"""
Faster Whisper Service
======================
100% gratuito, compatible con Render Free Tier.
No requiere API keys, ni compilación, ni apt-get.

Modelo: small (mejor balance velocidad/precisión)
Device: CPU (compatible con Render)
Compute Type: int8 (bajo consumo de RAM)
Auto-descarga: Los modelos se descargan automáticamente en runtime
"""

import os
import sys
from pathlib import Path
from typing import Optional
from django.conf import settings

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    print("[WHISPER] WARNING: faster-whisper no está instalado", file=sys.stderr, flush=True)


class FasterWhisperService:
    """
    Servicio de transcripción de audio usando faster-whisper.
    
    Ventajas:
    - 100% gratuito (sin API keys)
    - 4x más rápido que whisper original
    - Bajo consumo de memoria (int8 quantization)
    - Auto-descarga de modelos
    - Compatible con Render Free Tier (solo CPU)
    """
    
    def __init__(self, model_size: str = "small"):
        """
        Inicializa el servicio de Whisper.
        
        Args:
            model_size: Tamaño del modelo ("tiny", "base", "small", "medium", "large")
                       - tiny: ~75MB, rápido pero menos preciso
                       - base: ~145MB, buen balance
                       - small: ~488MB, RECOMENDADO (mejor balance)
                       - medium: ~1.5GB, más preciso pero lento
                       - large: ~3GB, máxima precisión (no recomendado para Render Free)
        """
        self.model_size = model_size
        self.model = None
        self.models_dir = self._get_models_dir()
        
        print(f"[WHISPER] Inicializando FasterWhisperService", file=sys.stderr, flush=True)
        print(f"[WHISPER] Modelo: {model_size}", file=sys.stderr, flush=True)
        print(f"[WHISPER] Directorio de modelos: {self.models_dir}", file=sys.stderr, flush=True)
        
    def _get_models_dir(self) -> Path:
        """
        Obtiene el directorio donde se guardarán los modelos.
        En Render, usa /tmp/whisper_models
        En desarrollo local, usa ./whisper_models
        """
        if os.environ.get('RENDER'):
            # En Render, usar /tmp porque tiene espacio writable
            models_dir = Path("/tmp/whisper_models")
        else:
            # En local, usar directorio del proyecto
            models_dir = Path(settings.BASE_DIR) / "whisper_models"
        
        # Crear directorio si no existe
        models_dir.mkdir(parents=True, exist_ok=True)
        return models_dir
    
    def is_available(self) -> bool:
        """
        Verifica si faster-whisper está disponible.
        """
        return FASTER_WHISPER_AVAILABLE
    
    def load_model(self) -> bool:
        """
        Carga el modelo de Whisper.
        El modelo se descarga automáticamente si no existe.
        
        Returns:
            True si el modelo se cargó exitosamente, False si falló.
        """
        if not FASTER_WHISPER_AVAILABLE:
            print("[WHISPER] ERROR: faster-whisper no está instalado", file=sys.stderr, flush=True)
            return False
        
        if self.model is not None:
            print("[WHISPER] Modelo ya cargado, reutilizando", file=sys.stderr, flush=True)
            return True
        
        try:
            print(f"[WHISPER] Cargando modelo '{self.model_size}'...", file=sys.stderr, flush=True)
            
            # Configuración optimizada para Render Free Tier (CPU)
            self.model = WhisperModel(
                model_size_or_path=self.model_size,
                device="cpu",  # Render Free Tier no tiene GPU
                compute_type="int8",  # Quantización para reducir uso de RAM
                download_root=str(self.models_dir),  # Directorio de descarga
                num_workers=1,  # Evitar sobrecarga en CPU limitado
            )
            
            print(f"[WHISPER] ✅ Modelo '{self.model_size}' cargado exitosamente", file=sys.stderr, flush=True)
            return True
            
        except Exception as e:
            print(f"[WHISPER] ❌ ERROR al cargar modelo: {str(e)}", file=sys.stderr, flush=True)
            traceback.print_exc()
            self.model = None
            return False
    
    def transcribe_audio(self, audio_path: str, language: str = "es") -> Optional[str]:
        """
        Transcribe un archivo de audio a texto.
        
        Args:
            audio_path: Ruta al archivo de audio (wav, mp3, m4a, etc.)
            language: Código de idioma (es, en, ca, etc.)
        
        Returns:
            Texto transcrito o None si falla
        """
        if not self.is_available():
            print("[WHISPER] ERROR: faster-whisper no disponible", file=sys.stderr, flush=True)
            return None
        
        # Cargar modelo si no está cargado
        if self.model is None:
            if not self.load_model():
                print("[WHISPER] ERROR: No se pudo cargar el modelo", file=sys.stderr, flush=True)
                return None
        
        try:
            print(f"[WHISPER] Transcribiendo audio: {audio_path}", file=sys.stderr, flush=True)
            print(f"[WHISPER] Idioma: {language}", file=sys.stderr, flush=True)
            
            # Transcribir con configuración optimizada
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,  # Balance entre velocidad y precisión
                vad_filter=True,  # Filtrar silencio (Voice Activity Detection)
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=100
                )
            )
            
            # Unir todos los segmentos en un solo texto
            transcription = " ".join([segment.text.strip() for segment in segments])
            
            print(f"[WHISPER] ✅ Transcripción completada", file=sys.stderr, flush=True)
            print(f"[WHISPER] Texto ({len(transcription)} caracteres): {transcription[:100]}...", file=sys.stderr, flush=True)
            
            return transcription.strip()
            
        except Exception as e:
            print(f"[WHISPER] ❌ ERROR al transcribir: {str(e)}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()
            return None


# Singleton global
_whisper_service: Optional[FasterWhisperService] = None


def get_whisper_service(model_size: str = "small") -> FasterWhisperService:
    """
    Obtiene la instancia global del servicio de Whisper (singleton).
    
    Args:
        model_size: Tamaño del modelo (por defecto "small")
    
    Returns:
        Instancia de FasterWhisperService
    """
    global _whisper_service
    
    if _whisper_service is None:
        _whisper_service = FasterWhisperService(model_size=model_size)
    
    return _whisper_service


def transcribe_audio(audio_path: str, language: str = "es") -> Optional[str]:
    """
    Función helper para transcribir audio directamente.
    
    Args:
        audio_path: Ruta al archivo de audio
        language: Código de idioma (por defecto "es")
    
    Returns:
        Texto transcrito o None si falla
    """
    service = get_whisper_service()
    return service.transcribe_audio(audio_path, language=language)
