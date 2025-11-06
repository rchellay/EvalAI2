// frontend/src/components/GroupModal.jsx
import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import useGroupStore from '../stores/groupStore';

const GroupModal = ({ group, onClose }) => {
  const { createGroup, updateGroup } = useGroupStore();
  
  const [formData, setFormData] = useState({
    name: '',
    course: '', // Sin valor por defecto, forzar selección
    student_ids: [],
    subject_ids: []
  });
  const [loading, setLoading] = useState(false);

  const cursoOptions = [
    '1r ESO', '2n ESO', '3r ESO', '4t ESO',
    '1r BAT', '2n BAT',
    '1r Primària', '2n Primària', '3r Primària', '4t Primària', '5è Primària', '6è Primària'
  ];

  useEffect(() => {
    if (group) {
      setFormData({
        name: group.name || '',
        course: group.course || '4t ESO',
        student_ids: group.students ? group.students.map(s => s.id) : [],
        subject_ids: group.subjects ? group.subjects.map(s => s.id) : []
      });
    }
  }, [group]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    console.log('[GroupModal] handleSubmit - formData:', formData);

    try {
      const payload = {
        name: formData.name,
        course: formData.course
      };

      console.log('[GroupModal] Payload:', payload);

      if (group) {
        console.log('[GroupModal] Updating group:', group.id);
        await updateGroup(group.id, payload);
        toast.success('Grupo actualizado');
      } else {
        console.log('[GroupModal] Creating new group');
        const newGroup = await createGroup(payload);
        console.log('[GroupModal] Group created:', newGroup);
        toast.success('Grupo creado');
      }

      console.log('[GroupModal] Calling onClose(true)');
      onClose(true);
    } catch (error) {
      console.error('Error saving group:', error);
      const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Error al guardar grupo';
      toast.error(errorMsg);
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

          {/* Course */}
          <div>
            <label
              htmlFor="group-course"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Curso *
            </label>
            <select
              id="group-course"
              name="course"
              required
              value={formData.course}
              onChange={(e) => setFormData({ ...formData, course: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="">Selecciona un curso</option>
              {cursoOptions.map(curso => (
                <option key={curso} value={curso}>{curso}</option>
              ))}
            </select>
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
