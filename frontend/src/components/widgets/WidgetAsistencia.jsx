import React, { useState } from 'react';
import api from '../../lib/axios';

const WidgetAsistencia = ({ studentId, subjectId, onAttendanceRecorded, titleClassName }) => {
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [motivo, setMotivo] = useState('');
  const [saving, setSaving] = useState(false);
  const [fechaClase, setFechaClase] = useState(new Date().toISOString().split('T')[0]);

  const handleStatusSelect = (status) => {
    setSelectedStatus(status);
    if (status === 'presente') {
      setMotivo(''); // Limpiar motivo si está presente
    }
  };

  const saveAttendance = async () => {
    if (!selectedStatus) {
      alert('Debes seleccionar un estado de asistencia');
      return;
    }

    if (selectedStatus === 'ausente' && !motivo.trim()) {
      alert('Debes especificar el motivo de la ausencia');
      return;
    }

    try {
      setSaving(true);
      const response = await api.post('/asistencias/', {
        alumnoId: studentId,
        asignaturaId: subjectId,
        fechaClase: fechaClase,
        presente: selectedStatus === 'presente',
        motivo: selectedStatus === 'ausente' ? motivo : ''
      });

      if (onAttendanceRecorded) {
        onAttendanceRecorded(response.data);
      }

      // Limpiar formulario
      setSelectedStatus(null);
      setMotivo('');

      alert('Asistencia registrada exitosamente');
    } catch (error) {
      console.error('Error registrando asistencia:', error);
      if (error.response?.status === 400 && error.response.data?.non_field_errors) {
        alert('Ya existe un registro de asistencia para esta fecha y asignatura');
      } else {
        alert('Error al registrar la asistencia');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
        <span className="mr-2">✅</span>
        Registro de Asistencia
      </h3>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Fecha de la clase
        </label>
        <input
          type="date"
          value={fechaClase}
          onChange={(e) => setFechaClase(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Estado de asistencia
        </label>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleStatusSelect('presente')}
            className={`p-4 rounded-lg border-2 transition-all ${
              selectedStatus === 'presente'
                ? 'bg-green-100 border-green-500 text-green-800'
                : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">✅</div>
              <div className="font-medium">Presente</div>
            </div>
          </button>

          <button
            onClick={() => handleStatusSelect('ausente')}
            className={`p-4 rounded-lg border-2 transition-all ${
              selectedStatus === 'ausente'
                ? 'bg-red-100 border-red-500 text-red-800'
                : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">❌</div>
              <div className="font-medium">Ausente</div>
            </div>
          </button>
        </div>
      </div>

      {selectedStatus === 'ausente' && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Motivo de la ausencia
          </label>
          <select
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Seleccionar motivo...</option>
            <option value="enfermedad">Enfermedad</option>
            <option value="familiar">Motivos familiares</option>
            <option value="transporte">Problemas de transporte</option>
            <option value="personal">Motivos personales</option>
            <option value="otro">Otro</option>
          </select>
          {motivo === 'otro' && (
            <textarea
              placeholder="Especificar motivo..."
              className="w-full mt-2 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
              onChange={(e) => setMotivo(e.target.value)}
            />
          )}
        </div>
      )}

      <button
        onClick={saveAttendance}
        disabled={saving || !selectedStatus || (selectedStatus === 'ausente' && !motivo)}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {saving ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Registrando...
          </>
        ) : (
          <>
            <span className="mr-2">💾</span>
            Registrar Asistencia
          </>
        )}
      </button>

      <div className="mt-4 text-xs text-gray-500 text-center">
        📅 Registra la asistencia diaria para mantener un seguimiento preciso del progreso del alumno.
      </div>
    </div>
  );
};

export default WidgetAsistencia;