import React, { useState, useEffect } from 'react';
import api from '../../lib/axios';

const WidgetAutoevaluacion = ({ studentId, subjectId, onSelfEvaluationCreated, titleClassName }) => {
  const [selfEvaluations, setSelfEvaluations] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    score: 3,
    comment: '',
    evaluation_type: 'autoevaluacion'
  });
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  // Cargar autoevaluaciones existentes
  useEffect(() => {
    fetchSelfEvaluations();
  }, [studentId, subjectId]);

  const fetchSelfEvaluations = async () => {
    try {
      setLoading(true);
      const params = { student: studentId };
      if (subjectId) params.subject = subjectId;

      const response = await api.get('/self-evaluations/', { params });
      setSelfEvaluations(response.data);
    } catch (error) {
      console.error('Error cargando autoevaluaciones:', error);
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
      alert('Debes escribir un comentario para tu autoevaluación');
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

      alert('Autoevaluación guardada exitosamente');
    } catch (error) {
      console.error('Error guardando autoevaluación:', error);
      alert('Error al guardar la autoevaluación');
    } finally {
      setSaving(false);
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
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white py-1 px-3 rounded-md hover:bg-blue-700 text-sm"
        >
          {showForm ? 'Cancelar' : '+ Evaluarme'}
        </button>
      </div>

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
                <span className="text-xs text-gray-500 capitalize">
                  {evaluation.evaluation_type === 'autoevaluacion' ? 'Autoevaluación' : 'Coevaluación'}
                </span>
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