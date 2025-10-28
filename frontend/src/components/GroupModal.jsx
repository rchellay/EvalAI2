// frontend/src/components/GroupModal.jsx
import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const GroupModal = ({ group, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    student_ids: [],
    subject_ids: []
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (group) {
      loadGroupDetails();
    }
  }, [group]);

  const loadGroupDetails = async () => {
    try {
      const response = await api.get(`/grupos/${group.id}`);
      const data = response.data;

      setFormData({
        name: data.name,
        student_ids: data.students ? data.students.map(s => s.id) : [],
        subject_ids: data.subjects ? data.subjects.map(s => s.id) : []
      });
    } catch (error) {
      console.error('Error loading group details:', error);
      toast.error('Error al cargar detalles del grupo');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        name: formData.name,
        student_ids: [],
        subject_ids: []
      };

      if (group) {
        await api.put(`/grupos/${group.id}`, payload);
        toast.success('Grupo actualizado');
      } else {
        await api.post('/grupos', payload);
        toast.success('Grupo creado');
      }

      onClose(true);
    } catch (error) {
      console.error('Error saving group:', error);
      toast.error(error.response?.data?.detail || 'Error al guardar grupo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {group ? 'Editar Grupo' : 'Nuevo Grupo'}
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
              htmlFor="group-name"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Nombre del grupo *
            </label>
            <input
              type="text"
              id="group-name"
              name="name"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Ej: 6A, Grupo de Refuerzo"
            />
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
              {loading ? 'Guardando...' : group ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default GroupModal;
