import React, { useState, useEffect } from 'react';
import api from '../../lib/axios';

const WidgetObjetivos = ({ studentId, subjectId, onObjectiveCreated, titleClassName }) => {
  const [objectives, setObjectives] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    deadline: '', // Se auto-calculará según el trimestre
    trimestre: '1',
    status: 'pendiente'
  });
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  // Cargar objetivos existentes
  useEffect(() => {
    fetchObjectives();
  }, [studentId, subjectId]);

  const fetchObjectives = async () => {
    try {
      setLoading(true);
      const params = { student: studentId };
      if (subjectId) params.subject = subjectId;

      const response = await api.get('/objectives/', { params });
      const objectivesData = Array.isArray(response.data) ? response.data : [];
      setObjectives(objectivesData);
    } catch (error) {
      console.error('Error cargando objetivos:', error);
      setObjectives([]); // Asegurar que siempre sea array
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Si cambia el trimestre, auto-calcular la fecha límite
    if (name === 'trimestre') {
      const today = new Date();
      const year = today.getFullYear();
      let deadline = '';
      
      switch(value) {
        case '1': // Primer trimestre (septiembre-diciembre)
          deadline = `${year}-12-20`; // 20 de diciembre
          break;
        case '2': // Segundo trimestre (enero-marzo)
          deadline = `${year + 1}-03-20`; // 20 de marzo
          break;
        case '3': // Tercer trimestre (abril-junio)
          deadline = `${year + 1}-06-20`; // 20 de junio
          break;
        default:
          deadline = '';
      }
      
      setFormData(prev => ({
        ...prev,
        trimestre: value,
        deadline: deadline
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const saveObjective = async () => {
    if (!formData.title.trim() || !formData.trimestre) {
      alert('El título y trimestre son obligatorios');
      return;
    }

    try {
      setSaving(true);
      const objectiveData = {
        ...formData,
        student: studentId,
        subject: subjectId || null
      };

      const response = await api.post('/objectives/', objectiveData);

      setObjectives(prev => [response.data, ...(prev || [])]);
      setFormData({
        title: '',
        description: '',
        deadline: '',
        trimestre: '1',
        status: 'pendiente'
      });
      setShowForm(false);

      if (onObjectiveCreated) {
        onObjectiveCreated(response.data);
      }

      alert('Objetivo creado exitosamente');
    } catch (error) {
      console.error('Error creando objetivo:', error);
      alert('Error al crear el objetivo');
    } finally {
      setSaving(false);
    }
  };

  const updateObjectiveStatus = async (objectiveId, newStatus) => {
    try {
      await axios.patch(`/api/objectives/${objectiveId}/`, { status: newStatus });
      setObjectives(prev =>
        prev.map(obj =>
          obj.id === objectiveId ? { ...obj, status: newStatus } : obj
        )
      );
    } catch (error) {
      console.error('Error actualizando objetivo:', error);
      alert('Error al actualizar el objetivo');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pendiente': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'en_progreso': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'logrado': return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelado': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pendiente': return '⏳';
      case 'en_progreso': return '🔄';
      case 'logrado': return '✅';
      case 'cancelado': return '❌';
      default: return '❓';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pendiente': return 'Pendiente';
      case 'en_progreso': return 'En Progreso';
      case 'logrado': return 'Logrado';
      case 'cancelado': return 'Cancelado';
      default: return status;
    }
  };

  const safeObjectives = Array.isArray(objectives) ? objectives : [];

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-center py-4">Cargando objetivos...</div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold flex items-center"}>
          <span className="mr-2">🎯</span>
          Objetivos y Metas
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white py-1 px-3 rounded-md hover:bg-blue-700 text-sm"
        >
          {showForm ? 'Cancelar' : '+ Nuevo'}
        </button>
      </div>

      {showForm && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium mb-3">Nuevo Objetivo</h4>

          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Título *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="Ej: Mejorar cálculo mental"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descripción
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Describe el objetivo en detalle..."
                className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black bg-white placeholder-gray-500"
                rows={2}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trimestre *
                </label>
                <select
                  name="trimestre"
                  value={formData.trimestre}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white font-semibold"
                  required
                >
                  <option value="1">1º Trimestre (Sep-Dic)</option>
                  <option value="2">2º Trimestre (Ene-Mar)</option>
                  <option value="3">3º Trimestre (Abr-Jun)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estado
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white font-semibold placeholder-gray-500"
                >
                  <option value="pendiente">Pendiente</option>
                  <option value="en_progreso">En Progreso</option>
                  <option value="logrado">Logrado</option>
                  <option value="cancelado">Cancelado</option>
                </select>
              </div>
            </div>

            <button
              onClick={saveObjective}
              disabled={saving}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Guardando...' : '💾 Guardar Objetivo'}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {safeObjectives.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🎯</div>
            <p>No hay objetivos definidos aún</p>
            <p className="text-sm">Haz clic en "+ Nuevo" para añadir el primer objetivo</p>
          </div>
        ) : (
          safeObjectives.map(objective => (
            <div key={objective.id} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-800">{objective.title}</h4>
                <span className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(objective.status)}`}>
                  {getStatusIcon(objective.status)} {getStatusText(objective.status)}
                </span>
              </div>

              {objective.description && (
                <p className="text-sm text-gray-600 mb-2">{objective.description}</p>
              )}

              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>📅 Límite: {new Date(objective.deadline).toLocaleDateString()}</span>
                {objective.status !== 'logrado' && objective.status !== 'cancelado' && (
                  <select
                    value={objective.status}
                    onChange={(e) => updateObjectiveStatus(objective.id, e.target.value)}
                    className="text-xs p-1 border border-gray-300 rounded"
                  >
                    <option value="pendiente">Pendiente</option>
                    <option value="en_progreso">En Progreso</option>
                    <option value="logrado">Logrado</option>
                    <option value="cancelado">Cancelado</option>
                  </select>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default WidgetObjetivos;