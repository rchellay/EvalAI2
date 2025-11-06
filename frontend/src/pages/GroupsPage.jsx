// frontend/src/pages/GroupsPage.jsx
import { useState, useEffect, useMemo } from 'react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import useGroupStore, { selectGroups, selectLoading } from '../stores/groupStore';
import GroupModal from '../components/GroupModal';

const GroupsPage = () => {
  const navigate = useNavigate();
  
  // Zustand store
  const groups = useGroupStore(selectGroups);
  const loading = useGroupStore(selectLoading);
  const { fetchGroups, deleteGroup } = useGroupStore();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    course: '',
    filter: 'all' // 'all', 'with_students', 'empty'
  });

  // Cargar grupos al montar
  useEffect(() => {
    fetchGroups().catch(error => {
      console.error('[GroupsPage] Error loading groups:', error);
      toast.error('Error al cargar grupos');
    });
  }, [fetchGroups]);

  // Filtrar grupos con useMemo para evitar recalcular en cada render
  const filteredGroups = useMemo(() => {
    if (!Array.isArray(groups)) return [];
    
    let result = [...groups];
    
    // Filtro por búsqueda
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      result = result.filter(group => 
        group.name?.toLowerCase().includes(searchLower) ||
        group.course?.toLowerCase().includes(searchLower)
      );
    }
    
    // Filtro por curso
    if (filters.course) {
      result = result.filter(group => group.course === filters.course);
    }
    
    // Filtros adicionales
    if (filters.filter === 'with_students') {
      result = result.filter(group => (group.total_students || 0) > 0);
    } else if (filters.filter === 'empty') {
      result = result.filter(group => (group.total_students || 0) === 0);
    }
    
    return result;
  }, [groups, filters]);

  // Stats calculadas con useMemo
  const stats = useMemo(() => {
    if (!Array.isArray(groups)) {
      return { total_groups: 0, total_students: 0, total_subgrupos: 0 };
    }
    
    return {
      total_groups: groups.length,
      total_students: groups.reduce((sum, g) => sum + (g.total_students || 0), 0),
      total_subgrupos: groups.reduce((sum, g) => sum + (g.total_subgrupos || 0), 0)
    };
  }, [groups]);

  const handleCreate = () => {
    setSelectedGroup(null);
    setIsModalOpen(true);
  };

  const handleEdit = (group) => {
    setSelectedGroup(group);
    setIsModalOpen(true);
  };

  const handleDelete = async (groupId) => {
    if (!window.confirm('¿Estás seguro de eliminar este grupo?')) return;

    try {
      await deleteGroup(groupId);
      toast.success('Grupo eliminado');
    } catch (error) {
      console.error('Error deleting group:', error);
      toast.error('Error al eliminar grupo');
    }
  };

  const handleViewDetails = (groupId) => {
    navigate(`/grupos/${groupId}`);
  };

  const handleModalClose = async (refresh) => {
    console.log('[GroupsPage] handleModalClose - refresh:', refresh);
    setIsModalOpen(false);
    setSelectedGroup(null);
    if (refresh) {
      console.log('[GroupsPage] Fetching groups...');
      await fetchGroups();
      console.log('[GroupsPage] Groups after fetch:', useGroupStore.getState().groups);
    }
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
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">Grupos</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Gestiona los grupos de estudiantes y sus asignaturas.
          </p>
        </header>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
              search
            </span>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full pl-10 pr-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-primary focus:border-primary text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
              placeholder="Buscar grupos..."
            />
          </div>
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-primary text-white rounded-lg font-medium flex items-center justify-center gap-2 hover:bg-primary/90 transition"
          >
            <span className="material-symbols-outlined">add_circle</span>
            <span>Nuevo grupo</span>
          </button>
        </div>

        {/* KPIs Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">KPIs</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
              <p className="text-gray-600 dark:text-gray-400">Total de grupos</p>
              <p className="text-4xl font-bold text-gray-900 dark:text-white mt-2">
                {stats.total_groups}
              </p>
            </div>
            <div className="bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
              <p className="text-gray-600 dark:text-gray-400">Estudiantes principales</p>
              <p className="text-4xl font-bold text-green-500 mt-2">{stats.total_students}</p>
            </div>
            <div className="bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
              <p className="text-gray-600 dark:text-gray-400">Participaciones en subgrupos</p>
              <p className="text-4xl font-bold text-blue-500 mt-2">{stats.total_subgrupos}</p>
            </div>
          </div>
        </section>

        {/* Groups Table */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Listado de grupos
          </h2>
          <div className="overflow-x-auto bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-800 rounded-lg">
            <table className="w-full text-left">
              <thead className="border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">Nombre</th>
                  <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">Curso</th>
                  <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">
                    Estudiantes
                  </th>
                  <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">
                    Asignaturas
                  </th>
                  <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">Estado</th>
                  <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredGroups.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-gray-500 dark:text-gray-400">
                      {groups.length === 0 ? 'No hay grupos. Crea tu primer grupo.' : 'No se encontraron grupos con los filtros aplicados.'}
                    </td>
                  </tr>
                ) : (
                  filteredGroups.map((group) => (
                    <tr
                      key={group.id}
                      className="border-b border-gray-200 dark:border-gray-800 hover:bg-primary/5 dark:hover:bg-primary/10 transition"
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: group.color }}
                          ></div>
                          <span className="text-gray-900 dark:text-white font-medium">
                            {group.name}
                          </span>
                        </div>
                      </td>
                      <td className="p-4 text-gray-500 dark:text-gray-400">{group.course}</td>
                      <td className="p-4 text-gray-500 dark:text-gray-400">
                        <div className="flex flex-col">
                          <span className="font-medium">{group.total_students || 0} principales</span>
                          <span className="text-sm text-blue-600">{group.total_subgrupos || 0} subgrupos</span>
                        </div>
                      </td>
                      <td className="p-4 text-gray-500 dark:text-gray-400">
                        {group.subject_count || 0}
                      </td>
                      <td className="p-4">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                            (group.total_students || 0) > 0
                              ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                              : 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200'
                          }`}
                        >
                          <span
                            className={`w-2 h-2 mr-2 rounded-full ${
                              (group.total_students || 0) > 0 ? 'bg-green-500' : 'bg-orange-500'
                            }`}
                          ></span>
                          {(group.total_students || 0) > 0 ? 'Con estudiantes' : 'Vacío'}
                        </span>
                      </td>
                      <td className="p-4 space-x-3">
                        <button
                          onClick={() => handleViewDetails(group.id)}
                          className="text-primary font-semibold hover:text-primary/80"
                        >
                          Ver detalles
                        </button>
                        <button
                          onClick={() => handleEdit(group)}
                          className="text-blue-600 hover:text-blue-500"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(group.id)}
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
        </section>
      </div>

      {/* Modal */}
      {isModalOpen && <GroupModal group={selectedGroup} onClose={handleModalClose} />}
    </div>
  );
};

export default GroupsPage;
