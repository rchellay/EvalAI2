/**
 * Componente React para mostrar el perfil de un estudiante con filtrado contextual.
 * 
 * Uso:
 * - Desde asignaturas: /estudiantes/:id?asignatura=1 (muestra solo datos de esa asignatura)
 * - Desde grupos: /estudiantes/:id (muestra todos los datos)
 */

import { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';

const StudentProfileContextual = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // Obtener asignatura_id de la URL (si existe)
  const asignaturaId = searchParams.get('asignatura');
  
  const [resumen, setResumen] = useState(null);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [comentarios, setComentarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('resumen');
  
  // Estado para crear nuevo comentario
  const [nuevoComentario, setNuevoComentario] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Estado para evaluación
  const [showEvaluationForm, setShowEvaluationForm] = useState(false);
  const [evaluationData, setEvaluationData] = useState({ score: '', comment: '' });
  const [currentEvaluation, setCurrentEvaluation] = useState(null);

  // Estado para información de asignatura
  const [subjectInfo, setSubjectInfo] = useState(null);

  useEffect(() => {
    loadStudentData();
  }, [id, asignaturaId]);

  useEffect(() => {
    if (asignaturaId) {
      api.get(`/subjects/${asignaturaId}/`).then(res => setSubjectInfo(res.data));
    }
  }, [asignaturaId]);

  const loadStudentData = async () => {
    try {
      setLoading(true);
      
      // Cargar información básica del estudiante
      const studentResponse = await api.get(`/students/${id}/`);
      setResumen({
        estudiante: studentResponse.data,
        grupos: [], // TODO: cargar grupos del estudiante
        asignaturas: [], // TODO: cargar asignaturas del estudiante
        estadisticas: { filtrado_por_asignatura: !!asignaturaId },
        ultimos_comentarios: []
      });
      
      // Cargar evaluaciones usando la nueva API
      const evaluationsParams = asignaturaId ? { subject_id: asignaturaId } : {};
      const evaluationsResponse = await api.get(`/alumnos/${id}/evaluaciones/`, { 
        params: evaluationsParams 
      });
      
      // Transformar las evaluaciones al formato esperado por el componente
      let transformedEvaluations = [];
      if (Array.isArray(evaluationsResponse.data)) {
        transformedEvaluations = evaluationsResponse.data.map(evaluation => ({
          id: evaluation.id,
          rubric: evaluation.subject_name || 'Evaluación general',
          subject: evaluation.subject_name || 'General',
          evaluator: evaluation.evaluator_name || 'Profesor',
          evaluated_at: evaluation.date,
          porcentaje: evaluation.score ? Math.round((evaluation.score / 10) * 100) : 0,
          total_score: evaluation.score || 0,
          max_possible: 10,
          criterios: [] // Las evaluaciones simples no tienen criterios detallados
        }));
      } else {
        console.warn('Evaluations API returned non-array data:', evaluationsResponse.data);
      }
      
      setEvaluaciones(transformedEvaluations);
      
      // Cargar comentarios usando la nueva API
      let apiComments = [];
      try {
        const commentsParams = asignaturaId ? { asignatura: asignaturaId } : {};
        const commentsResponse = await api.get(`/estudiantes/${id}/comentarios/`, { 
          params: commentsParams 
        });
        
        if (commentsResponse.data && Array.isArray(commentsResponse.data.comentarios)) {
          apiComments = commentsResponse.data.comentarios;
        } else {
          console.warn('Comments API returned unexpected format:', commentsResponse.data);
        }
      } catch (commentsError) {
        console.warn('Error loading comments:', commentsError);
        // Continue without comments if API fails
      }
      
      // Agregar comentarios de evaluaciones como comentarios adicionales
      let evaluationComments = [];
      if (Array.isArray(evaluationsResponse.data)) {
        evaluationComments = evaluationsResponse.data
          .filter(evaluation => evaluation.comment && evaluation.comment.trim())
          .map(evaluation => ({
            id: `eval_${evaluation.id}`,
            text: evaluation.comment,
            author: evaluation.evaluator_name || 'Profesor',
            subject: evaluation.subject_name || 'Evaluación',
            subject_id: evaluation.subject_id,
            created_at: evaluation.date
          }));
      }
      
      // Combinar comentarios de la API con comentarios de evaluaciones
      const allComments = [...apiComments, ...evaluationComments];
      
      setComentarios(allComments);
      
    } catch (error) {
      console.error('Error loading student data:', error);
      toast.error('Error al cargar los datos del estudiante');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateComentario = async (e) => {
    e.preventDefault();
    
    if (!nuevoComentario.trim()) {
      toast.error('El comentario no puede estar vacío');
      return;
    }

    try {
      setSubmitting(true);
      
      // Usar la nueva API para crear evaluaciones con comentarios
      const payload = {
        student: id,
        subject: asignaturaId || null,
        date: new Date().toISOString().split('T')[0],
        score: null, // Solo comentario, sin calificación
        comment: nuevoComentario.trim()
      };
      
      await api.post(`/alumnos/${id}/evaluaciones/`, payload);
      
      toast.success('Comentario creado exitosamente');
      setNuevoComentario('');
      
      // Recargar evaluaciones
      const evaluationsParams = asignaturaId ? { subject_id: asignaturaId } : {};
      const evaluationsResponse = await api.get(`/alumnos/${id}/evaluaciones/`, { 
        params: evaluationsParams 
      });
      
      const transformedEvaluations = evaluationsResponse.data.map(evaluation => ({
        id: evaluation.id,
        rubric: evaluation.subject_name || 'Comentario',
        subject: evaluation.subject_name || 'General',
        evaluator: evaluation.evaluator_name || 'Profesor',
        evaluated_at: evaluation.date,
        porcentaje: evaluation.score ? Math.round((evaluation.score / 10) * 100) : 0,
        total_score: evaluation.score || 0,
        max_possible: 10,
        criterios: []
      }));
      
      setEvaluaciones(transformedEvaluations);
      
    } catch (error) {
      console.error('Error creating comment:', error);
      toast.error('Error al crear el comentario');
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenEvaluationForm = (evaluation = null) => {
    if (evaluation) {
      setCurrentEvaluation(evaluation);
      setEvaluationData({
        score: evaluation.total_score || '',
        comment: evaluation.comment || ''
      });
    } else {
      setCurrentEvaluation(null);
      setEvaluationData({ score: '', comment: '' });
    }
    setShowEvaluationForm(true);
  };

  const handleSaveEvaluation = async () => {
    try {
      const payload = {
        student: id,
        subject: asignaturaId || null,
        date: new Date().toISOString().split('T')[0],
        score: evaluationData.score ? parseFloat(evaluationData.score) : null,
        comment: evaluationData.comment
      };

      if (currentEvaluation) {
        // Actualizar evaluación existente
        await api.put(`/alumnos/${id}/evaluaciones/${currentEvaluation.id}/`, payload);
        toast.success('Evaluación actualizada correctamente');
      } else {
        // Crear nueva evaluación
        await api.post(`/alumnos/${id}/evaluaciones/`, payload);
        toast.success('Evaluación guardada correctamente');
      }

      setShowEvaluationForm(false);
      setCurrentEvaluation(null);
      setEvaluationData({ score: '', comment: '' });

      // Recargar evaluaciones
      const evaluationsParams = asignaturaId ? { subject_id: asignaturaId } : {};
      const evaluationsResponse = await api.get(`/alumnos/${id}/evaluaciones/`, { 
        params: evaluationsParams 
      });
      
      const transformedEvaluations = evaluationsResponse.data.map(evaluation => ({
        id: evaluation.id,
        rubric: evaluation.subject_name || 'Evaluación general',
        subject: evaluation.subject_name || 'General',
        evaluator: evaluation.evaluator_name || 'Profesor',
        evaluated_at: evaluation.date,
        porcentaje: evaluation.score ? Math.round((evaluation.score / 10) * 100) : 0,
        total_score: evaluation.score || 0,
        max_possible: 10,
        criterios: []
      }));
      
      setEvaluaciones(transformedEvaluations);

    } catch (error) {
      console.error('Error saving evaluation:', error);
      toast.error('Error al guardar la evaluación');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!resumen) {
    return <div className="p-8 text-red-600">Estudiante no encontrado</div>;
  }

  const { estudiante, grupos, asignaturas, estadisticas, ultimos_comentarios } = resumen;
  const estaFiltrado = estadisticas.filtrado_por_asignatura;

  return (
    <div className="flex-1 p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        
        {/* Breadcrumb con contexto */}
        <nav className="mb-6 text-sm flex items-center gap-2">
          {estaFiltrado ? (
            <>
              <button
                onClick={() => navigate('/asignaturas')}
                className="text-primary hover:underline"
              >
                Asignaturas
              </button>
              <span className="text-gray-500">/</span>
              <button
                onClick={() => navigate(`/asignaturas/${asignaturaId}`)}
                className="text-primary hover:underline"
              >
                {subjectInfo?.name || 'Asignatura'}
              </button>
              <span className="text-gray-500">/</span>
              <span className="text-gray-900 dark:text-white font-medium">
                {estudiante.name}
              </span>
            </>
          ) : (
            <>
              <button
                onClick={() => navigate('/estudiantes')}
                className="text-primary hover:underline"
              >
                Estudiantes
              </button>
              <span className="text-gray-500">/</span>
              <span className="text-gray-900 dark:text-white font-medium">
                {estudiante.name}
              </span>
            </>
          )}
        </nav>

        {/* Header con badge de contexto */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-3xl font-bold">
              {estudiante.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                {estudiante.name}
              </h1>
              <p className="text-gray-500 dark:text-gray-400">{estudiante.email}</p>
              <p className="text-gray-500 dark:text-gray-400">{estudiante.course}</p>
            </div>
          </div>
          
          {/* Badge indicando el contexto */}
          {estaFiltrado && (
            <div className="px-4 py-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg border-2 border-purple-500">
              <p className="text-sm text-purple-700 dark:text-purple-300 font-medium">
                📚 Vista filtrada por asignatura
              </p>
              <p className="text-xs text-purple-600 dark:text-purple-400">
                {subjectInfo?.name}
              </p>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-card-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Grupos</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {grupos.length}
            </p>
          </div>
          <div className="bg-white dark:bg-card-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Asignaturas</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {asignaturas.length}
            </p>
          </div>
          <div className="bg-white dark:bg-card-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              {estaFiltrado ? 'Evaluaciones (filtradas)' : 'Total Evaluaciones'}
            </p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {evaluaciones.length}
            </p>
          </div>
          <div className="bg-white dark:bg-card-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Promedio</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {evaluaciones.length > 0 
                ? Math.round(evaluaciones.reduce((sum, evaluation) => sum + evaluation.porcentaje, 0) / evaluaciones.length)
                : 0
              }%
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-card-dark rounded-xl border border-gray-200 dark:border-gray-800">
          <div className="border-b border-gray-200 dark:border-gray-800">
            <nav className="flex gap-4 px-6">
              {['resumen', 'evaluaciones', 'comentarios'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-2 border-b-2 font-medium text-sm transition ${
                    activeTab === tab
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Tab: Resumen */}
            {activeTab === 'resumen' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Grupos
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {grupos.map((grupo) => (
                      <span
                        key={grupo.id}
                        className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm"
                      >
                        {grupo.name}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Asignaturas
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {asignaturas.map((asignatura) => (
                      <span
                        key={asignatura.id}
                        className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-sm"
                      >
                        {asignatura.name}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Últimos Comentarios
                  </h3>
                  {ultimos_comentarios.length === 0 ? (
                    <p className="text-gray-500 text-sm">No hay comentarios recientes</p>
                  ) : (
                    <div className="space-y-3">
                      {ultimos_comentarios.map((comentario) => (
                        <div
                          key={comentario.id}
                          className="border-l-4 border-blue-500 pl-4 py-2 bg-gray-50 dark:bg-gray-800/50"
                        >
                          <p className="text-gray-800 dark:text-gray-200">{comentario.text}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {comentario.author} • {comentario.subject} • 
                            {new Date(comentario.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tab: Evaluaciones */}
            {activeTab === 'evaluaciones' && (
              <div className="space-y-4">
                {evaluaciones.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    {estaFiltrado 
                      ? 'No hay evaluaciones en esta asignatura' 
                      : 'No hay evaluaciones registradas'
                    }
                  </p>
                ) : (
                  <div className="space-y-4">
                    {evaluaciones.map((evaluacion) => (
                      <div
                        key={evaluacion.id}
                        className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition"
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 dark:text-white">
                              {evaluacion.rubric}
                            </h4>
                            <p className="text-sm text-gray-500">
                              {evaluacion.subject} • {evaluacion.evaluator}
                            </p>
                            <p className="text-xs text-gray-400">
                              {new Date(evaluacion.evaluated_at).toLocaleString()}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {evaluacion.porcentaje > 0 && (
                              <div className="text-right mr-4">
                                <p className="text-2xl font-bold text-primary">
                                  {evaluacion.porcentaje}%
                                </p>
                                <p className="text-sm text-gray-500">
                                  {evaluacion.total_score}/{evaluacion.max_possible}
                                </p>
                              </div>
                            )}
                            <button
                              onClick={() => handleOpenEvaluationForm(evaluacion)}
                              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                            >
                              Editar
                            </button>
                          </div>
                        </div>

                        {evaluacion.comment && (
                          <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded">
                            <p className="text-sm text-gray-700 dark:text-gray-300">
                              <strong>Comentario:</strong> {evaluacion.comment}
                            </p>
                          </div>
                        )}

                        <div className="space-y-2">
                          {evaluacion.criterios.map((criterio, idx) => (
                            <div key={idx} className="flex justify-between text-sm">
                              <span className="text-gray-700 dark:text-gray-300">
                                {criterio.criterio}: {criterio.nivel}
                              </span>
                              <span className="text-gray-500">
                                {criterio.puntos} pts ({criterio.peso}%)
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Botón para nueva evaluación */}
                <div className="mt-6">
                  <button
                    onClick={() => handleOpenEvaluationForm()}
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition flex items-center gap-2"
                  >
                    <span className="material-symbols-outlined text-sm">add</span>
                    Nueva Evaluación
                  </button>
                </div>
              </div>
            )}

            {/* Tab: Comentarios */}
            {activeTab === 'comentarios' && (
              <div className="space-y-6">
                {/* Formulario para nuevo comentario */}
                <form onSubmit={handleCreateComentario} className="border-b border-gray-200 dark:border-gray-700 pb-6 mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Agregar Comentario
                  </h3>
                  <textarea
                    value={nuevoComentario}
                    onChange={(e) => setNuevoComentario(e.target.value)}
                    placeholder="Escribe tu comentario aquí..."
                    rows={3}
                    className="w-full px-4 py-2 bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-lg placeholder-gray-400 focus:ring-2 focus:ring-primary focus:outline-none"
                  />
                  {estaFiltrado && (
                    <p className="text-xs text-gray-500 mt-2">
                      Este comentario se asociará a:{' '}
                      <span className="font-medium text-primary">
                        {asignaturas.find(a => a.id === parseInt(asignaturaId))?.name}
                      </span>
                    </p>
                  )}
                  <button
                    type="submit"
                    disabled={submitting || !nuevoComentario.trim()}
                    className="mt-3 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? 'Guardando...' : 'Guardar Comentario'}
                  </button>
                </form>

                {/* Lista de comentarios */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Historial de Comentarios
                  </h3>
                  {comentarios.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">
                      {estaFiltrado 
                        ? 'No hay comentarios en esta asignatura' 
                        : 'No hay comentarios registrados'
                      }
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {comentarios.map((comentario) => (
                        <div
                          key={comentario.id}
                          className="border-l-4 border-green-500 pl-4 py-3 bg-gray-50 dark:bg-gray-800/50 rounded-r-lg"
                        >
                          <p className="text-gray-800 dark:text-gray-200 mb-2">
                            {comentario.text}
                          </p>
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>
                              {comentario.author} • {comentario.subject}
                            </span>
                            <span>
                              {new Date(comentario.created_at).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal de evaluación */}
      {showEvaluationForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              {currentEvaluation ? 'Editar Evaluación' : 'Nueva Evaluación'}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Calificación (0-10)
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  step="0.1"
                  value={evaluationData.score}
                  onChange={(e) => setEvaluationData(prev => ({ ...prev, score: e.target.value }))}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  placeholder="Ej: 8.5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Comentarios
                </label>
                <textarea
                  value={evaluationData.comment}
                  onChange={(e) => setEvaluationData(prev => ({ ...prev, comment: e.target.value }))}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  rows="3"
                  placeholder="Comentarios sobre el desempeño..."
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowEvaluationForm(false);
                  setCurrentEvaluation(null);
                  setEvaluationData({ score: '', comment: '' });
                }}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveEvaluation}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
              >
                {currentEvaluation ? 'Actualizar' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentProfileContextual;
