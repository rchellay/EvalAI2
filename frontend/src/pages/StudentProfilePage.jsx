// frontend/src/pages/StudentProfilePage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';
import AddCommentModal from '../components/modals/AddCommentModal';
import AddEvaluationModal from '../components/modals/AddEvaluationModal';
import AddAttendanceModal from '../components/modals/AddAttendanceModal';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const StudentProfilePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  // Contexto de asignatura (para navegación desde asignaturas/grupos)
  const asignaturaId = searchParams.get('asignatura');
  const selectedDate = searchParams.get('fecha');
  
  const [profile, setProfile] = useState(null);
  const [attendances, setAttendances] = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [comments, setComments] = useState([]);
  const [subjectAverages, setSubjectAverages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Modal states
  const [showCommentModal, setShowCommentModal] = useState(false);
  const [showEvaluationModal, setShowEvaluationModal] = useState(false);
  const [showAttendanceModal, setShowAttendanceModal] = useState(false);
  
  // Estados para contexto de asignatura (evaluaciones contextuales)
  const [resumen, setResumen] = useState(null);
  const [contextEvaluations, setContextEvaluations] = useState([]);
  const [contextComments, setContextComments] = useState([]);
  const [subjectInfo, setSubjectInfo] = useState(null);
  
  // Estado para evaluación contextual
  const [showContextEvaluationForm, setShowContextEvaluationForm] = useState(false);
  const [contextEvaluationData, setContextEvaluationData] = useState({ score: '', comment: '' });
  const [currentContextEvaluation, setCurrentContextEvaluation] = useState(null);
  
  // Form states
  const [commentForm, setCommentForm] = useState({
    content: '',
    comment_type: 'general',
    subject_id: null
  });
  const [evaluationForm, setEvaluationForm] = useState({
    subject_id: null,
    title: '',
    grade: '',
    max_grade: 10,
    mood: 'neutral',
    date: new Date().toISOString().split('T')[0],
    evaluation_type: 'exam',
    notes: ''
  });
  const [attendanceForm, setAttendanceForm] = useState({
    subject_id: null,
    date: new Date().toISOString().split('T')[0],
    status: 'present',
    notes: ''
  });
  
  const [subjects, setSubjects] = useState([]);
  const [isRecording, setIsRecording] = useState(false);

  useEffect(() => {
    loadStudentData();
    loadSubjects();
  }, [id]);

  // Cargar datos contextuales cuando hay asignaturaId
  useEffect(() => {
    if (asignaturaId) {
      loadContextData();
      // Cargar información de la asignatura
      api.get(`/subjects/${asignaturaId}/`).then(res => setSubjectInfo(res.data));
    }
  }, [id, asignaturaId]);

  const loadStudentData = async () => {
    try {
      setLoading(true);
      
      // Cargar datos básicos del estudiante
      const profileRes = await api.get(`/students/${id}/`);
      setProfile(profileRes.data);
      
      // Intentar cargar datos adicionales (pueden no existir aún)
      // TODO: Implementar endpoint GET para asistencia
      // try {
      //   const attendanceRes = await api.get(`/students/${id}/attendance`);
      //   setAttendances(Array.isArray(attendanceRes.data) ? attendanceRes.data : []);
      // } catch (err) {
      //   console.log('No attendance data available');
      //   setAttendances([]);
      // }
      
      try {
        const evaluationsRes = await api.get(`/alumnos/${id}/evaluaciones/`);
        const evaluationsData = evaluationsRes.data.results || evaluationsRes.data;
        setEvaluations(Array.isArray(evaluationsData) ? evaluationsData : []);
      } catch (err) {
        console.log('No evaluations data available');
        setEvaluations([]);
      }
      
      try {
        const commentsRes = await api.get(`/estudiantes/${id}/comentarios/`);
        const commentsData = commentsRes.data.comentarios || commentsRes.data;
        setComments(Array.isArray(commentsData) ? commentsData : []);
      } catch (err) {
        console.log('No comments data available');
        setComments([]);
      }
      
      // TODO: Implementar endpoint para promedios por asignatura
      // try {
      //   const averagesRes = await api.get(`/students/${id}/evaluations/by-subject`);
      //   setSubjectAverages(Array.isArray(averagesRes.data) ? averagesRes.data : []);
      // } catch (err) {
      //   console.log('No subject averages available');
      //   setSubjectAverages([]);
      // }
      
    } catch (error) {
      console.error('Error loading student data:', error);
      toast.error('Error al cargar datos del estudiante');
      // Navegar de vuelta si el estudiante no existe
      setTimeout(() => navigate('/estudiantes'), 2000);
    } finally {
      setLoading(false);
    }
  };

  const loadContextData = async () => {
    try {
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
      
      setContextEvaluations(transformedEvaluations);
      
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
      
      setContextComments(allComments);
      
    } catch (error) {
      console.error('Error loading context data:', error);
      toast.error('Error al cargar los datos contextuales');
    }
  };

  const loadSubjects = async () => {
    try {
      const res = await api.get('/subjects/');
      const subjectsData = res.data.results || res.data;
      setSubjects(subjectsData);
    } catch (error) {
      console.error('Error loading subjects:', error);
    }
  };

  const handleCreateComment = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/students/${id}/comments`, commentForm);
      toast.success('Comentario añadido correctamente');
      setShowCommentModal(false);
      setCommentForm({ content: '', comment_type: 'general', subject_id: null });
      loadStudentData();
    } catch (error) {
      console.error('Error creating comment:', error);
      toast.error('Error al crear comentario');
    }
  };

  const handleCreateEvaluation = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/students/${id}/evaluations`, evaluationForm);
      toast.success('Evaluación añadida correctamente');
      setShowEvaluationModal(false);
      setEvaluationForm({
        subject_id: null,
        title: '',
        grade: '',
        max_grade: 10,
        mood: 'neutral',
        date: new Date().toISOString().split('T')[0],
        evaluation_type: 'exam',
        notes: ''
      });
      loadStudentData();
    } catch (error) {
      console.error('Error creating evaluation:', error);
      toast.error('Error al crear evaluación');
    }
  };

  const handleCreateAttendance = async (e) => {
    e.preventDefault();
    try {
      // Preparar datos - solo incluir subject_id si está seleccionado
      const requestData = {
        date: attendanceForm.date,
        status: attendanceForm.status,
        notes: attendanceForm.notes || ''
      };
      
      if (attendanceForm.subject_id) {
        requestData.subject_id = parseInt(attendanceForm.subject_id);
      }
      
      const response = await api.post(`/students/${id}/attendance`, requestData);
      
      // Mostrar mensaje apropiado según si fue asistencia general o específica
      const message = attendanceForm.subject_id 
        ? 'Asistencia registrada correctamente'
        : response.data.message || 'Asistencia registrada para todas las asignaturas del día';
      
      toast.success(message);
      setShowAttendanceModal(false);
      setAttendanceForm({
        subject_id: null,
        date: new Date().toISOString().split('T')[0],
        status: 'present',
        notes: ''
      });
      loadStudentData();
    } catch (error) {
      console.error('Error creating attendance:', error);
      const errorMsg = error.response?.data?.error || 'Error al registrar asistencia';
      toast.error(errorMsg);
    }
  };

  const handleVoiceRecording = () => {
    toast.info('Función de grabación de voz en desarrollo');
    // TODO: Implementar integración con Whisper API
  };

  const handleExportPDF = async () => {
    toast.info('Generando PDF...', { duration: 2000 });
    // TODO: Implementar generación de PDF
  };

  // Funciones para evaluaciones contextuales (desde asignaturas/grupos)
  const handleOpenContextEvaluationForm = (evaluation = null) => {
    setCurrentContextEvaluation(evaluation);
    setContextEvaluationData({
      score: evaluation ? evaluation.total_score : '',
      comment: evaluation ? evaluation.comment || '' : ''
    });
    setShowContextEvaluationForm(true);
  };

  const handleSaveContextEvaluation = async () => {
    try {
      const data = {
        student: id,
        subject: asignaturaId,
        score: parseFloat(contextEvaluationData.score),
        comment: contextEvaluationData.comment,
        date: selectedDate || new Date().toISOString().split('T')[0]
      };

      if (currentContextEvaluation) {
        // Actualizar evaluación existente
        await api.put(`/evaluations/${currentContextEvaluation.id}/`, data);
        toast.success('Evaluación actualizada correctamente');
      } else {
        // Crear nueva evaluación
        await api.post('/evaluations/', data);
        toast.success('Evaluación creada correctamente');
      }

      // Recargar datos contextuales
      loadContextData();
      setShowContextEvaluationForm(false);
      setContextEvaluationData({ score: '', comment: '' });
      setCurrentContextEvaluation(null);
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

  if (!profile && !resumen) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Estudiante no encontrado
          </h2>
          <button
            onClick={() => navigate('/estudiantes')}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  // Siempre mostrar la vista global completa
  // Combinar evaluaciones y comentarios contextuales si existen
  const allEvaluations = contextEvaluations.length > 0 ? contextEvaluations : evaluations;
  const allComments = contextComments.length > 0 ? contextComments : comments;

  return (
    <div className="flex-1 p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm flex items-center gap-2">
          <button
            onClick={() => navigate('/estudiantes')}
            className="text-primary hover:underline"
          >
            Estudiantes
          </button>
          <span className="text-gray-500">›</span>
          <span className="text-gray-700 dark:text-gray-300">
            {profile?.name || resumen?.estudiante?.name}
          </span>
        </nav>

        {/* Header con información del estudiante */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {(profile?.name || resumen?.estudiante?.name)?.charAt(0).toUpperCase()}
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {profile?.name || resumen?.estudiante?.name}
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  {profile?.email || resumen?.estudiante?.email}
                </p>
                {subjectInfo && asignaturaId && (
                  <p className="text-sm text-primary font-medium mt-1">
                    Evaluación en: {subjectInfo.name}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={() => setShowEvaluationModal(true)}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 flex items-center gap-2"
            >
              <span>+</span>
              Nueva Evaluación
            </button>
          </div>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Asistencia Global</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">0%</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">0 registros</p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Promedio General</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {allEvaluations.length > 0
                ? Math.round(allEvaluations.reduce((acc, ev) => acc + (ev.total_score || 0), 0) / allEvaluations.length * 10) / 10
                : 0}/10
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">sobre 10</p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Evaluaciones</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{allEvaluations.length}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Total registradas</p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Comentarios</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{allComments.length}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Del profesorado</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'overview'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                Resumen
              </button>
              <button
                onClick={() => setActiveTab('evaluaciones')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'evaluaciones'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                Evaluaciones ({allEvaluations.length})
              </button>
              <button
                onClick={() => setActiveTab('comentarios')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'comentarios'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                Comentarios ({allComments.length})
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Aquí puedes agregar la distribución de asistencia y promedios por asignatura si lo deseas */}
                <p className="text-gray-500 dark:text-gray-400">Distribución de Asistencia y Promedios por Asignatura aquí...</p>
              </div>
            )}

            {activeTab === 'evaluaciones' && (
              <div className="space-y-4">
                {allEvaluations.length > 0 ? (
                  allEvaluations.map((evaluation) => (
                    <div
                      key={evaluation.id}
                      className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">
                            {evaluation.rubric}
                          </h4>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {evaluation.evaluator} • {new Date(evaluation.evaluated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-primary">
                            {evaluation.total_score}/10
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {evaluation.porcentaje}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                    No hay evaluaciones registradas
                  </p>
                )}
              </div>
            )}

            {activeTab === 'comentarios' && (
              <div className="space-y-4">
                {allComments.length > 0 ? (
                  allComments.map((comentario) => (
                    <div
                      key={comentario.id}
                      className="border-l-4 border-green-500 pl-4 py-3 bg-gray-50 dark:bg-gray-800/50 rounded-r-lg"
                    >
                      <p className="text-gray-800 dark:text-gray-200 mb-2">
                        {comentario.text || comentario.content}
                      </p>
                      <p className="text-xs text-gray-500">
                        {comentario.author || comentario.comment_type} • {comentario.subject || ''} • 
                        {comentario.created_at ? new Date(comentario.created_at).toLocaleDateString() : ''}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                    No hay comentarios registrados
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Modales de evaluación y comentario */}
        {showCommentModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-card-dark rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Nuevo Comentario
                </h3>
                <button
                  onClick={() => setShowCommentModal(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
              
              <form onSubmit={handleCreateComment} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tipo de Comentario
                  </label>
                  <select
                    value={commentForm.comment_type}
                    onChange={(e) => setCommentForm({...commentForm, comment_type: e.target.value})}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                    required
                  >
                    <option value="general">General</option>
                    <option value="behavior">Comportamiento</option>
                    <option value="academic">Académico</option>
                    <option value="progress">Progreso</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Asignatura (Opcional)
                  </label>
                  <select
                    value={commentForm.subject_id || ''}
                    onChange={(e) => setCommentForm({...commentForm, subject_id: e.target.value || null})}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                  >
                    <option value="">Sin asignatura específica</option>
                    {subjects.map(subject => (
                      <option key={subject.id} value={subject.id}>
                        {subject.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Comentario
                  </label>
                  <textarea
                    value={commentForm.content}
                    onChange={(e) => setCommentForm({...commentForm, content: e.target.value})}
                    rows={6}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                    placeholder="Escribe tu comentario aquí..."
                    required
                  />
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleVoiceRecording}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/30 transition"
                  >
                    <span className="material-symbols-outlined text-sm">mic</span>
                    Grabar Audio
                  </button>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    Transcripción automática con Whisper AI
                  </span>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-800">
                  <button
                    type="button"
                    onClick={() => setShowCommentModal(false)}
                    className="px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
                  >
                    Guardar Comentario
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showEvaluationModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-card-dark rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Nueva Evaluación
                </h3>
                <button
                  onClick={() => setShowEvaluationModal(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
              
              <form onSubmit={handleCreateEvaluation} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Asignatura *
                    </label>
                    <select
                      value={evaluationForm.subject_id || ''}
                      onChange={(e) => setEvaluationForm({...evaluationForm, subject_id: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                      required
                    >
                      <option value="">Seleccionar asignatura</option>
                      {subjects.map(subject => (
                        <option key={subject.id} value={subject.id}>
                          {subject.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Título *
                    </label>
                    <input
                      type="text"
                      value={evaluationForm.title}
                      onChange={(e) => setEvaluationForm({...evaluationForm, title: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                      placeholder="Ej: Examen Tema 5"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tipo de Evaluación
                    </label>
                    <select
                      value={evaluationForm.evaluation_type}
                      onChange={(e) => setEvaluationForm({...evaluationForm, evaluation_type: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                    >
                      <option value="exam">Examen</option>
                      <option value="homework">Tarea</option>
                      <option value="project">Proyecto</option>
                      <option value="presentation">Presentación</option>
                      <option value="participation">Participación</option>
                      <option value="other">Otro</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Fecha
                    </label>
                    <input
                      type="date"
                      value={evaluationForm.date}
                      onChange={(e) => setEvaluationForm({...evaluationForm, date: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nota Obtenida *
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={evaluationForm.grade}
                      onChange={(e) => setEvaluationForm({...evaluationForm, grade: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                      placeholder="7.5"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nota Máxima
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={evaluationForm.max_grade}
                      onChange={(e) => setEvaluationForm({...evaluationForm, max_grade: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                      required
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Estado de Ánimo del Estudiante
                    </label>
                    <select
                      value={evaluationForm.mood}
                      onChange={(e) => setEvaluationForm({...evaluationForm, mood: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                    >
                      <option value="confident">Confiado</option>
                      <option value="satisfied">Satisfecho</option>
                      <option value="neutral">Neutral</option>
                      <option value="anxious">Ansioso</option>
                    </select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Notas Adicionales
                    </label>
                    <textarea
                      value={evaluationForm.notes}
                      onChange={(e) => setEvaluationForm({...evaluationForm, notes: e.target.value})}
                      rows={3}
                      className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                      placeholder="Comentarios sobre el desempeño..."
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-800">
                  <button
                    type="button"
                    onClick={() => setShowEvaluationModal(false)}
                    className="px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
                  >
                    Guardar Evaluación
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Registrar Asistencia */}
        {showAttendanceModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-card-dark rounded-xl shadow-xl max-w-lg w-full">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Registrar Asistencia
                </h3>
                <button
                  onClick={() => setShowAttendanceModal(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
              
              <form onSubmit={handleCreateAttendance} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Asignatura
                  </label>
                  <select
                    value={attendanceForm.subject_id || ''}
                    onChange={(e) => setAttendanceForm({...attendanceForm, subject_id: e.target.value || null})}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                  >
                    <option value="">General</option>
                    {subjects.map(subject => (
                      <option key={subject.id} value={subject.id}>
                        {subject.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Fecha
                  </label>
                  <input
                    type="date"
                    value={attendanceForm.date}
                    onChange={(e) => setAttendanceForm({...attendanceForm, date: e.target.value})}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Estado
                  </label>
                  <select
                    value={attendanceForm.status}
                    onChange={(e) => setAttendanceForm({...attendanceForm, status: e.target.value})}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900 dark:text-white"
                    required
                  >
                    <option value="present">Presente</option>
                    <option value="absent">Ausente</option>
                    <option value="late">Tarde</option>
                    <option value="excused">Justificado</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notas
                  </label>
                  <textarea
                    value={attendanceForm.notes}
                    onChange={(e) => setAttendanceForm({...attendanceForm, notes: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                    placeholder="Notas adicionales..."
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-800">
                  <button
                    type="button"
                    onClick={() => setShowAttendanceModal(false)}
                    className="px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
                  >
                    Registrar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default StudentProfilePage;
