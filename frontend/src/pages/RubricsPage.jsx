// frontend/src/pages/RubricsPage.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const RubricsPage = () => {
  const navigate = useNavigate();
  const [rubrics, setRubrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, active, inactive, draft
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadRubrics();
  }, [filter]);

  const loadRubrics = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filter !== 'all') {
        params.status = filter;
      }
      const response = await api.get('/rubrics/', { params });
      const rubricsData = response.data.results || response.data;
      setRubrics(Array.isArray(rubricsData) ? rubricsData : []);
    } catch (error) {
      console.error('Error loading rubrics:', error);
      toast.error('Error al cargar rúbricas');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (rubricId) => {
    if (!window.confirm('¿Estás seguro de eliminar esta rúbrica?')) return;
    
    try {
      await api.delete(`/rubrics/${rubricId}/`);
      toast.success('Rúbrica eliminada correctamente');
      loadRubrics();
    } catch (error) {
      console.error('Error deleting rubric:', error);
      toast.error('Error al eliminar rúbrica');
    }
  };

  const handleDuplicate = async (rubric) => {
    try {
      const response = await api.post(`/rubrics/${rubric.id}/duplicate/`);
      toast.success('Rúbrica duplicada correctamente');
      loadRubrics();
    } catch (error) {
      console.error('Error duplicating rubric:', error);
      toast.error('Error al duplicar rúbrica');
    }
  };

  const filteredRubrics = rubrics.filter(rubric =>
    rubric.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (rubric.description && rubric.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-400',
      inactive: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
      draft: 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-700 dark:text-yellow-400'
    };
    const labels = {
      active: 'Activa',
      inactive: 'Inactiva',
      draft: 'Borrador'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${styles[status] || styles.draft}`}>
        {labels[status] || status}
      </span>
    );
  };

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Rúbricas de Evaluación</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Crea y gestiona rúbricas para evaluaciones estructuradas
            </p>
          </div>
          <button
            onClick={() => navigate('/rubricas/nueva')}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 font-semibold transition"
          >
            <span className="material-symbols-outlined text-base">add</span>
            Nueva Rúbrica
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                search
              </span>
              <input
                type="text"
                placeholder="Buscar rúbricas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 focus:ring-primary focus:border-primary"
              />
            </div>

            {/* Filters */}
            <div className="flex gap-2">
              {['all', 'active', 'draft', 'inactive'].map(status => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    filter === status
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {status === 'all' ? 'Todas' : status === 'active' ? 'Activas' : status === 'draft' ? 'Borradores' : 'Inactivas'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Rubrics Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : filteredRubrics.length === 0 ? (
          <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-12 text-center">
            <span className="material-symbols-outlined text-6xl text-gray-300 dark:text-gray-700 mb-4">
              assignment
            </span>
            <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
              No hay rúbricas
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Crea tu primera rúbrica para empezar a evaluar
            </p>
            <button
              onClick={() => navigate('/rubricas/nueva')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 font-semibold transition"
            >
              <span className="material-symbols-outlined text-base">add</span>
              Nueva Rúbrica
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredRubrics.map(rubric => (
              <div
                key={rubric.id}
                className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 hover:border-primary dark:hover:border-primary transition-colors cursor-pointer group"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1" onClick={() => navigate(`/rubricas/${rubric.id}/editar`)}>
                      <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary transition">
                        {rubric.title}
                      </h3>
                      {rubric.description && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                          {rubric.description}
                        </p>
                      )}
                    </div>
                    {getStatusBadge(rubric.status)}
                  </div>

                  <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-4">
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined text-sm">list_alt</span>
                      {rubric.criteria_count || 0} criterios
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined text-sm">calendar_today</span>
                      {new Date(rubric.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-4 border-t border-gray-100 dark:border-gray-700 flex-wrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/rubricas/${rubric.id}/editar`);
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition"
                    >
                      <span className="material-symbols-outlined text-base">edit</span>
                      Editar
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/rubricas/${rubric.id}/aplicar`);
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 text-sm text-primary hover:bg-primary/10 dark:hover:bg-primary/20 rounded transition font-medium"
                    >
                      <span className="material-symbols-outlined text-base">check_circle</span>
                      Aplicar
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/rubricas/${rubric.id}/resultados`);
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 text-sm text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded transition font-medium"
                    >
                      <span className="material-symbols-outlined text-base">bar_chart</span>
                      Resultados
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(rubric.id);
                      }}
                      className="ml-auto flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition"
                    >
                      <span className="material-symbols-outlined text-base">delete</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RubricsPage;
