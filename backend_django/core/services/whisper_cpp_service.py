"""
Whisper.cpp Service - Local Audio Transcription
================================================
Uses locally compiled whisper.cpp binary for audio transcription.
No external API dependencies - runs entirely on server.
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


class WhisperCppError(Exception):
    """Custom exception for Whisper.cpp related errors"""
    pass


class WhisperCppService:
    """Cliente para transcripción de audio usando Whisper.cpp local"""
    
    def __init__(self):
        self.whisper_path = getattr(settings, 'WHISPER_CPP_PATH', '/opt/whisper.cpp')
        self.model_path = getattr(settings, 'WHISPER_MODEL_PATH', '/opt/whisper.cpp/models/ggml-medium.bin')
        self.timeout = getattr(settings, 'WHISPER_TIMEOUT', 120)
        self.max_file_size = getattr(settings, 'WHISPER_MAX_FILE_SIZE', 25 * 1024 * 1024)
        
        self.executable = os.path.join(self.whisper_path, 'main')
        
        # Validate installation
        if not os.path.exists(self.executable):
            logger.warning(f"⚠️ Whisper.cpp executable not found at: {self.executable}")
        
        if not os.path.exists(self.model_path):
            logger.warning(f"⚠️ Whisper model not found at: {self.model_path}")
    
    def is_available(self):
        """Check if Whisper.cpp is properly installed"""
        return os.path.exists(self.executable) and os.path.exists(self.model_path)
    
    def transcribe_audio(self, audio_file_path, language='es'):
        """
        Transcribe audio file using Whisper.cpp
        
        Args:
            audio_file_path: Path to audio file (.wav, .mp3, .m4a)
            language: ISO language code (default: 'es' for Spanish)
        
        Returns:
            str: Transcribed text
        
        Raises:
            WhisperCppError: If transcription fails
        """
        if not self.is_available():
            raise WhisperCppError(
                "Whisper.cpp no está instalado correctamente. "
                f"Verifica que existan: {self.executable} y {self.model_path}"
            )
        
        # Check file size
        file_size = os.path.getsize(audio_file_path)
        if file_size > self.max_file_size:
            raise WhisperCppError(
                f"Archivo demasiado grande: {file_size / 1024 / 1024:.2f}MB. "
                f"Máximo permitido: {self.max_file_size / 1024 / 1024}MB"
            )
        
        logger.info(f"[WHISPER.CPP] Transcribing audio: {audio_file_path}")
        logger.info(f"[WHISPER.CPP] File size: {file_size} bytes")
        logger.info(f"[WHISPER.CPP] Language: {language}")
        
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_base = os.path.join(tmp_dir, 'output')
            
            try:
                # Build command
                # whisper.cpp generates: output.txt, output.srt, output.vtt
                cmd = [
                    self.executable,
                    '-m', self.model_path,
                    '-f', audio_file_path,
                    '-l', language,
                    '-otxt',  # Generate text output
                    '-of', output_base,  # Output file base name
                    '--no-timestamps',  # Clean text without timestamps
                    '-t', '4',  # Use 4 threads
                ]
                
                logger.info(f"[WHISPER.CPP] Running command: {' '.join(cmd)}")
                
                # Execute whisper.cpp
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False
                )
                
                logger.info(f"[WHISPER.CPP] Return code: {result.returncode}")
                
                if result.returncode != 0:
                    logger.error(f"[WHISPER.CPP] STDERR: {result.stderr}")
                    raise WhisperCppError(
                        f"Whisper.cpp failed with code {result.returncode}: {result.stderr}"
                    )
                
                # Read transcription from output.txt
                output_txt = f"{output_base}.txt"
                
                if not os.path.exists(output_txt):
                    logger.error(f"[WHISPER.CPP] Output file not found: {output_txt}")
                    logger.error(f"[WHISPER.CPP] STDOUT: {result.stdout}")
                    raise WhisperCppError("Transcription file not generated")
                
                with open(output_txt, 'r', encoding='utf-8') as f:
                    transcription = f.read().strip()
                
                logger.info(f"[WHISPER.CPP] Transcription length: {len(transcription)} characters")
                logger.info(f"[WHISPER.CPP] Preview: {transcription[:100]}...")
                
                if not transcription:
                    raise WhisperCppError("Transcription is empty - audio may be silent or too noisy")
                
                return transcription
                
            except subprocess.TimeoutExpired:
                logger.error(f"[WHISPER.CPP] Timeout after {self.timeout}s")
                raise WhisperCppError(
                    f"Transcripción cancelada: excedió el tiempo límite de {self.timeout}s"
                )
            except FileNotFoundError:
                logger.error(f"[WHISPER.CPP] Executable not found: {self.executable}")
                raise WhisperCppError(
                    f"Whisper.cpp no encontrado en: {self.executable}"
                )
            except Exception as e:
                logger.exception("[WHISPER.CPP] Unexpected error during transcription")
                raise WhisperCppError(f"Error inesperado: {str(e)}")


# Singleton instance
_whisper_client = None

def get_whisper_client():
    """Get or create singleton Whisper.cpp client"""
    global _whisper_client
    if _whisper_client is None:
        _whisper_client = WhisperCppService()
    return _whisper_client
