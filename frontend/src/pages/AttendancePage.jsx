// frontend/src/pages/AttendancePage.jsx
import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const AttendancePage = () => {
  const [subjects, setSubjects] = useState([]);
  const [allSubjects, setAllSubjects] = useState([]); // Todas las asignaturas
  const [groups, setGroups] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date().toISOString().split('T')[0]);

  // Función para obtener el día de la semana en inglés (para backend)
  const getDayOfWeekEnglish = (dateString) => {
    const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    const date = new Date(dateString + 'T12:00:00'); // Añadir hora para evitar problemas de zona horaria
    return dayNames[date.getDay()];
  };

  // Función para obtener el día de la semana en español (para UI)
  const getDayOfWeek = (dateString) => {
    const dayNamesSpanish = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
    const date = new Date(dateString + 'T12:00:00');
    return dayNamesSpanish[date.getDay()];
  };

  // Función para filtrar asignaturas por día
  const filterSubjectsByDate = (subjectsList, dateString) => {
    const dayOfWeek = getDayOfWeekEnglish(dateString);
    return subjectsList.filter(subject => 
      subject.days && Array.isArray(subject.days) && subject.days.includes(dayOfWeek)
    );
  };

  // Declarar funciones antes de los useEffect
  const loadSubjects = async () => {
    try {
      const response = await api.get('/subjects/');
      const subjectsData = response.data.results || response.data;
      const subjectsArray = Array.isArray(subjectsData) ? subjectsData : [];
      
      setAllSubjects(subjectsArray); // Guardar todas las asignaturas
      
      // Filtrar por fecha actual
      const filteredSubjects = filterSubjectsByDate(subjectsArray, currentDate);
      setSubjects(filteredSubjects);
    } catch (error) {
      console.error('Error loading subjects:', error);
      toast.error('Error al cargar asignaturas');
    }
  };

  const loadAllGroups = async () => {
    try {
      const response = await api.get('/groups/');
      const groupsData = response.data.results || response.data;
      setGroups(Array.isArray(groupsData) ? groupsData : []);
      
      // Auto-seleccionar primer grupo si solo hay uno
      if (groupsData.length === 1) {
        setSelectedGroup(groupsData[0].id.toString());
      }
    } catch (error) {
      console.error('Error loading groups:', error);
      toast.error('Error al cargar grupos');
    }
  };

  const loadGroupsBySubject = async (subjectId) => {
    try {
      // Obtener grupos que tienen esta asignatura
      const response = await api.get('/groups/');
      const groupsData = response.data.results || response.data;
      const filteredGroups = groupsData.filter(group =>
        group.subjects && Array.isArray(group.subjects) && group.subjects.some(s => s.id === parseInt(subjectId))
      );
      setGroups(filteredGroups);
      
      // Auto-seleccionar primer grupo si solo hay uno
      if (filteredGroups.length === 1) {
        setSelectedGroup(filteredGroups[0].id.toString());
      }
    } catch (error) {
      console.error('Error loading groups:', error);
      toast.error('Error al cargar grupos');
    }
  };

  const loadStudentsByGroup = async () => {
    setLoading(true);
    try {
      // Cargar estudiantes del grupo sin asignatura específica
      const response = await api.get(`/groups/${selectedGroup}/`);
      const groupData = response.data;
      
      if (groupData.students && Array.isArray(groupData.students)) {
        // Mapear estudiantes al formato esperado
        const studentsData = groupData.students.map(student => ({
          id: student.id,
          name: student.name,
          photo: student.photo,
          status: null,
          comment: null,
          attendance_id: null
        }));
        setStudents(studentsData);
      } else {
        setStudents([]);
      }
    } catch (error) {
      console.error('Error loading students:', error);
      toast.error('Error al cargar estudiantes');
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAttendanceToday = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        asignatura: selectedSubject,
        grupo: selectedGroup,
        fecha: currentDate
      });

      // Usar endpoint por_fecha en lugar de hoy para poder cambiar fecha
      const response = await api.get(`/asistencia/por_fecha/?${params}`);
      
      if (response.data.success) {
        setStudents(response.data.students);
      } else {
        toast.error(response.data.error || 'Error al cargar asistencia');
        setStudents([]);
      }
    } catch (error) {
      console.error('Error loading attendance:', error);
      toast.error('Error al cargar asistencia');
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = (studentId, newStatus) => {
    setStudents(prevStudents =>
      prevStudents.map(student =>
        student.id === studentId
          ? { ...student, status: student.status === newStatus ? null : newStatus }
          : student
      )
    );
  };

  const handleCommentChange = (studentId, comment) => {
    setStudents(prevStudents =>
      prevStudents.map(student =>
        student.id === studentId
          ? { ...student, comment }
          : student
      )
    );
  };

  const handleMarkAllPresent = () => {
    setStudents(prevStudents =>
      prevStudents.map(student => ({
        ...student,
        status: 'presente'
      }))
    );
    toast.success('Todos marcados como presentes');
  };

  const handleSaveAttendance = async () => {
    if (!selectedGroup) {
      toast.error('Selecciona un grupo');
      return;
    }

    // Filtrar solo estudiantes con estado definido
    const attendancesToSave = students
      .filter(student => student.status)
      .map(student => ({
        student: student.id,
        status: student.status,
        comment: student.comment || ''
      }));

    if (attendancesToSave.length === 0) {
      toast.error('Marca al menos un estudiante');
      return;
    }

    setSaving(true);
    try {
      const payload = {
        date: currentDate,
        attendances: attendancesToSave,
        group: parseInt(selectedGroup)
      };

      // Solo incluir subject si está seleccionado
      if (selectedSubject) {
        payload.subject = parseInt(selectedSubject);
      }

      console.log('Sending payload:', payload);
      const response = await api.post('/asistencia/registrar/', payload);
      
      if (response.data.success) {
        const message = selectedSubject 
          ? response.data.message
          : `${response.data.message} - Registrado para todas las asignaturas del día`;
        toast.success(message);
        
        // Recargar datos
        if (selectedSubject) {
          loadAttendanceToday();
        } else {
          loadStudentsByGroup();
        }
      } else {
        toast.error('Error al guardar asistencia');
      }
    } catch (error) {
      console.error('Error saving attendance:', error);
      console.error('Error response:', error.response?.data);
      
      // Extraer el mensaje de error apropiadamente
      let errorMsg = 'Error al guardar asistencia';
      
      if (error.response?.data) {
        const errorData = error.response.data;
        if (Array.isArray(errorData) && errorData.length > 0) {
          errorMsg = errorData[0];
        } else if (errorData.errors) {
          errorMsg = typeof errorData.errors === 'string' ? errorData.errors : JSON.stringify(errorData.errors);
        } else if (errorData.error) {
          errorMsg = errorData.error;
        } else if (typeof errorData === 'string') {
          errorMsg = errorData;
        }
      }
      
      toast.error(errorMsg, { duration: 5000 });
    } finally {
      setSaving(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'presente':
        return { icon: 'check_circle', color: 'text-green-500', bg: 'bg-green-50' };
      case 'ausente':
        return { icon: 'cancel', color: 'text-red-500', bg: 'bg-red-50' };
      case 'tarde':
        return { icon: 'schedule', color: 'text-yellow-500', bg: 'bg-yellow-50' };
      default:
        return { icon: 'radio_button_unchecked', color: 'text-gray-400', bg: 'bg-gray-50' };
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'presente':
        return 'Presente';
      case 'ausente':
        return 'Ausente';
      case 'tarde':
        return 'Tarde';
      default:
        return 'Sin marcar';
    }
  };

  // useEffect hooks
  // Cargar asignaturas al iniciar
  useEffect(() => {
    loadSubjects();
  }, []);

  // Filtrar asignaturas cuando cambia la fecha
  useEffect(() => {
    if (allSubjects.length > 0) {
      const filteredSubjects = filterSubjectsByDate(allSubjects, currentDate);
      setSubjects(filteredSubjects);
      
      // Si la asignatura seleccionada ya no está en el día, resetearla
      if (selectedSubject && Array.isArray(filteredSubjects) && !filteredSubjects.some(s => s.id === parseInt(selectedSubject))) {
        setSelectedSubject(null);
        toast.info('La asignatura seleccionada no tiene clase este día');
      }
    }
  }, [currentDate, allSubjects]);

  // Cargar grupos cuando se selecciona una asignatura o cargar todos si no hay selección
  useEffect(() => {
    if (selectedSubject) {
      loadGroupsBySubject(selectedSubject);
    } else {
      // Si no hay asignatura, cargar todos los grupos
      loadAllGroups();
    }
  }, [selectedSubject]);

  // Cargar estudiantes cuando se selecciona un grupo (asignatura es opcional)
  useEffect(() => {
    if (selectedGroup) {
      if (selectedSubject) {
        loadAttendanceToday();
      } else {
        // Si no hay asignatura, cargar estudiantes del grupo sin filtrar por asignatura
        loadStudentsByGroup();
      }
    } else {
      setStudents([]);
    }
  }, [selectedSubject, selectedGroup, currentDate]);

  // Calcular estadísticas
  const stats = {
    total: students.length,
    presentes: students.filter(s => s.status === 'presente').length,
    ausentes: students.filter(s => s.status === 'ausente').length,
    tardes: students.filter(s => s.status === 'tarde').length,
    sinMarcar: students.filter(s => !s.status).length
  };

  return (
    <div className="flex-1 p-4 md:p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Registro de Asistencia
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Marca la asistencia de forma rápida y eficiente
          </p>
        </div>

        {/* Selectores */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4 md:p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Selector de Asignatura */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Asignatura (Opcional)
              </label>
              <select
                value={selectedSubject || ''}
                onChange={(e) => {
                  setSelectedSubject(e.target.value);
                  setSelectedGroup(null);
                }}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="">📚 Todas las asignaturas del día</option>
                {subjects.length === 0 && (
                  <option disabled>No hay asignaturas programadas este día</option>
                )}
                {subjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
              {subjects.length === 0 && (
                <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
                  ⚠️ No hay asignaturas programadas para {getDayOfWeek(currentDate)}. Cambia la fecha.
                </p>
              )}
              {subjects.length > 0 && (
                <p className="mt-1 text-xs text-green-600 dark:text-green-400">
                  ✓ {subjects.length} asignatura{subjects.length !== 1 ? 's' : ''} disponible{subjects.length !== 1 ? 's' : ''} para {getDayOfWeek(currentDate)}
                </p>
              )}
            </div>

            {/* Selector de Grupo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Grupo *
              </label>
              <select
                value={selectedGroup || ''}
                onChange={(e) => setSelectedGroup(e.target.value)}
                disabled={groups.length === 0}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">Selecciona un grupo</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Selector de Fecha */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Fecha
              </label>
              <input
                type="date"
                value={currentDate}
                onChange={(e) => setCurrentDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>

          {/* Mensaje informativo cuando no hay asignatura seleccionada */}
          {!selectedSubject && selectedGroup && (
            <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">
                  info
                </span>
                <div>
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    Registro de Asistencia General
                  </p>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                    Se registrará la asistencia para <strong>todas las asignaturas programadas</strong> en la fecha seleccionada para este grupo.
                  </p>
                  <p className="text-xs text-blue-600 dark:text-blue-400 mt-2 italic">
                    ⚠️ Si el grupo no tiene asignaturas ese día, selecciona una asignatura específica arriba.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Estadísticas */}
        {students.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center shadow-sm">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Total</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center shadow-sm">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.presentes}</p>
              <p className="text-xs text-green-700 dark:text-green-300">Presentes</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 text-center shadow-sm">
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.ausentes}</p>
              <p className="text-xs text-red-700 dark:text-red-300">Ausentes</p>
            </div>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 text-center shadow-sm">
              <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.tardes}</p>
              <p className="text-xs text-yellow-700 dark:text-yellow-300">Tardes</p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-center shadow-sm">
              <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">{stats.sinMarcar}</p>
              <p className="text-xs text-gray-700 dark:text-gray-300">Sin marcar</p>
            </div>
          </div>
        )}

        {/* Botones de acción */}
        {students.length > 0 && (
          <div className="flex flex-wrap gap-3 mb-6">
            <button
              onClick={handleMarkAllPresent}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition text-sm font-medium"
            >
              <span className="material-symbols-outlined text-lg">done_all</span>
              Marcar todos presentes
            </button>
            <button
              onClick={handleSaveAttendance}
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <>
                  <span className="material-symbols-outlined text-lg animate-spin">refresh</span>
                  Guardando...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-lg">save</span>
                  Guardar cambios
                </>
              )}
            </button>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        )}

        {/* Lista de estudiantes */}
        {!loading && students.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
            {/* Tabla en desktop */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Estudiante
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Comentario
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {students.map((student) => {
                    const statusInfo = getStatusIcon(student.status);
                    return (
                      <tr key={student.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              {student.photo ? (
                                <img
                                  className="h-10 w-10 rounded-full object-cover"
                                  src={student.photo}
                                  alt={student.name}
                                />
                              ) : (
                                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                  <span className="text-primary font-semibold text-sm">
                                    {student.name.charAt(0).toUpperCase()}
                                  </span>
                                </div>
                              )}
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900 dark:text-white">
                                {student.name}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleStatusChange(student.id, 'presente')}
                              className={`p-2 rounded-lg transition ${
                                student.status === 'presente'
                                  ? 'bg-green-100 dark:bg-green-900/30'
                                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                              }`}
                              title="Presente"
                            >
                              <span className={`material-symbols-outlined text-2xl ${
                                student.status === 'presente' ? 'text-green-600' : 'text-gray-400'
                              }`}>
                                check_circle
                              </span>
                            </button>
                            <button
                              onClick={() => handleStatusChange(student.id, 'ausente')}
                              className={`p-2 rounded-lg transition ${
                                student.status === 'ausente'
                                  ? 'bg-red-100 dark:bg-red-900/30'
                                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                              }`}
                              title="Ausente"
                            >
                              <span className={`material-symbols-outlined text-2xl ${
                                student.status === 'ausente' ? 'text-red-600' : 'text-gray-400'
                              }`}>
                                cancel
                              </span>
                            </button>
                            <button
                              onClick={() => handleStatusChange(student.id, 'tarde')}
                              className={`p-2 rounded-lg transition ${
                                student.status === 'tarde'
                                  ? 'bg-yellow-100 dark:bg-yellow-900/30'
                                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                              }`}
                              title="Tarde"
                            >
                              <span className={`material-symbols-outlined text-2xl ${
                                student.status === 'tarde' ? 'text-yellow-600' : 'text-gray-400'
                              }`}>
                                schedule
                              </span>
                            </button>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <input
                            type="text"
                            value={student.comment || ''}
                            onChange={(e) => handleCommentChange(student.id, e.target.value)}
                            placeholder="Comentario opcional..."
                            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary focus:border-transparent"
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Cards en móvil */}
            <div className="md:hidden divide-y divide-gray-200 dark:divide-gray-700">
              {students.map((student) => {
                const statusInfo = getStatusIcon(student.status);
                return (
                  <div key={student.id} className="p-4">
                    {/* Estudiante */}
                    <div className="flex items-center mb-3">
                      <div className="flex-shrink-0 h-12 w-12">
                        {student.photo ? (
                          <img
                            className="h-12 w-12 rounded-full object-cover"
                            src={student.photo}
                            alt={student.name}
                          />
                        ) : (
                          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-primary font-semibold">
                              {student.name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {student.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {getStatusLabel(student.status)}
                        </p>
                      </div>
                    </div>

                    {/* Botones de estado */}
                    <div className="flex gap-2 mb-3">
                      <button
                        onClick={() => handleStatusChange(student.id, 'presente')}
                        className={`flex-1 p-3 rounded-lg flex items-center justify-center gap-2 transition ${
                          student.status === 'presente'
                            ? 'bg-green-100 dark:bg-green-900/30 ring-2 ring-green-500'
                            : 'bg-gray-100 dark:bg-gray-700'
                        }`}
                      >
                        <span className={`material-symbols-outlined ${
                          student.status === 'presente' ? 'text-green-600' : 'text-gray-500'
                        }`}>
                          check_circle
                        </span>
                      </button>
                      <button
                        onClick={() => handleStatusChange(student.id, 'ausente')}
                        className={`flex-1 p-3 rounded-lg flex items-center justify-center gap-2 transition ${
                          student.status === 'ausente'
                            ? 'bg-red-100 dark:bg-red-900/30 ring-2 ring-red-500'
                            : 'bg-gray-100 dark:bg-gray-700'
                        }`}
                      >
                        <span className={`material-symbols-outlined ${
                          student.status === 'ausente' ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          cancel
                        </span>
                      </button>
                      <button
                        onClick={() => handleStatusChange(student.id, 'tarde')}
                        className={`flex-1 p-3 rounded-lg flex items-center justify-center gap-2 transition ${
                          student.status === 'tarde'
                            ? 'bg-yellow-100 dark:bg-yellow-900/30 ring-2 ring-yellow-500'
                            : 'bg-gray-100 dark:bg-gray-700'
                        }`}
                      >
                        <span className={`material-symbols-outlined ${
                          student.status === 'tarde' ? 'text-yellow-600' : 'text-gray-500'
                        }`}>
                          schedule
                        </span>
                      </button>
                    </div>

                    {/* Comentario */}
                    <input
                      type="text"
                      value={student.comment || ''}
                      onChange={(e) => handleCommentChange(student.id, e.target.value)}
                      placeholder="Comentario opcional..."
                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Empty state */}
        {!loading && students.length === 0 && selectedSubject && selectedGroup && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-12 text-center">
            <span className="material-symbols-outlined text-6xl text-gray-400 mb-4">
              people_alt
            </span>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No hay estudiantes
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Este grupo no tiene estudiantes asignados
            </p>
          </div>
        )}

        {/* Initial state */}
        {!loading && !selectedSubject && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-12 text-center">
            <span className="material-symbols-outlined text-6xl text-primary mb-4">
              how_to_reg
            </span>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Comienza a pasar lista
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Selecciona una asignatura y grupo para registrar la asistencia
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AttendancePage;
