// frontend/src/pages/SubjectDetailPage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const DAYS_OF_WEEK_ES = {
  monday: 'Lunes',
  tuesday: 'Martes',
  wednesday: 'Miércoles',
  thursday: 'Jueves',
  friday: 'Viernes',
  saturday: 'Sábado',
  sunday: 'Domingo'
};

const SubjectDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [subject, setSubject] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubjectDetails();
  }, [id]);

  const loadSubjectDetails = async () => {
    try {
      const response = await api.get(`/subjects/${id}/`);
      setSubject(response.data);
    } catch (error) {
      console.error('Error loading subject:', error);
      toast.error('Error al cargar la asignatura');
      navigate('/asignaturas');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!subject) {
    return (
      <div className="p-8">
        <p className="text-red-600">Asignatura no encontrada</p>
      </div>
    );
  }

  return (
    <div className="flex-1 p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm">
          <Link to="/asignaturas" className="text-primary hover:underline">
            Asignaturas
          </Link>
          <span className="mx-2 text-gray-500">/</span>
          <span className="text-gray-900 dark:text-white font-medium">{subject.name}</span>
        </nav>

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold text-white"
              style={{ backgroundColor: subject.color }}
            >
              {subject.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">{subject.name}</h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">{subject.course}</p>
              {subject.description && (
                <p className="text-gray-600 dark:text-gray-400 mt-2">{subject.description}</p>
              )}
            </div>
          </div>
          <button
            onClick={() => navigate('/asignaturas')}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
          >
            Volver
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Grupos</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {subject.group_count || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Estudiantes</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {subject.student_count || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Horarios</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {subject.schedules?.length || 0}
            </p>
          </div>
        </div>

        {/* Schedules Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Horarios de clase
          </h2>
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
            {!subject.schedules || subject.schedules.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                No hay horarios definidos para esta asignatura.
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-800">
                {subject.schedules.map((schedule, index) => (
                  <div key={index} className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                        <span className="material-symbols-outlined text-blue-600 dark:text-blue-300">
                          schedule
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {DAYS_OF_WEEK_ES[schedule.day_of_week]}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {schedule.start_time.substring(0, 5)} - {schedule.end_time.substring(0, 5)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Groups Section */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Grupos ({subject.groups?.length || 0})
          </h2>
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
            {!subject.groups || subject.groups.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                Esta asignatura no está asignada a ningún grupo.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
                {subject.groups.map((group) => (
                  <Link
                    key={group.id}
                    to={`/grupos/${group.id}`}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: group.color }}
                        ></div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{group.name}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {group.course} • {group.student_count} estudiantes
                          </p>
                        </div>
                      </div>
                      <span className="material-symbols-outlined text-gray-400">
                        chevron_right
                      </span>
                    </div>

                    {/* Students preview */}
                    {group.students && group.students.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                          Estudiantes:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {group.students.slice(0, 5).map((student) => (
                            <div
                              key={student.id}
                              className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-700 dark:text-gray-300"
                            >
                              {student.name || student.username || 'Sin nombre'}
                            </div>
                          ))}
                          {group.students.length > 5 && (
                            <div className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-500">
                              +{group.students.length - 5} más
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default SubjectDetailPage;
