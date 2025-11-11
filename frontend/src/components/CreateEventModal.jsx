import React, { useState } from 'react';
import { X, Calendar, Clock, AlertCircle, Save } from 'lucide-react';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';
import Switch from './Switch';

const CreateEventModal = ({ isOpen, onClose, onEventCreated, initialDate = null }) => {
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    fecha: initialDate || new Date().toISOString().split('T')[0],
    hora_inicio: '',
    hora_fin: '',
    tipo: 'normal',
    todo_el_dia: true,
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.titulo || !formData.fecha) {
      toast.error('El título y la fecha son obligatorios');
      return;
    }

    setSaving(true);
    try {
      // Preparar datos para enviar
      const dataToSend = {
        titulo: formData.titulo,
        descripcion: formData.descripcion,
        fecha: formData.fecha,
        tipo: formData.tipo,
        todo_el_dia: formData.todo_el_dia,
      };

      // Solo enviar horas si no es todo el día
      if (!formData.todo_el_dia && formData.hora_inicio) {
        dataToSend.hora_inicio = formData.hora_inicio;
        dataToSend.hora_fin = formData.hora_fin || formData.hora_inicio;
      }

      const response = await api.post('/eventos/', dataToSend);
      
      toast.success(`✅ Evento "${formData.titulo}" creado correctamente`);
      
      if (onEventCreated) {
        onEventCreated(response.data);
      }
      
      // Resetear formulario y cerrar
      setFormData({
        titulo: '',
        descripcion: '',
        fecha: new Date().toISOString().split('T')[0],
        hora_inicio: '',
        hora_fin: '',
        tipo: 'normal',
        todo_el_dia: true,
      });
      onClose();
      
    } catch (error) {
      console.error('Error creando evento:', error);
      toast.error('Error al crear el evento');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Calendar className="mr-2 h-6 w-6 text-blue-600" />
            Crear Evento / Recordatorio
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition"
          >
            <X className="h-6 w-6 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          
          {/* Título */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🏷️ Nombre del evento *
            </label>
            <input
              type="text"
              value={formData.titulo}
              onChange={(e) => handleChange('titulo', e.target.value)}
              placeholder="Ej: Reunión de padres, Día festivo..."
              required
              minLength={3}
              className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-gray-400"
            />
          </div>

          {/* Fecha */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📅 Fecha *
            </label>
            <input
              type="date"
              value={formData.fecha}
              onChange={(e) => handleChange('fecha', e.target.value)}
              required
              className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Todo el día */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700">Todo el día</span>
            <Switch
              checked={formData.todo_el_dia}
              onChange={(checked) => handleChange('todo_el_dia', checked)}
            />
          </div>

          {/* Horario (solo si no es todo el día) */}
          {!formData.todo_el_dia && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🕐 Hora de inicio
                </label>
                <input
                  type="time"
                  value={formData.hora_inicio}
                  onChange={(e) => handleChange('hora_inicio', e.target.value)}
                  className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🕐 Hora de fin
                </label>
                <input
                  type="time"
                  value={formData.hora_fin}
                  onChange={(e) => handleChange('hora_fin', e.target.value)}
                  className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🗒️ Descripción (opcional)
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => handleChange('descripcion', e.target.value)}
              placeholder="Añade detalles sobre este evento..."
              rows={4}
              className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none placeholder:text-gray-400"
            />
          </div>

          {/* Tipo de evento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              🎯 Tipo de evento
            </label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { value: 'normal', label: 'Normal', color: 'blue', emoji: '📌', borderSelected: 'border-blue-600', bgSelected: 'bg-blue-50', textColor: 'text-blue-900' },
                { value: 'no_lectivo', label: 'Día no lectivo', color: 'red', emoji: '🔴', borderSelected: 'border-red-600', bgSelected: 'bg-red-50', textColor: 'text-red-900' },
                { value: 'reminder', label: 'Recordatorio', color: 'yellow', emoji: '⏰', borderSelected: 'border-yellow-600', bgSelected: 'bg-yellow-50', textColor: 'text-yellow-900' },
                { value: 'meeting', label: 'Reunión', color: 'purple', emoji: '👥', borderSelected: 'border-purple-600', bgSelected: 'bg-purple-50', textColor: 'text-purple-900' },
              ].map(tipo => (
                <button
                  key={tipo.value}
                  type="button"
                  onClick={() => handleChange('tipo', tipo.value)}
                  className={`p-3 rounded-lg border-2 transition text-left ${
                    formData.tipo === tipo.value
                      ? `${tipo.borderSelected} ${tipo.bgSelected}`
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className={`font-medium text-sm ${formData.tipo === tipo.value ? tipo.textColor : 'text-gray-700'}`}>
                    {tipo.emoji} {tipo.label}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Aviso para días no lectivos */}
          {formData.tipo === 'no_lectivo' && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-800">
                <strong>Día no lectivo:</strong> Este día se marcará en rojo en el calendario
                y no se podrán crear clases regulares en esta fecha.
              </div>
            </div>
          )}

          {/* Botones */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={!formData.titulo || !formData.fecha || saving}
              className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="h-5 w-5" />
                  Guardar Evento
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateEventModal;

