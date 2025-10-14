// frontend/src/pages/StudentProfilePage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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

  const loadStudentData = async () => {
    try {
      setLoading(true);
      
      // Cargar datos básicos del estudiante
      const profileRes = await api.get(`/students/${id}/`);
      setProfile(profileRes.data);
      
      // Intentar cargar datos adicionales (pueden no existir aún)
      try {
        const attendanceRes = await api.get(`/students/${id}/attendance`);
        setAttendances(Array.isArray(attendanceRes.data) ? attendanceRes.data : []);
      } catch (err) {
        console.log('No attendance data available');
        setAttendances([]);
      }
      
      try {
        const evaluationsRes = await api.get(`/students/${id}/evaluations`);
        setEvaluations(Array.isArray(evaluationsRes.data) ? evaluationsRes.data : []);
      } catch (err) {
        console.log('No evaluations data available');
        setEvaluations([]);
      }
      
      try {
        const commentsRes = await api.get(`/students/${id}/comments`);
        setComments(Array.isArray(commentsRes.data) ? commentsRes.data : []);
      } catch (err) {
        console.log('No comments data available');
        setComments([]);
      }
      
      try {
        const averagesRes = await api.get(`/students/${id}/evaluations/by-subject`);
        setSubjectAverages(Array.isArray(averagesRes.data) ? averagesRes.data : []);
      } catch (err) {
        console.log('No subject averages available');
        setSubjectAverages([]);
      }
      
    } catch (error) {
      console.error('Error loading student data:', error);
      toast.error('Error al cargar datos del estudiante');
      // Navegar de vuelta si el estudiante no existe
      setTimeout(() => navigate('/estudiantes'), 2000);
    } finally {
      setLoading(false);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!profile) {
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

  // Datos para el gráfico de asistencia
  const getAttendanceCounts = () => {
    const counts = { present: 0, absent: 0, late: 0, excused: 0 };
    attendances.forEach(att => {
      if (att.status in counts) counts[att.status]++;
    });
    return counts;
  };
  
  const attCounts = getAttendanceCounts();
  const attendanceChartData = {
    labels: ['Presente', 'Ausente', 'Tarde', 'Justificado'],
    datasets: [
      {
        data: [
          attCounts.present,
          attCounts.absent,
          attCounts.late,
          attCounts.excused
        ],
        backgroundColor: [
          '#22c55e',
          '#ef4444',
          '#f59e0b',
          '#3b82f6'
        ],
        borderWidth: 0
      }
    ]
  };

  // Datos para el gráfico de promedios por asignatura
  const averagesChartData = {
    labels: subjectAverages.map(s => s.subject_name),
    datasets: [
      {
        label: 'Promedio',
        data: subjectAverages.map(s => s.average_grade),
        backgroundColor: '#39E079',
        borderRadius: 8
      }
    ]
  };

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        
        {/* Header con información del estudiante */}
        <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 mb-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            
            {/* Avatar y datos básicos */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center">
                  <span className="text-3xl font-bold text-primary">
                    {(profile.name || profile.username || '?').charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                  {profile.name || profile.username || 'Sin nombre'}
                </h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">
                  {profile.email || 'Sin email'}
                </p>
                {profile.course && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    📚 {profile.course}
                  </p>
                )}
                {profile.groups && profile.groups.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {profile.groups.map(group => (
                      <span
                        key={group.id}
                        className="px-3 py-1 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: `${group.color || '#3B82F6'}20`,
                          color: group.color || '#3B82F6'
                        }}
                      >
                        {group.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Botones de acción */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => navigate(`/estudiantes/${id}/editar`)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
              >
                <span className="material-symbols-outlined text-sm">edit</span>
                Editar
              </button>
              <button
                onClick={handleExportPDF}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
              >
                <span className="material-symbols-outlined text-sm">description</span>
                Exportar PDF
              </button>
            </div>
          </div>
        </div>

        {/* Tarjetas de estadísticas rápidas */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          
          {/* Asistencia */}
          <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">Asistencia Global</span>
              <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-green-600 dark:text-green-400">
                  check_circle
                </span>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {profile.attendance_percentage || 0}%
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {attendances.length || 0} registros
            </p>
          </div>

          {/* Promedio General */}
          <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">Promedio General</span>
              <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">
                  school
                </span>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {evaluations.length > 0 
                ? (evaluations.reduce((sum, e) => sum + (e.grade || 0), 0) / evaluations.length).toFixed(1)
                : '---'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              sobre 10
            </p>
          </div>

          {/* Evaluaciones */}
          <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">Evaluaciones</span>
              <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-purple-600 dark:text-purple-400">
                  assignment
                </span>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {evaluations.length || 0}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Total registradas
            </p>
          </div>

          {/* Comentarios */}
          <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">Comentarios</span>
              <div className="w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-orange-600 dark:text-orange-400">
                  comment
                </span>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {comments.length || 0}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Del profesorado
            </p>
          </div>
        </div>

        {/* Tabs de navegación */}
        <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 mb-6">
          <div className="border-b border-gray-200 dark:border-gray-800">
            <nav className="flex gap-4 p-4 overflow-x-auto">
              {[
                { id: 'overview', label: 'Resumen', icon: 'dashboard' },
                { id: 'attendance', label: 'Asistencia', icon: 'event_available' },
                { id: 'evaluations', label: 'Evaluaciones', icon: 'grade' },
                { id: 'comments', label: 'Comentarios', icon: 'comment' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-primary/10 text-primary'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <span className="material-symbols-outlined text-sm">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Contenido de los tabs */}
          <div className="p-6">
            
            {/* Tab: Resumen */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                
                {/* Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Gráfico de asistencia */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      Distribución de Asistencia
                    </h3>
                    <div className="h-64 flex items-center justify-center">
                      <Doughnut 
                        data={attendanceChartData}
                        options={{
                          plugins: {
                            legend: {
                              position: 'bottom',
                              labels: {
                                color: '#9ca3af',
                                padding: 15,
                                font: {
                                  size: 12
                                }
                              }
                            }
                          },
                          maintainAspectRatio: false
                        }}
                      />
                    </div>
                  </div>

                  {/* Gráfico de promedios */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      Promedios por Asignatura
                    </h3>
                    <div className="h-64">
                      <Bar 
                        data={averagesChartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: false
                            }
                          },
                          scales: {
                            y: {
                              beginAtZero: true,
                              max: 10,
                              grid: {
                                color: '#374151'
                              },
                              ticks: {
                                color: '#9ca3af'
                              }
                            },
                            x: {
                              grid: {
                                display: false
                              },
                              ticks: {
                                color: '#9ca3af'
                              }
                            }
                          }
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Asignaturas matriculadas */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Asignaturas Matriculadas
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {subjectAverages.map(subject => (
                      <div
                        key={subject.subject_id}
                        className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                      >
                        <div className="flex items-center gap-3 mb-2">
                          <span className="material-symbols-outlined text-primary">
                            book
                          </span>
                          <h4 className="font-medium text-gray-900 dark:text-white">
                            {subject.subject_name}
                          </h4>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            Promedio: <span className="font-semibold text-gray-900 dark:text-white">{subject.average_grade}</span>
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {subject.evaluation_count} evaluaciones
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Tab: Asistencia */}
            {activeTab === 'attendance' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Historial de Asistencia
                  </h3>
                  <button
                    onClick={() => setShowAttendanceModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                  >
                    <span className="material-symbols-outlined text-sm">add</span>
                    Registrar
                  </button>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-800">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                          Fecha
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                          Asignatura
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                          Estado
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                          Notas
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendances.map(attendance => (
                        <tr key={attendance.id} className="border-b border-gray-100 dark:border-gray-800">
                          <td className="py-3 px-4 text-sm text-gray-900 dark:text-white">
                            {new Date(attendance.date).toLocaleDateString('es-ES')}
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-900 dark:text-white">
                            {attendance.subject_name || '-'}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                              attendance.status === 'present' ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400' :
                              attendance.status === 'absent' ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400' :
                              attendance.status === 'late' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400' :
                              'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                            }`}>
                              {attendance.status === 'present' ? 'Presente' :
                               attendance.status === 'absent' ? 'Ausente' :
                               attendance.status === 'late' ? 'Tarde' : 'Justificado'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-500 dark:text-gray-400">
                            {attendance.notes || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Tab: Evaluaciones */}
            {activeTab === 'evaluations' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Historial de Evaluaciones
                  </h3>
                  <button
                    onClick={() => setShowEvaluationModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                  >
                    <span className="material-symbols-outlined text-sm">add</span>
                    Nueva Evaluación
                  </button>
                </div>
                
                <div className="space-y-3">
                  {evaluations.map(evaluation => (
                    <div
                      key={evaluation.id}
                      className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary/50 transition"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {evaluation.title}
                            </h4>
                            {evaluation.mood && (
                              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                evaluation.mood === 'confident' ? 'bg-green-100 text-green-700' :
                                evaluation.mood === 'satisfied' ? 'bg-blue-100 text-blue-700' :
                                evaluation.mood === 'neutral' ? 'bg-gray-100 text-gray-700' :
                                'bg-orange-100 text-orange-700'
                              }`}>
                                {evaluation.mood === 'confident' ? 'Confiado' :
                                 evaluation.mood === 'satisfied' ? 'Satisfecho' :
                                 evaluation.mood === 'neutral' ? 'Neutral' : 'Ansioso'}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                            {evaluation.subject_name} • {new Date(evaluation.date).toLocaleDateString('es-ES')}
                          </p>
                          {evaluation.notes && (
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                              {evaluation.notes}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-primary">
                            {evaluation.grade?.toFixed(1)}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            sobre {evaluation.max_grade}
                          </div>
                          {evaluation.percentage && (
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {evaluation.percentage.toFixed(0)}%
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab: Comentarios */}
            {activeTab === 'comments' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Comentarios del Profesorado
                  </h3>
                  <button
                    onClick={() => setShowCommentModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                  >
                    <span className="material-symbols-outlined text-sm">add</span>
                    Nuevo Comentario
                  </button>
                </div>
                
                <div className="space-y-4">
                  {comments.map(comment => (
                    <div
                      key={comment.id}
                      className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <span className="material-symbols-outlined text-primary text-sm">
                            person
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900 dark:text-white">
                                {comment.author_name}
                              </span>
                              {comment.is_voice_transcription && (
                                <span className="material-symbols-outlined text-purple-500 text-sm" title="Transcripción de voz">
                                  mic
                                </span>
                              )}
                            </div>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {new Date(comment.created_at).toLocaleDateString('es-ES')}
                            </span>
                          </div>
                          {comment.subject_name && (
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                              {comment.subject_name}
                            </p>
                          )}
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            {comment.content}
                          </p>
                          <div className="flex gap-2 mt-2">
                            <span className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs text-gray-600 dark:text-gray-400">
                              {comment.comment_type}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {comments.length === 0 && (
                    <div className="text-center py-12">
                      <span className="material-symbols-outlined text-6xl text-gray-300 dark:text-gray-700">
                        chat_bubble_outline
                      </span>
                      <p className="text-gray-500 dark:text-gray-400 mt-4">
                        No hay comentarios aún
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal: Nuevo Comentario */}
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
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
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

      {/* Modal: Nueva Evaluación */}
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
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
                  Asignatura (Opcional)
                </label>
                <select
                  value={attendanceForm.subject_id || ''}
                  onChange={(e) => setAttendanceForm({...attendanceForm, subject_id: e.target.value || null})}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">📚 Todas las asignaturas del día</option>
                  {subjects.map(subject => (
                    <option key={subject.id} value={subject.id}>
                      {subject.name}
                    </option>
                  ))}
                </select>
                {!attendanceForm.subject_id && (
                  <p className="mt-2 text-sm text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-3 py-2 rounded-lg">
                    ℹ️ Se registrará la asistencia para todas las clases programadas en la fecha seleccionada
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fecha
                </label>
                <input
                  type="date"
                  value={attendanceForm.date}
                  onChange={(e) => setAttendanceForm({...attendanceForm, date: e.target.value})}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Estado *
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'present', label: 'Presente', color: 'green' },
                    { value: 'absent', label: 'Ausente', color: 'red' },
                    { value: 'late', label: 'Tarde', color: 'yellow' },
                    { value: 'excused', label: 'Justificado', color: 'blue' }
                  ].map(status => (
                    <button
                      key={status.value}
                      type="button"
                      onClick={() => setAttendanceForm({...attendanceForm, status: status.value})}
                      className={`px-4 py-3 rounded-lg border-2 transition ${
                        attendanceForm.status === status.value
                          ? `border-${status.color}-500 bg-${status.color}-50 dark:bg-${status.color}-900/20`
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <span className={`font-medium ${
                        attendanceForm.status === status.value
                          ? `text-${status.color}-700 dark:text-${status.color}-400`
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {status.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Notas
                </label>
                <textarea
                  value={attendanceForm.notes}
                  onChange={(e) => setAttendanceForm({...attendanceForm, notes: e.target.value})}
                  rows={3}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  placeholder="Comentarios adicionales..."
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
                  Registrar Asistencia
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentProfilePage;
