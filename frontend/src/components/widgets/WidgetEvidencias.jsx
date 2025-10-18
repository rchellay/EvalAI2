import React, { useState, useRef, useEffect } from 'react';
import api from '../../lib/axios';

const WidgetEvidencias = ({ studentId, subjectId, onEvidenceUploaded, titleClassName }) => {
  const [evidences, setEvidences] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    file: null
  });
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);

  // Cargar evidencias existentes
  useEffect(() => {
    fetchEvidences();
  }, [studentId, subjectId]);

  const fetchEvidences = async () => {
    try {
      setLoading(true);
      const params = { student: studentId };
      if (subjectId) params.subject = subjectId;

      const response = await api.get('/evidences/', { params });
      setEvidences(response.data);
    } catch (error) {
      console.error('Error cargando evidencias:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        file: file
      }));
    }
  };

  const uploadEvidence = async () => {
    if (!formData.title.trim() || !formData.file) {
      alert('El título y archivo son obligatorios');
      return;
    }

    // Validar tipo de archivo
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    if (!allowedTypes.includes(formData.file.type)) {
      alert('Solo se permiten archivos de imagen (JPG, PNG, GIF) y PDF');
      return;
    }

    // Validar tamaño (máximo 10MB)
    if (formData.file.size > 10 * 1024 * 1024) {
      alert('El archivo no puede superar los 10MB');
      return;
    }

    try {
      setUploading(true);

      const formDataToSend = new FormData();
      formDataToSend.append('student', studentId);
      if (subjectId) formDataToSend.append('subject', subjectId);
      formDataToSend.append('title', formData.title);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('file', formData.file);

      const response = await api.post('/evidences/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setEvidences(prev => [response.data, ...(prev || [])]);
      setFormData({
        title: '',
        description: '',
        file: null
      });
      setShowForm(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      if (onEvidenceUploaded) {
        onEvidenceUploaded(response.data);
      }

      alert('Evidencia subida exitosamente');
    } catch (error) {
      console.error('Error subiendo evidencia:', error);
      alert('Error al subir la evidencia');
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (fileType) => {
    if (fileType?.startsWith('image/')) return '🖼️';
    if (fileType === 'application/pdf') return '📄';
    return '📎';
  };

  const getFileTypeText = (fileType) => {
    if (fileType?.startsWith('image/')) return 'Imagen';
    if (fileType === 'application/pdf') return 'PDF';
    return 'Archivo';
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-center py-4">Cargando evidencias...</div>
      </div>
    );
  }

  const safeEvidences = Array.isArray(evidences) ? evidences : [];

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
          <span className="mr-2">🧾</span>
          Evidencias / Archivos
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white py-1 px-3 rounded-md hover:bg-blue-700 text-sm"
        >
          {showForm ? 'Cancelar' : '📎 Subir'}
        </button>
      </div>

      {showForm && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium mb-3">Nueva Evidencia</h4>

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
                placeholder="Ej: Trabajo del cuaderno de matemáticas"
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
                placeholder="Describe el contenido de la evidencia..."
                className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black bg-white placeholder-gray-500"
                rows={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Archivo *
              </label>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileChange}
                className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white placeholder-gray-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Formatos permitidos: JPG, PNG, GIF, PDF (máx. 10MB)
              </p>
              {formData.file && (
                <p className="text-sm text-green-600 mt-1">
                  Archivo seleccionado: {formData.file.name}
                </p>
              )}
            </div>

            <button
              onClick={uploadEvidence}
              disabled={uploading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Subiendo...
                </>
              ) : (
                '📤 Subir Evidencia'
              )}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {safeEvidences.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📎</div>
            <p>No hay evidencias subidas aún</p>
            <p className="text-sm">Haz clic en "Subir" para añadir la primera evidencia</p>
          </div>
        ) : (
          safeEvidences.map(evidence => (
            <div key={evidence.id} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-start space-x-3">
                <div className="text-2xl">
                  {getFileIcon(evidence.file_type)}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800">{evidence.title}</h4>
                  {evidence.description && (
                    <p className="text-sm text-gray-600 mt-1">{evidence.description}</p>
                  )}
                  <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                    <span>{getFileTypeText(evidence.file_type)}</span>
                    <span>{new Date(evidence.created_at).toLocaleDateString()}</span>
                  </div>
                  {evidence.file_url && (
                    <a
                      href={evidence.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block mt-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      👁️ Ver archivo
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default WidgetEvidencias;