import React, { useState, useEffect } from 'react';
import api from '../../lib/axios';

const WidgetHistorialEvaluaciones = ({ studentId, subjectId, titleClassName, refreshTrigger }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, recent, subject

  useEffect(() => {
    if (studentId) {
      fetchActivities();
    }
  }, [studentId, subjectId, filter, refreshTrigger]);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const params = { student: studentId };

      if (filter === 'subject' && subjectId) {
        params.subject = subjectId;
      }

      if (filter === 'recent') {
        params.limit = 10;
      }

      // Solo obtener evaluaciones y comentarios reales
      const [evaluationsResponse, commentsResponse] = await Promise.allSettled([
        api.get('/evaluations/', { params }),
        api.get('/comments/', { params })
      ]);

      // Extraer datos de manera segura
      const getDataFromResponse = (response) => {
        if (response.status === 'fulfilled') {
          const data = response.value.data.results || response.value.data;
          return Array.isArray(data) ? data : [];
        }
        return [];
      };

      const evaluations = getDataFromResponse(evaluationsResponse);
      const comments = getDataFromResponse(commentsResponse);

      // Combinar solo evaluaciones y comentarios reales
      const combinedActivities = [
        ...evaluations.map(evaluation => ({
          ...evaluation,
          type: 'evaluation',
          date: evaluation.date,
          content: evaluation.comment,
          score: evaluation.score,
          id: `eval-${evaluation.id}`
        })),
        ...comments.map(comment => ({
          ...comment,
          type: 'comment',
          date: comment.created_at,
          content: comment.text,
          score: null,
          id: `comment-${comment.id}`
        }))
      ];

      // Ordenar por fecha (más reciente primero)
      combinedActivities.sort((a, b) => new Date(b.date) - new Date(a.date));

      setActivities(combinedActivities);
    } catch (error) {
      console.error('Error cargando actividades:', error);
      setActivities([]);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score === null) return 'bg-gray-100 text-gray-800'; // For comments
    if (score >= 8) return 'bg-green-100 text-green-800';
    if (score >= 6) return 'bg-blue-100 text-blue-800';
    if (score >= 4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-center py-4">Cargando historial...</div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
        <span className="mr-2">📜</span>
        Historial de Evaluaciones
      </h3>

      <div className="mb-4 flex justify-end">
        <div className="relative">
          <select
            onChange={(e) => setFilter(e.target.value)}
            value={filter}
            className="block appearance-none w-full bg-white border border-gray-300 text-gray-700 py-2 px-4 pr-8 rounded-md leading-tight focus:outline-none focus:bg-white focus:border-blue-500"
          >
            <option value="all">Todas</option>
            <option value="recent">Más recientes</option>
            {subjectId && <option value="subject">De esta asignatura</option>}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
            <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
              <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
            </svg>
          </div>
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {activities.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📜</div>
            <p>No hay evaluaciones o comentarios registrados</p>
            <p className="text-sm">Las evaluaciones y comentarios aparecerán aquí cuando se registren</p>
          </div>
        ) : (
          activities.map(activity => (
            <div key={activity.id} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    {activity.type === 'evaluation' && activity.score !== null && (
                      <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(activity.score)}`}>
                        {activity.score}/10
                      </span>
                    )}
                    {activity.type === 'comment' && (
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        activity.subject 
                          ? 'bg-purple-100 text-purple-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {activity.subject ? '📚' : '💬'} {activity.subject ? 'Comentario de asignatura' : 'Comentario general'}
                      </span>
                    )}
                    <span className="text-sm text-gray-500">
                      {formatDate(activity.date)}
                    </span>
                  </div>

                  {activity.subject && (
                    <p className="text-sm font-medium" style={{ color: '#9333ea' }}>
                      {activity.subject.name || activity.subject_name}
                    </p>
                  )}
                </div>

                {activity.evaluator && (
                  <span className="text-xs text-gray-500">
                    Por: {activity.evaluator.username}
                  </span>
                )}
                {activity.author && (
                  <span className="text-xs text-gray-500">
                    Por: {activity.author.username}
                  </span>
                )}
              </div>

              {activity.content && (
                <p className="text-sm text-gray-700 leading-relaxed mt-2">
                  {activity.content}
                </p>
              )}

              <div className="mt-2 text-xs text-gray-400">
                {activity.type === 'evaluation' ? '📊 Evaluación' : '💬 Comentario rápido'}
              </div>
            </div>
          ))
        )}
      </div>

      {activities.length > 0 && (
        <div className="mt-4 text-xs text-gray-500 text-center">
          💡 Mostrando {activities.length} actividad{activities.length !== 1 ? 'es' : ''} del estudiante
        </div>
      )}
    </div>
  );
};

export default WidgetHistorialEvaluaciones;