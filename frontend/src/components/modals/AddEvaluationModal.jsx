import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../../lib/axios';
import { toast } from 'react-hot-toast';

const AddEvaluationModal = ({ isOpen, onClose, studentId, onSuccess }) => {
  const [subjects, setSubjects] = useState([]);
  const [formData, setFormData] = useState({
    subject_id: '',
    title: '',
    grade: '',
    max_grade: 10,
    evaluation_type: 'exam',
    mood: '',
    date: new Date().toISOString().split('T')[0],
    notes: ''
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
    
    if (!formData.subject_id || !formData.title || !formData.grade) {
      toast.error('Por favor completa los campos obligatorios');
      return;
    }

    if (parseFloat(formData.grade) > parseFloat(formData.max_grade)) {
      toast.error('La nota no puede ser mayor que la nota máxima');
      return;
    }

    setLoading(true);
    try {
      await api.post(`/students/${studentId}/evaluations`, {
        subject_id: parseInt(formData.subject_id),
        title: formData.title,
        grade: parseFloat(formData.grade),
        max_grade: parseFloat(formData.max_grade),
        evaluation_type: formData.evaluation_type,
        mood: formData.mood || null,
        date: formData.date,
        notes: formData.notes || null
      });
      
      toast.success('Evaluación añadida correctamente');
      onSuccess();
      onClose();
      setFormData({
        subject_id: '',
        title: '',
        grade: '',
        max_grade: 10,
        evaluation_type: 'exam',
        mood: '',
        date: new Date().toISOString().split('T')[0],
        notes: ''
      });
    } catch (error) {
      console.error('Error adding evaluation:', error);
      toast.error('Error al añadir la evaluación');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Nueva Evaluación
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
          
          {/* Asignatura */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Asignatura <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.subject_id}
              onChange={(e) => setFormData({ ...formData, subject_id: e.target.value })}
              required
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

          {/* Título y Tipo */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Título <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="ej: Examen Tema 3"
                required
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Tipo
              </label>
              <select
                value={formData.evaluation_type}
                onChange={(e) => setFormData({ ...formData, evaluation_type: e.target.value })}
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
              >
                <option value="exam">Examen</option>
                <option value="homework">Tarea</option>
                <option value="project">Proyecto</option>
                <option value="participation">Participación</option>
                <option value="other">Otro</option>
              </select>
            </div>
          </div>

          {/* Nota y Nota Máxima */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Nota <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.grade}
                onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                placeholder="7.5"
                required
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Nota Máxima
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.max_grade}
                onChange={(e) => setFormData({ ...formData, max_grade: e.target.value })}
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
              />
            </div>
          </div>

          {/* Fecha y Estado de Ánimo */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Estado de Ánimo
              </label>
              <select
                value={formData.mood}
                onChange={(e) => setFormData({ ...formData, mood: e.target.value })}
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
              >
                <option value="">Sin especificar</option>
                <option value="confident">😊 Confiado</option>
                <option value="satisfied">🙂 Satisfecho</option>
                <option value="neutral">😐 Neutral</option>
                <option value="anxious">😰 Ansioso</option>
              </select>
            </div>
          </div>

          {/* Notas adicionales */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Notas Adicionales
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              placeholder="Observaciones sobre la evaluación..."
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
              {loading ? 'Guardando...' : 'Guardar Evaluación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddEvaluationModal;
