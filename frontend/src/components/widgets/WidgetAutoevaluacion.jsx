import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../../lib/axios';

const WidgetAutoevaluacion = ({ studentId, subjectId, onSelfEvaluationCreated, titleClassName }) => {
  const [selfEvaluations, setSelfEvaluations] = useState([]);
  const [customEvaluations, setCustomEvaluations] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  const [loading, setLoading] = useState(true);

  // Cargar autoevaluaciones existentes y evaluaciones personalizadas disponibles
  useEffect(() => {
    fetchSelfEvaluations();
    fetchCustomEvaluations();
  }, [studentId, subjectId]);

  const fetchCustomEvaluations = async () => {
    try {
      const response = await api.get(`/custom-evaluations/for-student/${studentId}/`);
      setCustomEvaluations(response.data || []);
    } catch (error) {
      console.error('Error cargando evaluaciones personalizadas:', error);
      setCustomEvaluations([]);
    }
  };

  const fetchSelfEvaluations = async () => {
    try {
      setLoading(true);
      const params = { student: studentId };
      if (subjectId) params.subject = subjectId;

      const response = await api.get('/self-evaluations/', { params });
      // Asegurar que siempre sea un array
      const data = response.data;
      const evaluations = Array.isArray(data) ? data : (data.results ? data.results : []);
      setSelfEvaluations(evaluations);
    } catch (error) {
      console.error('Error cargando autoevaluaciones:', error);
      setSelfEvaluations([]); // Asegurar array vacío en caso de error
    } finally {
      setLoading(false);
    }
  };

  const handleScoreChange = (score) => {
    setFormData(prev => ({
      ...prev,
      score: score
    }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const saveSelfEvaluation = async () => {
    if (!formData.comment.trim()) {
      toast.error('Debes escribir un comentario para tu autoevaluación');
      return;
    }

    try {
      setSaving(true);
      const evaluationData = {
        ...formData,
        student: studentId,
        subject: subjectId || null
      };

      const response = await api.post('/self-evaluations/', evaluationData);

      setSelfEvaluations(prev => [response.data, ...(prev || [])]);
      setFormData({
        score: 3,
        comment: '',
        evaluation_type: 'autoevaluacion'
      });
      setShowForm(false);

      if (onSelfEvaluationCreated) {
        onSelfEvaluationCreated(response.data);
      }

      toast.success('Autoevaluación guardada exitosamente');
    } catch (error) {
      console.error('Error guardando autoevaluación:', error);
      toast.error('Error al guardar la autoevaluación');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (evaluationId) => {
    if (!window.confirm('¿Estás seguro de eliminar esta autoevaluación?')) {
      return;
    }

    try {
      setDeletingId(evaluationId);
      await api.delete(`/self-evaluations/${evaluationId}/`);
      setSelfEvaluations(prev => prev.filter(ev => ev.id !== evaluationId));
      toast.success('Autoevaluación eliminada');
    } catch (error) {
      console.error('Error eliminando autoevaluación:', error);
      toast.error('Error al eliminar. Inténtalo de nuevo.');
    } finally {
      setDeletingId(null);
    }
  };

  const getScoreEmoji = (score) => {
    switch (score) {
      case 1: return '😞';
      case 2: return '😐';
      case 3: return '🙂';
      case 4: return '😊';
      case 5: return '😄';
      default: return '❓';
    }
  };

  const getScoreText = (score) => {
    switch (score) {
      case 1: return 'Muy bajo';
      case 2: return 'Bajo';
      case 3: return 'Regular';
      case 4: return 'Bueno';
      case 5: return 'Excelente';
      default: return 'Sin calificar';
    }
  };

  const getScoreColor = (score) => {
    switch (score) {
      case 1: return 'text-red-600 bg-red-100';
      case 2: return 'text-orange-600 bg-orange-100';
      case 3: return 'text-yellow-600 bg-yellow-100';
      case 4: return 'text-blue-600 bg-blue-100';
      case 5: return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-center py-4">Cargando autoevaluaciones...</div>
      </div>
    );
  }

  // Ensure selfEvaluations is always treated as an array
  const safeSelfEvaluations = Array.isArray(selfEvaluations) ? selfEvaluations : [];

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold flex items-center"}>
          <span className="mr-2">🧠</span>
          Autoevaluación
        </h3>
        <a
          href={`/teacher/evaluations/new?studentId=${studentId}`}
          className="bg-blue-600 text-white py-1 px-3 rounded-md hover:bg-blue-700 text-sm inline-block"
        >
          + Crear Autoevaluación
        </a>
      </div>

      {/* FORMULARIO SIMPLE OCULTO - Ya no se usa
      {showForm && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium mb-3">Mi Autoevaluación</h4>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ¿Cómo calificarías tu desempeño? (1-5)
              </label>
              <div className="flex justify-center space-x-2">
                {[1, 2, 3, 4, 5].map(score => (
                  <button
                    key={score}
                    onClick={() => handleScoreChange(score)}
                    className={`w-12 h-12 rounded-full border-2 flex items-center justify-center text-xl transition-all ${
                      formData.score === score
                        ? 'border-blue-500 bg-blue-100'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {getScoreEmoji(score)}
                  </button>
                ))}
              </div>
              <p className="text-center text-sm text-gray-600 mt-2">
                {getScoreText(formData.score)}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comentario *
              </label>
                  <textarea
                    name="comment"
                    value={formData.comment}
                    onChange={handleInputChange}
                    placeholder="Escribe tu comentario sobre tu desempeño..."
                    className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black bg-white placeholder-gray-500"
                    rows={2}
              />
            </div>

            <button
              onClick={saveSelfEvaluation}
              disabled={saving || !formData.comment.trim()}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Guardando...
                </>
              ) : (
                '💾 Guardar Autoevaluación'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Autoevaluaciones personalizadas disponibles */}
      {customEvaluations.length > 0 && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-3 flex items-center">
            <span className="mr-2">📝</span>
            Autoevaluaciones Disponibles
          </h4>
          <div className="space-y-2">
            {customEvaluations.map(evaluation => (
              <div key={evaluation.id} className="bg-white rounded-lg p-3 border border-blue-200">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900">{evaluation.title}</h5>
                    {evaluation.description && (
                      <p className="text-sm text-gray-600 mt-1">{evaluation.description}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      Creada por: {evaluation.teacher_name}
                    </p>
                  </div>
                  {evaluation.has_responded && (
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full ml-2">
                      ✓ Respondida
                    </span>
                  )}
                </div>
                <a
                  href={evaluation.qr_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-block w-full text-center py-2 px-4 rounded-md text-sm font-medium transition ${
                    evaluation.has_responded && !evaluation.allow_multiple_attempts
                      ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                  onClick={(e) => {
                    if (evaluation.has_responded && !evaluation.allow_multiple_attempts) {
                      e.preventDefault();
                    }
                  }}
                >
                  {evaluation.has_responded && !evaluation.allow_multiple_attempts
                    ? '✓ Ya respondida'
                    : '📝 Responder Autoevaluación'}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-3">
        {safeSelfEvaluations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🧠</div>
            <p>No hay autoevaluaciones aún</p>
            <p className="text-sm">Haz clic en "+ Evaluarme" para realizar tu primera autoevaluación</p>
          </div>
        ) : (
          safeSelfEvaluations.map(evaluation => (
            <div key={evaluation.id} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{getScoreEmoji(evaluation.score)}</span>
                  <div>
                    <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(evaluation.score)}`}>
                      {evaluation.score}/5 - {getScoreText(evaluation.score)}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(evaluation.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 capitalize">
                    {evaluation.evaluation_type === 'autoevaluacion' ? 'Autoevaluación' : 'Coevaluación'}
                  </span>
                  <button
                    onClick={() => handleDelete(evaluation.id)}
                    disabled={deletingId === evaluation.id}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
                    title="Eliminar autoevaluación"
                  >
                    {deletingId === evaluation.id ? (
                      <div className="animate-spin h-4 w-4 border-2 border-red-600 border-t-transparent rounded-full"></div>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <p className="text-sm text-gray-700 leading-relaxed">
                {evaluation.comment}
              </p>
            </div>
          ))
        )}
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        🤔 La autoevaluación ayuda a desarrollar la metacognición y el aprendizaje autónomo.
      </div>
    </div>
  );
};

export default WidgetAutoevaluacion;