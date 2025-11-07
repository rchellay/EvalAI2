// frontend/src/pages/GroupDetailPage.jsx
import { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';
import useGroupStore, { 
  selectCurrentGroup, 
  selectAvailableStudents, 
  selectLoading, 
  selectGroupStudents,
  selectGroupCounts
} from '../stores/groupStore';
import CreateStudentModal from '../components/CreateStudentModal';
import GroupModal from '../components/GroupModal';

const GroupDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // Zustand store con selectores optimizados
  const group = useGroupStore(selectCurrentGroup);
  const availableStudents = useGroupStore(selectAvailableStudents);
  const loading = useGroupStore(selectLoading);
  const students = useGroupStore(selectGroupStudents);
  const counts = useGroupStore(selectGroupCounts);
  
  const { fetchGroupDetails, addStudentToGroup, createStudentInGroup, removeStudentFromGroup } = useGroupStore();
  
  const [showAddStudentModal, setShowAddStudentModal] = useState(false);
  const [showCreateStudentModal, setShowCreateStudentModal] = useState(false);
  const [showEditGroupModal, setShowEditGroupModal] = useState(false);
  const [selectedStudents, setSelectedStudents] = useState([]);

  // Handlers optimizados con useCallback (ANTES de early returns)
  const handleAddStudents = useCallback(async () => {
    if (selectedStudents.length === 0) {
      toast.error('Selecciona al menos un estudiante');
      return;
    }

    try {
      for (const studentId of selectedStudents) {
        await addStudentToGroup(id, studentId);
      }
      
      toast.success(`${selectedStudents.length} estudiante(s) añadido(s)`);
      setSelectedStudents([]);
      setShowAddStudentModal(false);
    } catch (error) {
      console.error('Error adding students:', error);
      toast.error('Error al añadir estudiantes');
    }
  }, [selectedStudents, id, addStudentToGroup]);

  const handleCreateStudentSuccess = useCallback(async (studentData) => {
    try {
      const newStudent = await createStudentInGroup(id, studentData);
      toast.success(`Estudiante ${newStudent.name} creado exitosamente`);
      setShowCreateStudentModal(false);
    } catch (error) {
      console.error('Error creating student:', error);
      toast.error('Error al crear estudiante');
    }
  }, [id, createStudentInGroup]);

  const handleRemoveStudent = useCallback(async (studentId, isSubgrupo = false) => {
    if (!window.confirm(`¿${isSubgrupo ? 'Quitar este estudiante del subgrupo?' : 'Quitar este estudiante del grupo?'}`)) return;

    try {
      await removeStudentFromGroup(id, studentId);
      toast.success('Estudiante removido');
    } catch (error) {
      console.error('Error removing student:', error);
      const errorMsg = error.response?.data?.error || 'Error al remover estudiante';
      toast.error(errorMsg);
    }
  }, [id, removeStudentFromGroup]);

  // Memoizar estudiantes disponibles con validación defensiva (ANTES de early returns)
  const studentsNotInGroup = useMemo(() => {
    // DEFENSIVE: Asegurar que sean arrays antes de operar
    const safeStudents = Array.isArray(students) ? students : [];
    const safeAvailable = Array.isArray(availableStudents) ? availableStudents : [];
    
    if (safeStudents.length === 0) return safeAvailable;
    
    const studentIds = new Set(safeStudents.map(s => s?.id).filter(Boolean));
    return safeAvailable.filter(student => student?.id && !studentIds.has(student.id));
  }, [students, availableStudents]);

  // Cargar datos solo una vez cuando cambia el ID
  useEffect(() => {
    fetchGroupDetails(id).catch((error) => {
      console.error('[GroupDetail] Error loading group:', error);
      toast.error('Error al cargar el grupo');
      navigate('/grupos');
    });
  }, [id, fetchGroupDetails, navigate]);

  // UN SOLO early return con TODAS las condiciones
  if (loading || !group || !group.name || !group.course) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm">
          <Link to="/grupos" className="text-primary hover:underline">
            Grupos
          </Link>
          <span className="mx-2 text-gray-500">/</span>
          <span className="text-gray-900 dark:text-white font-medium">{group.name}</span>
        </nav>

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold text-white"
              style={{ backgroundColor: group.color }}
            >
              {group.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">{group.name}</h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">{group.course}</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowEditGroupModal(true)}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
            >
              Editar grupo
            </button>
            <button
              onClick={() => navigate('/grupos')}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
            >
              Volver
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Estudiantes</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {group.students?.length || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Asignaturas</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {group.subjects?.length || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 p-6 rounded-xl">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Estado</p>
            <p
              className={`text-3xl font-bold mt-2 ${
                group.is_active ? 'text-green-500' : 'text-orange-500'
              }`}
            >
              {group.is_active ? 'Activo' : 'Inactivo'}
            </p>
          </div>
        </div>

        {/* Students Section */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Estudiantes ({group.students?.length || 0})
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate(`/estudiantes/nuevo?groupId=${id}`)}
                className="flex items-center gap-1 text-primary font-semibold text-sm hover:text-primary/80 transition"
              >
                <span className="material-symbols-outlined text-base">add_circle</span>
                <span>Nuevo</span>
              </button>
              <button
                onClick={() => setShowAddStudentModal(true)}
                className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 dark:bg-primary/20 text-primary font-medium text-sm rounded-lg hover:bg-primary/20 dark:hover:bg-primary/30 transition"
              >
                <span className="material-symbols-outlined text-base">person_add</span>
                <span>Agregar existente</span>
              </button>
            </div>
          </div>

          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
            {(() => {
              console.log('[GroupDetailPage] Rendering students section');
              console.log('[GroupDetailPage] group:', group);
              console.log('[GroupDetailPage] group?.students:', group?.students);
              console.log('[GroupDetailPage] students (selector):', students);
              console.log('[GroupDetailPage] students.length:', students?.length);
              return null;
            })()}
            {!students || students.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                No hay estudiantes en este grupo. Añade estudiantes para empezar.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
                {students.map((student) => (
                  <div
                    key={student.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md hover:border-primary transition cursor-pointer group relative"
                  >
                    <div 
                      onClick={() => navigate(`/estudiantes/${student.id}`)}
                      className="flex items-start justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold group-hover:bg-primary group-hover:text-white transition">
                          {(student.name || student.username || '?').charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white group-hover:text-primary transition">
                            {student.name || student.username || 'Sin nombre'}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {student.email || 'Sin email'}
                          </p>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveStudent(student.id);
                      }}
                      className="absolute top-3 right-3 text-red-600 hover:text-red-500 p-1 bg-white dark:bg-gray-800 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 transition"
                      title="Quitar del grupo"
                    >
                      <span className="material-symbols-outlined text-sm">close</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Subjects Section */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Asignaturas ({group.subjects?.length || 0})
            </h2>
          </div>

          <div className="bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
            {!group.subjects || group.subjects.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                Este grupo no está asociado a ninguna asignatura. Asigna este grupo desde la página de
                Asignaturas.
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-800">
                {group.subjects.map((subject) => (
                  <Link
                    key={subject.id}
                    to={`/asignaturas/${subject.id}`}
                    className="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: subject.color }}
                      ></div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{subject.name}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{subject.course}</p>
                      </div>
                    </div>
                    <span className="material-symbols-outlined text-gray-400">
                      chevron_right
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>

      {/* Add Students Modal */}
      {showAddStudentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Añadir estudiantes
              </h2>
              <button
                onClick={() => {
                  setShowAddStudentModal(false);
                  setSelectedStudents([]);
                }}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="p-6">
              {studentsNotInGroup.length === 0 ? (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                  Todos los estudiantes ya están en este grupo
                </p>
              ) : (
                <>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Selecciona los estudiantes que quieres añadir al grupo:
                  </p>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {studentsNotInGroup.map((student) => (
                      <label
                        key={student.id}
                        className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer border border-gray-200 dark:border-gray-700"
                      >
                        <input
                          type="checkbox"
                          checked={selectedStudents.includes(student.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedStudents([...selectedStudents, student.id]);
                            } else {
                              setSelectedStudents(
                                selectedStudents.filter((id) => id !== student.id)
                              );
                            }
                          }}
                          className="rounded border-gray-300 text-primary focus:ring-primary"
                        />
                        <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold">
                          {(student.name || student.username || '?').charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 dark:text-white">
                            {student.name || student.username || 'Sin nombre'}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {student.email || 'Sin email'}
                          </p>
                        </div>
                      </label>
                    ))}
                  </div>
                </>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => {
                  setShowAddStudentModal(false);
                  setSelectedStudents([]);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddStudents}
                disabled={selectedStudents.length === 0}
                className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Añadir {selectedStudents.length > 0 && `(${selectedStudents.length})`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Student Modal */}
      {showCreateStudentModal && (
        <CreateStudentModal
          groupId={id}
          onClose={() => setShowCreateStudentModal(false)}
          onSuccess={() => {
            loadGroupStudents(); // Recargar la lista de estudiantes
          }}
        />
      )}

      {/* Edit Group Modal */}
      {showEditGroupModal && (
        <GroupModal
          group={group}
          onClose={(refresh) => {
            setShowEditGroupModal(false);
            if (refresh) {
              loadGroupDetails();
              loadGroupStudents();
            }
          }}
        />
      )}
    </div>
  );
};

export default GroupDetailPage;
