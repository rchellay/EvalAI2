// frontend/src/pages/StudentEvaluationPanel.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

// Importar los widgets
import WidgetRubricas from '../components/widgets/WidgetRubricas';
import WidgetComentariosRapidos from '../components/widgets/WidgetComentariosRapidos';
import WidgetGrabacionAudio from '../components/widgets/WidgetGrabacionAudio';
import WidgetAsistencia from '../components/widgets/WidgetAsistencia';
import WidgetRecomendacionesIA from '../components/widgets/WidgetRecomendacionesIA';
import WidgetObjetivos from '../components/widgets/WidgetObjetivos';
import WidgetEvidencias from '../components/widgets/WidgetEvidencias';
import WidgetAutoevaluacion from '../components/widgets/WidgetAutoevaluacion';
import WidgetHistorialEvaluaciones from '../components/widgets/WidgetHistorialEvaluaciones';

const StudentEvaluationPanel = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Context from navigation
  const asignaturaId = searchParams.get('asignatura');

  // State
  const [student, setStudent] = useState(null);
  const [subject, setSubject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshHistorial, setRefreshHistorial] = useState(0);

  useEffect(() => {
    loadData();
  }, [id, asignaturaId]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load student data
      const studentResponse = await api.get(`/students/${id}/`);
      setStudent(studentResponse.data);

      // Load subject data if accessed from subject
      if (asignaturaId) {
        const subjectResponse = await api.get(`/subjects/${asignaturaId}/`);
        setSubject(subjectResponse.data);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluationCreated = (evaluation) => {
    toast.success('Evaluación registrada exitosamente');
    setRefreshHistorial(prev => prev + 1);
  };

  const handleCommentCreated = (comment) => {
    toast.success('Comentario guardado exitosamente');
    setRefreshHistorial(prev => prev + 1);
  };

  const handleAudioSaved = (audio) => {
    toast.success('Audio guardado exitosamente');
    setRefreshHistorial(prev => prev + 1);
  };

  const handleAttendanceRecorded = (attendance) => {
    toast.success('Asistencia registrada exitosamente');
  };

  const handleObjectiveCreated = (objective) => {
    toast.success('Objetivo creado exitosamente');
  };

  const handleEvidenceUploaded = (evidence) => {
    toast.success('Evidencia subida exitosamente');
  };

  const handleSelfEvaluationCreated = (evaluation) => {
    toast.success('Autoevaluación guardada exitosamente');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando perfil del alumno...</p>
        </div>
      </div>
    );
  }

  if (!student) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Estudiante no encontrado</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header y Grid */}
        <div>
          {/* Header */}
          <div className="mb-6">
            <div>
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-black flex items-center">
                    <span className="mr-3">👨‍🎓</span>
                    {student.name}
                  </h1>
                  {subject && (
                    <div>
                      <p className="text-black mt-1">
                        📘 Asignatura: {subject.name}
                      </p>
                    </div>
                  )}
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => navigate(`/estudiantes/${id}/editar`)}
                    className="px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                  >
                    ✏️ Ver/Editar Perfil
                  </button>
                  <button
                    onClick={() => navigate(-1)}
                    className="px-4 py-2 text-black hover:text-white border border-black rounded-md hover:bg-black"
                  >
                    ← Volver
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Ajustes en los widgets */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <>
            <WidgetComentariosRapidos
              studentId={id}
              subjectId={asignaturaId}
              onCommentCreated={handleCommentCreated}
              className="bg-white text-black border border-gray-300 rounded-md shadow-md"
              titleClassName="text-xl font-bold text-black mb-4"
            />

            <WidgetGrabacionAudio
              studentId={id}
              subjectId={asignaturaId}
              onAudioSaved={handleAudioSaved}
              className="bg-white text-black border border-gray-300 rounded-md shadow-md"
              titleClassName="text-xl font-bold text-black mb-4"
            />

            <WidgetAsistencia
              studentId={id}
              subjectId={asignaturaId}
              onAttendanceRecorded={handleAttendanceRecorded}
              className="bg-white text-black border border-gray-300 rounded-md shadow-md"
              titleClassName="text-xl font-bold text-black mb-4"
            />

            <WidgetRubricas
              studentId={id}
              subjectId={asignaturaId}
              onEvaluationCreated={handleEvaluationCreated}
              className="bg-white text-black border border-gray-300 rounded-md shadow-md"
              titleClassName="text-xl font-bold text-black mb-4"
            />

            <WidgetObjetivos
              studentId={id}
              subjectId={asignaturaId}
              onObjectiveCreated={handleObjectiveCreated}
              className="bg-white text-black border border-gray-300 rounded-md shadow-md"
              titleClassName="text-xl font-bold text-black mb-4"
            />

            <WidgetEvidencias
              studentId={id}
              subjectId={asignaturaId}
              onEvidenceUploaded={handleEvidenceUploaded}
              className="bg-white text-black border border-gray-300 rounded-md shadow-md"
              titleClassName="text-xl font-bold text-black mb-4"
            />

            <WidgetAutoevaluacion
              studentId={id}
              subjectId={asignaturaId}
              onSelfEvaluationCreated={handleSelfEvaluationCreated}
              className="bg-white text-black border border-gray-300 rounded-md shadow-md"
              titleClassName="text-xl font-bold text-black mb-4"
            />

            {/* Recomendaciones IA - Ancho completo */}
            <div className="md:col-span-2 lg:col-span-3">
              <WidgetRecomendacionesIA
                studentId={id}
                className="bg-white text-black border border-gray-300 rounded-md shadow-md"
                titleClassName="text-xl font-bold text-black mb-4"
              />
            </div>

            {/* Historial de Evaluaciones - Ancho completo */}
            <div className="md:col-span-2 lg:col-span-3">
              <WidgetHistorialEvaluaciones
                studentId={id}
                subjectId={asignaturaId}
                refreshTrigger={refreshHistorial}
                onEvaluationDeleted={() => setRefreshHistorial(prev => prev + 1)}
                className="bg-white text-black border border-gray-300 rounded-md shadow-md"
                titleClassName="text-xl font-bold text-black mb-4"
              />
            </div>
          </>
        </div>
      </div>
    </div>
  );
};

export default StudentEvaluationPanel;