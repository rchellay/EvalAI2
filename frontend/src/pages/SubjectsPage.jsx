// frontend/src/pages/SubjectsPage.jsx
import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';
import SubjectModal from '../components/SubjectModal';

const SubjectsPage = () => {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    filter: 'all' // 'all', 'active', 'archived'
  });

  useEffect(() => {
    loadSubjects();
  }, [filters]);

  const loadSubjects = async () => {
    console.log('[SubjectsPage] Cargando asignaturas...');
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.filter === 'active') params.is_active = true;
      if (filters.filter === 'archived') params.is_active = false;

      console.log('[SubjectsPage] Petición a /subjects con params:', params);
      const response = await api.get('/subjects/', { params });
      console.log('[SubjectsPage] Respuesta recibida:', response.data);
      // Django REST Framework returns paginated data with "results" array
      const subjectsData = response.data.results || response.data;
      console.log('[SubjectsPage] Total asignaturas:', Array.isArray(subjectsData) ? subjectsData.length : 0);
      setSubjects(Array.isArray(subjectsData) ? subjectsData : []);
    } catch (error) {
      console.error('[SubjectsPage] ❌ Error loading subjects:', error);
      console.error('[SubjectsPage] Error response:', error.response?.data);
      console.error('[SubjectsPage] Error status:', error.response?.status);
      toast.error('Error al cargar asignaturas');
      setSubjects([]); // Ensure it's always an array
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setSelectedSubject(null);
    setIsModalOpen(true);
  };

  const handleEdit = (subject) => {
    setSelectedSubject(subject);
    setIsModalOpen(true);
  };

  const handleDelete = async (subjectId) => {
    if (!window.confirm('¿Estás seguro de eliminar esta asignatura?')) return;

    try {
      await api.delete(`/subjects/${subjectId}/`);
      toast.success('Asignatura eliminada');
      loadSubjects();
    } catch (error) {
      console.error('Error deleting subject:', error);
      toast.error('Error al eliminar asignatura');
    }
  };

  const handleModalClose = (refresh) => {
    setIsModalOpen(false);
    setSelectedSubject(null);
    if (refresh) loadSubjects();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-wrap justify-between items-center gap-4 mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Asignaturas</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Gestiona tus asignaturas y grupos de forma eficiente.
            </p>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90 transition"
          >
            <span className="material-symbols-outlined">add</span>
            Nueva Asignatura
          </button>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
              search
            </span>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-700 focus:ring-primary focus:border-primary text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
              placeholder="Buscar asignaturas..."
            />
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={() => setFilters({ ...filters, filter: 'all' })}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              filters.filter === 'all'
                ? 'bg-primary/10 dark:bg-primary/20 text-primary'
                : 'bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            Todas
            <span className="material-symbols-outlined text-base">expand_more</span>
          </button>
          <button
            onClick={() => setFilters({ ...filters, filter: 'active' })}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              filters.filter === 'active'
                ? 'bg-primary/10 dark:bg-primary/20 text-primary'
                : 'bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            Activas
            <span className="material-symbols-outlined text-base">expand_more</span>
          </button>
          <button
            onClick={() => setFilters({ ...filters, filter: 'archived' })}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              filters.filter === 'archived'
                ? 'bg-primary/10 dark:bg-primary/20 text-primary'
                : 'bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            Archivadas
            <span className="material-symbols-outlined text-base">expand_more</span>
          </button>
        </div>

        {/* Table */}
        <div className="bg-white dark:bg-background-dark/50 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-800">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-background-dark">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Curso
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Grupos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estudiantes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {subjects.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    No hay asignaturas. Crea tu primera asignatura.
                  </td>
                </tr>
              ) : (
                subjects.map((subject) => (
                  <tr key={subject.id} className="hover:bg-primary/5 dark:hover:bg-primary/10 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: subject.color }}
                        ></div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {subject.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {subject.course}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {subject.group_count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {subject.student_count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          subject.is_active
                            ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300'
                            : 'bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300'
                        }`}
                      >
                        {subject.is_active ? 'Activa' : 'Archivada'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                      <button
                        onClick={() => handleEdit(subject)}
                        className="text-primary hover:text-primary/80"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(subject.id)}
                        className="text-red-600 hover:text-red-500"
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <SubjectModal
          subject={selectedSubject}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};

export default SubjectsPage;
