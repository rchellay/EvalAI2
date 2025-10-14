// frontend/src/pages/GroupsPage.jsx
import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import api from '../lib/axios';
import GroupModal from '../components/GroupModal';

const GroupsPage = () => {
  const navigate = useNavigate();
  const [groups, setGroups] = useState([]);
  const [stats, setStats] = useState({
    total_groups: 0,
    active_groups: 0,
    inactive_groups: 0
  });
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    course: '',
    filter: 'all' // 'all', 'active', 'inactive'
  });

  useEffect(() => {
    loadGroups();
    loadStats();
  }, [filters]);

  const loadGroups = async () => {
    console.log('[GroupsPage] Cargando grupos...');
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.course) params.course = filters.course;
      if (filters.filter === 'active') params.is_active = true;
      if (filters.filter === 'inactive') params.is_active = false;

      console.log('[GroupsPage] Petición a /groups con params:', params);
      const response = await api.get('/groups', { params });
      console.log('[GroupsPage] Respuesta recibida:', response.data);
      // Django REST Framework returns paginated data with "results" array
      const groupsData = response.data.results || response.data;
      console.log('[GroupsPage] Total grupos:', Array.isArray(groupsData) ? groupsData.length : 0);
      setGroups(Array.isArray(groupsData) ? groupsData : []);
    } catch (error) {
      console.error('[GroupsPage] ❌ Error loading groups:', error);
      console.error('[GroupsPage] Error response:', error.response?.data);
      console.error('[GroupsPage] Error status:', error.response?.status);
      toast.error('Error al cargar grupos');
      setGroups([]); // Ensure it's always an array
    } finally {
      setLoading(false);
    }
  };

  const loadStats = () => {
    const totalGroups = groups.length;
    const activeGroups = groups.filter(g => g.students && g.students.length > 0).length;
    setStats({ 
      total: totalGroups, 
      active: activeGroups, 
      inactive: totalGroups - activeGroups 
    });
  };

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
      await api.delete(`/groups/${groupId}`);
      toast.success('Grupo eliminado');
      loadGroups();
      loadStats();
    } catch (error) {
      console.error('Error deleting group:', error);
      toast.error('Error al eliminar grupo');
    }
  };

  const handleViewDetails = (groupId) => {
    navigate(`/grupos/${groupId}`);
  };

  const handleModalClose = (refresh) => {
    setIsModalOpen(false);
    setSelectedGroup(null);
    if (refresh) {
      loadGroups();
      loadStats();
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
              <p className="text-gray-600 dark:text-gray-400">Grupos activos</p>
              <p className="text-4xl font-bold text-green-500 mt-2">{stats.active_groups}</p>
            </div>
            <div className="bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
              <p className="text-gray-600 dark:text-gray-400">Grupos inactivos</p>
              <p className="text-4xl font-bold text-orange-500 mt-2">{stats.inactive_groups}</p>
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
                {groups.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-gray-500 dark:text-gray-400">
                      No hay grupos. Crea tu primer grupo.
                    </td>
                  </tr>
                ) : (
                  groups.map((group) => (
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
                        {group.student_count || 0}
                      </td>
                      <td className="p-4 text-gray-500 dark:text-gray-400">
                        {group.subject_count || 0}
                      </td>
                      <td className="p-4">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                            group.is_active
                              ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                              : 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200'
                          }`}
                        >
                          <span
                            className={`w-2 h-2 mr-2 rounded-full ${
                              group.is_active ? 'bg-green-500' : 'bg-orange-500'
                            }`}
                          ></span>
                          {group.is_active ? 'Activo' : 'Inactivo'}
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
