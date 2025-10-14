// frontend/src/components/SubjectModal.jsx
import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const DAYS_OF_WEEK = [
  { value: 'monday', label: 'Lunes' },
  { value: 'tuesday', label: 'Martes' },
  { value: 'wednesday', label: 'Miércoles' },
  { value: 'thursday', label: 'Jueves' },
  { value: 'friday', label: 'Viernes' },
  { value: 'saturday', label: 'Sábado' },
  { value: 'sunday', label: 'Domingo' }
];

const SubjectModal = ({ subject, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    color: '#137fec',
    description: '',
    group_ids: [],
    schedules: []
  });
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadGroups();
    if (subject) {
      // Load existing subject data
      loadSubjectDetails();
    }
  }, [subject]);

  const loadGroups = async () => {
    try {
      const response = await api.get('/groups');
      const groupsData = response.data.results || response.data;
      setGroups(Array.isArray(groupsData) ? groupsData : []);
    } catch (error) {
      console.error('Error loading groups:', error);
      setGroups([]);
      toast.error('Error al cargar grupos');
    }
  };

  const loadSubjectDetails = async () => {
    try {
      const response = await api.get(`/subjects/${subject.id}/`);
      const data = response.data;
      
      // Convert days array to schedules format
      const schedules = data.days?.map(day => ({
        day_of_week: day,
        start_time: data.start_time ? data.start_time.substring(0, 5) : '09:00',
        end_time: data.end_time ? data.end_time.substring(0, 5) : '10:00'
      })) || [];
      
      setFormData({
        name: data.name || '',
        color: data.color || '#137fec',
        description: data.description || '',
        group_ids: data.groups?.map(g => g.id) || [],
        schedules: schedules.length > 0 ? schedules : [{ day_of_week: 'monday', start_time: '09:00', end_time: '10:00' }]
      });
    } catch (error) {
      console.error('Error loading subject details:', error);
      console.error('Error response:', error.response?.data);
      toast.error('Error al cargar detalles de asignatura');
    }
  };

  const addSchedule = () => {
    setFormData({
      ...formData,
      schedules: [
        ...formData.schedules,
        { day_of_week: 'monday', start_time: '09:00', end_time: '10:00' }
      ]
    });
  };

  const removeSchedule = (index) => {
    const newSchedules = formData.schedules.filter((_, i) => i !== index);
    setFormData({ ...formData, schedules: newSchedules });
  };

  const updateSchedule = (index, field, value) => {
    const newSchedules = [...formData.schedules];
    newSchedules[index][field] = value;
    setFormData({ ...formData, schedules: newSchedules });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validación: debe haber al menos un horario
    if (!formData.schedules || formData.schedules.length === 0) {
      toast.error('Debe agregar al menos un horario');
      return;
    }
    
    setLoading(true);

    try {
      // Extract days and times from schedules
      const days = formData.schedules.map(s => s.day_of_week);
      const firstSchedule = formData.schedules[0];
      const startTime = firstSchedule.start_time ? firstSchedule.start_time + ':00' : '09:00:00';
      const endTime = firstSchedule.end_time ? firstSchedule.end_time + ':00' : '10:00:00';

      // Backend expects: name, days, start_time, end_time, color
      const payload = {
        name: formData.name,
        days: days,
        start_time: startTime,
        end_time: endTime,
        color: formData.color
      };

      if (subject) {
        await api.put(`/subjects/${subject.id}/`, payload);
        toast.success('Asignatura actualizada');
      } else {
        await api.post('/subjects/', payload);
        toast.success('Asignatura creada');
      }
      
      onClose(true);
    } catch (error) {
      console.error('Error saving subject:', error);
      toast.error(error.response?.data?.detail || 'Error al guardar asignatura');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {subject ? 'Editar Asignatura' : 'Nueva Asignatura'}
          </h2>
          <button
            onClick={() => onClose(false)}
            className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Info */}
          <div>
            <label
              htmlFor="subject-name"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Nombre de la asignatura *
            </label>
            <input
              type="text"
              id="subject-name"
              name="name"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Ej: Matemáticas Avanzadas"
            />
          </div>

          {/* Description */}
          <div>
            <label
              htmlFor="subject-description"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Descripción
            </label>
            <textarea
              id="subject-description"
              name="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Descripción opcional..."
            />
          </div>

          {/* Color */}
          <div>
            <label
              htmlFor="subject-color"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Color identificativo
            </label>
            <div className="flex items-center gap-3">
              <input
                type="color"
                id="subject-color"
                name="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="h-10 w-20 rounded border border-gray-300 dark:border-gray-600 cursor-pointer"
              />
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Se usará en el calendario
              </span>
            </div>
          </div>

          {/* Groups */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Grupos asociados
            </label>
            <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto p-2 border border-gray-300 dark:border-gray-600 rounded-lg">
              {!Array.isArray(groups) || groups.length === 0 ? (
                <p className="col-span-2 text-sm text-gray-500 dark:text-gray-400 text-center py-2">
                  No hay grupos disponibles
                </p>
              ) : (
                groups.map((group) => (
                  <label
                    key={group.id}
                    className="flex items-center gap-2 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={formData.group_ids.includes(group.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFormData({
                            ...formData,
                            group_ids: [...formData.group_ids, group.id]
                          });
                        } else {
                          setFormData({
                            ...formData,
                            group_ids: formData.group_ids.filter((id) => id !== group.id)
                          });
                        }
                      }}
                      className="rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {group.name}
                    </span>
                  </label>
                ))
              )}
            </div>
          </div>

          {/* Schedules */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Horarios de clase
              </label>
              <button
                type="button"
                onClick={addSchedule}
                className="flex items-center gap-1 px-3 py-1 text-sm bg-primary text-white rounded-lg hover:bg-primary/90"
              >
                <span className="material-symbols-outlined text-base">add</span>
                Añadir horario
              </button>
            </div>

            <div className="space-y-3">
              {formData.schedules.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                  No hay horarios definidos. Añade los días y horas en que se imparte esta asignatura.
                </p>
              ) : (
                formData.schedules.map((schedule, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <select
                      value={schedule.day_of_week}
                      onChange={(e) => updateSchedule(index, 'day_of_week', e.target.value)}
                      className="flex-1 px-3 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                    >
                      {DAYS_OF_WEEK.map((day) => (
                        <option key={day.value} value={day.value}>
                          {day.label}
                        </option>
                      ))}
                    </select>

                    <input
                      type="time"
                      value={schedule.start_time}
                      onChange={(e) => updateSchedule(index, 'start_time', e.target.value)}
                      className="w-28 px-3 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                    />

                    <span className="text-gray-500 dark:text-gray-400">-</span>

                    <input
                      type="time"
                      value={schedule.end_time}
                      onChange={(e) => updateSchedule(index, 'end_time', e.target.value)}
                      className="w-28 px-3 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                    />

                    <button
                      type="button"
                      onClick={() => removeSchedule(index)}
                      className="text-red-600 hover:text-red-500 dark:text-red-400"
                    >
                      <span className="material-symbols-outlined">delete</span>
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Guardando...' : subject ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SubjectModal;
