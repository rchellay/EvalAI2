import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../../lib/axios';
import { toast } from 'react-hot-toast';

const AddCommentModal = ({ isOpen, onClose, studentId, onSuccess }) => {
  const [subjects, setSubjects] = useState([]);
  const [formData, setFormData] = useState({
    content: '',
    comment_type: 'general',
    subject_id: ''
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
    
    if (!formData.content.trim()) {
      toast.error('El comentario no puede estar vacío');
      return;
    }

    setLoading(true);
    try {
      await api.post(`/students/${studentId}/comments`, {
        content: formData.content,
        comment_type: formData.comment_type,
        subject_id: formData.subject_id || null
      });
      
      toast.success('Comentario añadido correctamente');
      onSuccess();
      onClose();
      setFormData({ content: '', comment_type: 'general', subject_id: '' });
    } catch (error) {
      console.error('Error adding comment:', error);
      toast.error('Error al añadir el comentario');
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
            Nuevo Comentario
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
          
          {/* Tipo de comentario */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Tipo de Comentario
            </label>
            <select
              value={formData.comment_type}
              onChange={(e) => setFormData({ ...formData, comment_type: e.target.value })}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
            >
              <option value="general">General</option>
              <option value="behavior">Comportamiento</option>
              <option value="academic">Académico</option>
              <option value="progress">Progreso</option>
            </select>
          </div>

          {/* Asignatura (opcional) */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Asignatura (Opcional)
            </label>
            <select
              value={formData.subject_id}
              onChange={(e) => setFormData({ ...formData, subject_id: e.target.value })}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 dark:text-white"
            >
              <option value="">Sin asignatura específica</option>
              {subjects.map(subject => (
                <option key={subject.id} value={subject.id}>
                  {subject.name}
                </option>
              ))}
            </select>
          </div>

          {/* Contenido */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Comentario
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              rows={6}
              placeholder="Escribe el comentario aquí..."
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
              {loading ? 'Guardando...' : 'Guardar Comentario'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddCommentModal;
