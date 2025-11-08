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
  const [selectedEvidence, setSelectedEvidence] = useState(null);
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
      // Manejar tanto formato de array directo como objeto paginado
      const evidencesData = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      setEvidences(evidencesData);
    } catch (error) {
      console.error('Error cargando evidencias:', error);
      setEvidences([]); // Asegurar que siempre sea un array
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (evidenceId) => {
    if (!confirm('¿Estás seguro de que deseas eliminar esta evidencia?')) {
      return;
    }

    try {
      await api.delete(`/evidences/${evidenceId}/`);
      setEvidences(prev => prev.filter(e => e.id !== evidenceId));
      setSelectedEvidence(null); // Cerrar modal
      alert('Evidencia eliminada correctamente');
    } catch (error) {
      console.error('Error eliminando evidencia:', error);
      alert('Error al eliminar la evidencia. Inténtalo de nuevo.');
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

      <div className="space-y-4">
        {safeEvidences.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📎</div>
            <p>No hay evidencias subidas aún</p>
            <p className="text-sm">Haz clic en "Subir" para añadir la primera evidencia</p>
          </div>
        ) : (
          <>
            {/* Galería de imágenes */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {safeEvidences.map(evidence => (
                <div 
                  key={evidence.id} 
                  className="group relative bg-gray-50 rounded-lg overflow-hidden border border-gray-200 hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer"
                  onClick={() => setSelectedEvidence(evidence)}
                >
                  {/* Preview de imagen o icono de archivo */}
                  <div className="aspect-square flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 relative">
                    {evidence.file_type?.startsWith('image/') ? (
                      <>
                        <img 
                          src={evidence.file_url} 
                          alt={evidence.title}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        <div className="hidden w-full h-full items-center justify-center">
                          <span className="text-5xl">🖼️</span>
                        </div>
                        {/* Overlay al hover */}
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                          <span className="text-white text-sm font-medium">👁️ Ver</span>
                        </div>
                      </>
                    ) : evidence.file_type === 'application/pdf' ? (
                      <div className="flex flex-col items-center justify-center">
                        <span className="text-5xl mb-2">📄</span>
                        <span className="text-xs text-gray-600 font-medium">PDF</span>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center">
                        <span className="text-5xl mb-2">📎</span>
                        <span className="text-xs text-gray-600 font-medium">Archivo</span>
                      </div>
                    )}
                  </div>
                  
                  {/* Info del archivo */}
                  <div className="p-2 bg-white">
                    <h4 className="text-sm font-medium text-gray-800 truncate" title={evidence.title}>
                      {evidence.title}
                    </h4>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-gray-500">
                        {new Date(evidence.created_at).toLocaleDateString('es-ES', { 
                          day: 'numeric', 
                          month: 'short' 
                        })}
                      </span>
                      <span className="text-xs text-blue-600 font-medium">
                        {getFileIcon(evidence.file_type)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Modal de vista detallada */}
      {selectedEvidence && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedEvidence(null)}
        >
          <div 
            className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex justify-between items-start p-4 border-b">
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900">{selectedEvidence.title}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Subido el {new Date(selectedEvidence.created_at).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
              <button
                onClick={() => setSelectedEvidence(null)}
                className="ml-4 text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Contenido */}
            <div className="p-4">
              {/* Preview del archivo */}
              <div className="mb-4 bg-gray-50 rounded-lg flex items-center justify-center min-h-[400px] max-h-[600px] overflow-hidden">
                {selectedEvidence.file_type?.startsWith('image/') ? (
                  <img 
                    src={selectedEvidence.file_url} 
                    alt={selectedEvidence.title}
                    className="w-full h-full object-contain rounded"
                    style={{ maxHeight: '600px' }}
                  />
                ) : selectedEvidence.file_type === 'application/pdf' ? (
                  <div className="w-full h-full">
                    <iframe
                      src={selectedEvidence.file_url}
                      className="w-full h-full rounded"
                      style={{ minHeight: '500px' }}
                      title={selectedEvidence.title}
                    />
                  </div>
                ) : (
                  <div className="text-center p-8">
                    <span className="text-6xl mb-4 block">📎</span>
                    <p className="text-gray-600 mb-4">Archivo adjunto</p>
                    <a
                      href={selectedEvidence.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
                    >
                      � Descargar
                    </a>
                  </div>
                )}
              </div>

              {/* Descripción */}
              {selectedEvidence.description && (
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Descripción:</h4>
                  <p className="text-gray-600 text-sm leading-relaxed bg-gray-50 p-3 rounded">
                    {selectedEvidence.description}
                  </p>
                </div>
              )}

              {/* Información adicional */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Tipo:</span>
                  <span className="ml-2 text-gray-600">{getFileTypeText(selectedEvidence.file_type)}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Fecha:</span>
                  <span className="ml-2 text-gray-600">
                    {new Date(selectedEvidence.created_at).toLocaleDateString('es-ES')}
                  </span>
                </div>
              </div>

              {/* Botón de descarga y eliminar */}
              <div className="mt-6 flex justify-center gap-4">
                <a
                  href={selectedEvidence.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 font-medium"
                >
                  <span className="mr-2">📥</span>
                  Descargar archivo original
                </a>
                <button
                  onClick={() => handleDelete(selectedEvidence.id)}
                  className="inline-flex items-center bg-red-600 text-white px-6 py-3 rounded-md hover:bg-red-700 font-medium"
                >
                  <span className="mr-2">🗑️</span>
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WidgetEvidencias;