import React, { useState } from 'react';
import api from '../../lib/axios';

const WidgetComentariosRapidos = ({ studentId, subjectId, onCommentCreated, titleClassName }) => {
  const [selectedComments, setSelectedComments] = useState([]);
  const [customComment, setCustomComment] = useState('');
  const [improving, setImproving] = useState(false);
  const [saving, setSaving] = useState(false);

  const quickComments = [
    { id: 1, text: '✅ Buena participación', emoji: '✅' },
    { id: 2, text: '⚠️ Debe concentrarse más', emoji: '⚠️' },
    { id: 3, text: '💡 Excelente trabajo en grupo', emoji: '💡' },
    { id: 4, text: '🎯 Ha comprendido el concepto', emoji: '🎯' },
    { id: 5, text: '📈 Muestra progreso significativo', emoji: '📈' },
    { id: 6, text: '🤝 Colabora bien con compañeros', emoji: '🤝' },
    { id: 7, text: '📚 Demuestra interés por aprender', emoji: '📚' },
    { id: 8, text: '⏰ Necesita mejorar puntualidad', emoji: '⏰' },
    { id: 9, text: '🎨 Creatividad destacable', emoji: '🎨' },
    { id: 10, text: '🔍 Pregunta con curiosidad', emoji: '🔍' },
  ];

  const toggleComment = (comment) => {
    setSelectedComments(prev => {
      const exists = prev.find(c => c.id === comment.id);
      if (exists) {
        return prev.filter(c => c.id !== comment.id);
      } else {
        return [...prev, comment];
      }
    });
  };

  const improveWithAI = async () => {
    const currentText = [
      ...selectedComments.map(c => c.text),
      customComment
    ].filter(Boolean).join('. ');

    if (!currentText.trim()) {
      alert('Selecciona al menos un comentario o escribe uno personalizado');
      return;
    }

    try {
      setImproving(true);
      const response = await api.post('/evaluaciones/mejorar-comentario/', {
        contenido: currentText
      });

      setCustomComment(response.data.comentarioMejorado);
      setSelectedComments([]); // Limpiar selección ya que ahora usamos el mejorado
    } catch (error) {
      console.error('Error mejorando comentario:', error);
      alert('Error al mejorar el comentario con IA');
    } finally {
      setImproving(false);
    }
  };

  const saveFeedback = async () => {
    const finalComment = [
      ...selectedComments.map(c => c.text),
      customComment
    ].filter(Boolean).join('. ');

    if (!finalComment.trim()) {
      alert('Debes seleccionar o escribir al menos un comentario');
      return;
    }

    try {
      setSaving(true);
      const response = await api.post('/evaluaciones/feedback-rapido/', {
        alumnoId: studentId,
        asignaturaId: subjectId,
        contenido: finalComment
      });

      if (onCommentCreated) {
        onCommentCreated(response.data);
      }

      // Limpiar formulario
      setSelectedComments([]);
      setCustomComment('');

      alert('Comentario guardado exitosamente');
    } catch (error) {
      console.error('Error guardando comentario:', error);
      alert('Error al guardar el comentario');
    } finally {
      setSaving(false);
    }
  };

  const getSelectedText = () => {
    return selectedComments.map(c => c.text).join('. ') +
           (selectedComments.length > 0 && customComment ? '. ' : '') +
           customComment;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
        <span className="mr-2">💬</span>
        Comentarios Rápidos / Feedback
      </h3>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Seleccionar comentarios rápidos
        </label>
        <div className="grid grid-cols-2 gap-2">
          {quickComments.map(comment => {
            const isSelected = selectedComments.find(c => c.id === comment.id);
            return (
              <button
                key={comment.id}
                onClick={() => toggleComment(comment)}
                className={`p-2 text-sm rounded-md border transition-colors ${
                  isSelected
                    ? 'bg-blue-100 border-blue-300 text-blue-800'
                    : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {comment.emoji} {comment.text}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Comentario personalizado (opcional)
        </label>
        <textarea
          value={customComment}
          onChange={(e) => setCustomComment(e.target.value)}
          placeholder="Escribe un comentario adicional..."
          className="w-full p-3 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-700 focus:border-blue-700 resize-none text-black bg-white placeholder-gray-500"
          rows={3}
        />
      </div>

      {getSelectedText() && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <h4 className="text-sm font-medium text-blue-800 mb-1">Comentario final:</h4>
          <p className="text-sm text-blue-700">{getSelectedText()}</p>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={improveWithAI}
          disabled={improving || !getSelectedText().trim()}
          className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {improving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Mejorando...
            </>
          ) : (
            <>
              <span className="mr-2">🪄</span>
              Mejorar con IA
            </>
          )}
        </button>

        <button
          onClick={saveFeedback}
          disabled={saving || !getSelectedText().trim()}
          className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {saving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Guardando...
            </>
          ) : (
            <>
              <span className="mr-2">💾</span>
              Guardar
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default WidgetComentariosRapidos;