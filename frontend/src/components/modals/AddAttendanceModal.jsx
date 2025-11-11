import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../../lib/axios';
import { toast } from 'react-hot-toast';
import Switch from '../Switch';

const AddAttendanceModal = ({ isOpen, onClose, studentId, studentGroup, onSuccess }) => {
  const [subjects, setSubjects] = useState([]);
  const [formData, setFormData] = useState({
    subject_id: '',
    date: new Date().toISOString().split('T')[0],
    status: 'present',
    notes: '',
    register_all: false
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSubjects();
    }
  }, [isOpen]);

  const loadSubjects = async () => {
    try {
      const response = await api.get('/subjects/');
      const subjectsData = response.data.results || response.data;
      setSubjects(subjectsData || []);
    } catch (error) {
      console.error('Error loading subjects:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.register_all && !formData.subject_id) {
      toast.error('Por favor selecciona una asignatura o marca "Todas las asignaturas del día"');
      return;
    }

    setLoading(true);
    try {
      // Si register_all está marcado, no enviar subject_id
      const requestData = {
        date: formData.date,
        status: formData.status,
        notes: formData.notes || null
      };

      if (!formData.register_all && formData.subject_id) {
        requestData.subject_id = parseInt(formData.subject_id);
      }

      await api.post(`/students/${studentId}/attendance`, requestData);
      
      const message = formData.register_all 
        ? 'Asistencia registrada para todas las asignaturas del día'
        : 'Asistencia registrada correctamente';
      
      toast.success(message);
      onSuccess();
      onClose();
      setFormData({
        subject_id: '',
        date: new Date().toISOString().split('T')[0],
        status: 'present',
        notes: '',
        register_all: false
      });
    } catch (error) {
      console.error('Error adding attendance:', error);
      toast.error(error.response?.data?.error || 'Error al registrar la asistencia');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-lg w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Registrar Asistencia
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
          >
            <X size={20} className="text-slate-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          {/* Opción de registrar todas las asignaturas */}
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-slate-900 dark:text-white">
                  Registrar para todas las asignaturas del día
                </span>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  Marca esta opción para registrar la asistencia en todas las clases programadas para este día
                </p>
              </div>
              <Switch
                checked={formData.register_all}
                onChange={(checked) => setFormData({ 
                  ...formData, 
                  register_all: checked,
                  subject_id: checked ? '' : formData.subject_id
                })}
              />
            </div>
          </div>

          {/* Asignatura */}
          {!formData.register_all && (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Asignatura <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.subject_id}
                onChange={(e) => setFormData({ ...formData, subject_id: e.target.value })}
                required={!formData.register_all}
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
              >
                <option value="">Selecciona una asignatura</option>
                {subjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Fecha */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Fecha
            </label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
            />
          </div>

          {/* Estado */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Estado
            </label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { value: 'present', label: '✓ Presente', color: 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/40' },
                { value: 'absent', label: '✗ Ausente', color: 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/40' },
                { value: 'late', label: '⌚ Tarde', color: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 hover:bg-yellow-200 dark:hover:bg-yellow-900/40' },
                { value: 'excused', label: '📄 Justificado', color: 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/40' }
              ].map(status => (
                <button
                  key={status.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, status: status.value })}
                  className={`px-4 py-3 rounded-lg font-medium transition border-2 ${
                    formData.status === status.value 
                      ? 'border-blue-500 ' + status.color
                      : 'border-transparent ' + status.color
                  }`}
                >
                  {status.label}
                </button>
              ))}
            </div>
          </div>

          {/* Notas */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Notas (Opcional)
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              placeholder="Observaciones adicionales..."
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white resize-none"
            />
          </div>

          {/* Botones */}
          <div className="flex gap-3 justify-end pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Guardando...' : 'Guardar Asistencia'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddAttendanceModal;
