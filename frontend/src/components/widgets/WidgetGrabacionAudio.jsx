import React, { useState, useRef } from 'react';
import api from '../../lib/axios';

const WidgetGrabacionAudio = ({ studentId, subjectId, onAudioSaved, titleClassName }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [saving, setSaving] = useState(false);
  const [transcribing, setTranscribing] = useState(false);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error al iniciar grabación:', error);
      alert('Error al acceder al micrófono. Asegúrate de tener permisos.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      // Detener el stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    }
  };

  const transcribeAudio = async () => {
    if (!audioBlob) return;

    try {
      setTranscribing(true);

      // Crear FormData para enviar el archivo de audio al backend
      const formData = new FormData();
      formData.append('audio', audioBlob, 'grabacion.wav');
      formData.append('alumnoId', studentId);
      if (subjectId) {
        formData.append('asignaturaId', subjectId);
      }

      // Enviar al backend para transcripción con Whisper
      const response = await api.post('/evaluaciones/audio/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.transcription) {
        setTranscription(response.data.transcription);
      }

      setTranscribing(false);

    } catch (error) {
      console.error('Error transcribiendo audio:', error);
      const errorMessage = error.response?.data?.error || 'Error al transcribir el audio. Verifica tu conexión a internet y la configuración de la API.';
      alert(errorMessage);
      setTranscribing(false);
    }
  };

  const saveAudio = async () => {
    if (!audioBlob) return;

    try {
      setSaving(true);

      // Si no hay transcripción, hacerla primero junto con el guardado
      let formData = new FormData();
      formData.append('audio', audioBlob, 'grabacion.wav');
      formData.append('alumnoId', studentId);
      if (subjectId) {
        formData.append('asignaturaId', subjectId);
      }

      const response = await api.post('/evaluaciones/audio/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Actualizar transcripción si se recibió del backend
      if (response.data.transcription && !transcription) {
        setTranscription(response.data.transcription);
      }

      if (onAudioSaved) {
        onAudioSaved(response.data);
      }

      // Limpiar estado
      setAudioBlob(null);
      setAudioUrl(null);
      setTranscription('');
      setIsRecording(false);

      alert('Audio procesado y guardado exitosamente');
    } catch (error) {
      console.error('Error guardando audio:', error);
      const errorMessage = error.response?.data?.error || 'Error al procesar el audio. Verifica tu conexión y configuración de APIs.';
      alert(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const resetRecording = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setTranscription('');
    setIsRecording(false);

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
        <span className="mr-2">�</span>
        Grabación de Audio
      </h3>

      <div className="text-center mb-6">
        {!audioBlob ? (
          <div>
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="bg-red-600 text-white py-3 px-6 rounded-full hover:bg-red-700 flex items-center justify-center mx-auto"
              >
                <span className="text-2xl mr-2">▶️</span>
                Grabar
              </button>
            ) : (
              <div>
                <div className="flex items-center justify-center mb-4">
                  <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse mr-2"></div>
                  <span className="text-red-600 font-medium">Grabando...</span>
                </div>
                <button
                  onClick={stopRecording}
                  className="bg-gray-600 text-white py-3 px-6 rounded-full hover:bg-gray-700 flex items-center justify-center mx-auto"
                >
                  <span className="text-2xl mr-2">⏹️</span>
                  Detener
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Audio grabado</h4>
              <audio controls className="w-full">
                <source src={audioUrl} type="audio/wav" />
                Tu navegador no soporta el elemento audio.
              </audio>
            </div>

            {!transcription ? (
              <div className="space-y-2">
                <button
                  onClick={transcribeAudio}
                  disabled={transcribing}
                  className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto"
                >
                  {transcribing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Transcribiendo...
                    </>
                  ) : (
                    <>
                      <span className="mr-2">🎙️</span>
                      Solo Transcribir
                    </>
                  )}
                </button>

                <button
                  onClick={saveAudio}
                  disabled={saving}
                  className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Procesando...
                    </>
                  ) : (
                    <>
                      <span className="mr-2">🤖</span>
                      Procesar con IA y Guardar
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Transcripción:</h4>
                  <p className="text-sm text-blue-800">{transcription}</p>
                </div>

                <button
                  onClick={saveAudio}
                  disabled={saving}
                  className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Guardando...
                    </>
                  ) : (
                    <>
                      <span className="mr-2">💾</span>
                      Guardar Evaluación
                    </>
                  )}
                </button>
              </div>
            )}

            <button
              onClick={resetRecording}
              className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 flex items-center justify-center mx-auto"
            >
              <span className="mr-2">🔄</span>
              Nueva Grabación
            </button>
          </div>
        )}
      </div>

      <div className="text-xs text-gray-500 text-center">
        💡 El audio se transcribirá automáticamente usando IA para generar evaluaciones detalladas.
      </div>
    </div>
  );
};

export default WidgetGrabacionAudio;