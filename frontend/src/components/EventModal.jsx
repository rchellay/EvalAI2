import { useState, useEffect } from 'react';
import { X, Calendar, Clock, Repeat, Tag, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';
import RecurrenceEditor from './RecurrenceEditor';

export default function EventModal({ isOpen, onClose, event, onSave, subjects = [] }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_at: '',
    end_at: '',
    all_day: false,
    event_type: 'task',
    subject_id: null,
    color: '#3B82F6',
    recurrence_rule: null,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  });

  const [loading, setLoading] = useState(false);
  const [showRecurrence, setShowRecurrence] = useState(false);

  useEffect(() => {
    if (event) {
      // Editing existing event
      setFormData({
        title: event.title || '',
        description: event.description || '',
        start_at: event.start || '',
        end_at: event.end || '',
        all_day: event.allDay || false,
        event_type: event.extendedProps?.event_type || 'task',
        subject_id: event.extendedProps?.subject_id || null,
        color: event.backgroundColor || '#3B82F6',
        recurrence_rule: event.extendedProps?.recurrence_rule || null,
        timezone: event.extendedProps?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone
      });
      setShowRecurrence(!!event.extendedProps?.recurrence_rule);
    } else {
      // Reset for new event
      setFormData({
        title: '',
        description: '',
        start_at: '',
        end_at: '',
        all_day: false,
        event_type: 'task',
        subject_id: null,
        color: '#3B82F6',
        recurrence_rule: null,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      });
      setShowRecurrence(false);
    }
  }, [event, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validation
      if (!formData.title.trim()) {
        toast.error('El título es obligatorio');
        setLoading(false);
        return;
      }

      if (!formData.start_at) {
        toast.error('La fecha de inicio es obligatoria');
        setLoading(false);
        return;
      }

      // Prepare payload
      const payload = {
        ...formData,
        start_at: new Date(formData.start_at).toISOString(),
        end_at: formData.end_at ? new Date(formData.end_at).toISOString() : null,
        recurrence_rule: showRecurrence ? formData.recurrence_rule : null
      };

      let response;
      if (event?.id) {
        // Update existing
        response = await api.put(`/calendar/events/${event.id}`, payload);
        toast.success('Evento actualizado');
      } else {
        // Create new
        response = await api.post('/calendar/events', payload);
        toast.success('Evento creado');
      }

      if (onSave) {
        onSave(response.data);
      }
      
      onClose();
    } catch (error) {
      console.error('Error saving event:', error);
      toast.error(error.response?.data?.detail || 'Error al guardar evento');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleRecurrenceChange = (rrule) => {
    setFormData(prev => ({ ...prev, recurrence_rule: rrule }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">
            {event ? 'Editar Evento' : 'Nuevo Evento'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="event-title" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <FileText size={16} />
              Título *
            </label>
            <input
              id="event-title"
              name="title"
              type="text"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Título del evento"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="event-description" className="text-sm font-medium text-gray-700 mb-2 block">
              Descripción
            </label>
            <textarea
              id="event-description"
              name="description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="3"
              placeholder="Descripción opcional"
            />
          </div>

          {/* Dates Row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="event-start" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Calendar size={16} />
                Fecha Inicio *
              </label>
              <input
                id="event-start"
                name="start_at"
                type="datetime-local"
                value={formData.start_at}
                onChange={(e) => handleChange('start_at', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label htmlFor="event-end" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Clock size={16} />
                Fecha Fin
              </label>
              <input
                id="event-end"
                name="end_at"
                type="datetime-local"
                value={formData.end_at}
                onChange={(e) => handleChange('end_at', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* All Day */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="all_day"
              checked={formData.all_day}
              onChange={(e) => handleChange('all_day', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="all_day" className="text-sm font-medium text-gray-700">
              Evento de día completo
            </label>
          </div>

          {/* Event Type & Subject Row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="event-type" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Tag size={16} />
                Tipo
              </label>
              <select
                id="event-type"
                name="event_type"
                value={formData.event_type}
                onChange={(e) => handleChange('event_type', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="task">Tarea</option>
                <option value="exam">Examen</option>
                <option value="assignment">Asignación</option>
                <option value="class">Clase</option>
                <option value="other">Otro</option>
              </select>
            </div>

            <div>
              <label htmlFor="event-subject" className="text-sm font-medium text-gray-700 mb-2 block">
                Asignatura
              </label>
              <select
                id="event-subject"
                name="subject_id"
                value={formData.subject_id || ''}
                onChange={(e) => handleChange('subject_id', e.target.value ? parseInt(e.target.value) : null)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Sin asignatura</option>
                {subjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Color Picker */}
          <div>
            <label htmlFor="event-color" className="text-sm font-medium text-gray-700 mb-2 block">
              Color
            </label>
            <div className="flex items-center gap-2">
              <input
                id="event-color"
                name="color"
                type="color"
                value={formData.color}
                onChange={(e) => handleChange('color', e.target.value)}
                className="w-12 h-12 border border-gray-300 rounded cursor-pointer"
              />
              <span className="text-sm text-gray-600">{formData.color}</span>
            </div>
          </div>

          {/* Recurrence Toggle */}
          <div>
            <button
              type="button"
              onClick={() => setShowRecurrence(!showRecurrence)}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <Repeat size={16} />
              {showRecurrence ? 'Ocultar repetición' : 'Añadir repetición'}
            </button>
          </div>

          {/* Recurrence Editor */}
          {showRecurrence && (
            <RecurrenceEditor
              value={formData.recurrence_rule}
              onChange={handleRecurrenceChange}
            />
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition-colors"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Guardando...' : event ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
