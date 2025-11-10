import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const TeacherEvaluations = () => {
  const navigate = useNavigate();
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showQR, setShowQR] = useState(null);
  const [showResponses, setShowResponses] = useState(null);
  const [responses, setResponses] = useState([]);
  const [loadingResponses, setLoadingResponses] = useState(false);

  useEffect(() => {
    fetchEvaluations();
  }, []);

  const fetchEvaluations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/custom-evaluations/');
      setEvaluations(response.data);
    } catch (error) {
      console.error('Error cargando autoevaluaciones:', error);
      toast.error('Error al cargar autoevaluaciones');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    navigate('/teacher/evaluations/new');
  };

  const handleEdit = (id) => {
    navigate(`/teacher/evaluations/${id}/edit`);
  };

  const handleDuplicate = async (id) => {
    try {
      await api.post(`/custom-evaluations/${id}/duplicate/`);
      toast.success('Autoevaluación duplicada exitosamente');
      fetchEvaluations();
    } catch (error) {
      console.error('Error duplicando:', error);
      toast.error('Error al duplicar autoevaluación');
    }
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`¿Estás seguro de eliminar "${title}"?`)) {
      return;
    }

    try {
      await api.delete(`/custom-evaluations/${id}/`);
      toast.success('Autoevaluación eliminada');
      fetchEvaluations();
    } catch (error) {
      console.error('Error eliminando:', error);
      toast.error('Error al eliminar autoevaluación');
    }
  };

  const handleToggleActive = async (evaluation) => {
    try {
      await api.patch(`/custom-evaluations/${evaluation.id}/`, {
        is_active: !evaluation.is_active
      });
      toast.success(evaluation.is_active ? 'Autoevaluación desactivada' : 'Autoevaluación activada');
      fetchEvaluations();
    } catch (error) {
      console.error('Error actualizando estado:', error);
      toast.error('Error al actualizar estado');
    }
  };

  const handleShowQR = (evaluation) => {
    setShowQR(evaluation);
  };

  const handleDownloadQR = async (id, title) => {
    try {
      const response = await api.get(`/custom-evaluations/${id}/qr/`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `QR-${title}.png`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('QR descargado');
    } catch (error) {
      console.error('Error descargando QR:', error);
      toast.error('Error al descargar QR');
    }
  };

  const handleShowResponses = async (evaluation) => {
    try {
      setLoadingResponses(true);
      setShowResponses(evaluation);
      const response = await api.get(`/custom-evaluations/${evaluation.id}/responses/`);
      setResponses(response.data);
    } catch (error) {
      console.error('Error cargando respuestas:', error);
      toast.error('Error al cargar respuestas');
    } finally {
      setLoadingResponses(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">📝 Autoevaluaciones Personalizadas</h1>
        <button
          onClick={handleCreate}
          className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 flex items-center gap-2"
        >
          <span>➕</span>
          Crear Autoevaluación
        </button>
      </div>

      {evaluations.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="text-6xl mb-4">📋</div>
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No hay autoevaluaciones</h2>
          <p className="text-gray-500 mb-6">Crea tu primera autoevaluación personalizada con QR</p>
          <button
            onClick={handleCreate}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700"
          >
            ➕ Crear Primera Autoevaluación
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Título
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Grupo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Preguntas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Respuestas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Creado
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {evaluations.map((evaluation) => (
                <tr key={evaluation.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{evaluation.title}</div>
                    {evaluation.description && (
                      <div className="text-sm text-gray-500 truncate max-w-xs">{evaluation.description}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {evaluation.group_name || `Grupo ${evaluation.group}`}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {evaluation.questions?.length || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleShowResponses(evaluation)}
                      className="text-sm text-purple-600 hover:text-purple-800"
                    >
                      {evaluation.total_responses || 0} respuestas
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleToggleActive(evaluation)}
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        evaluation.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {evaluation.is_active ? '✓ Activa' : '✗ Inactiva'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(evaluation.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => handleShowQR(evaluation)}
                        className="text-purple-600 hover:text-purple-900"
                        title="Ver QR"
                      >
                        📱
                      </button>
                      <button
                        onClick={() => handleEdit(evaluation.id)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDuplicate(evaluation.id)}
                        className="text-green-600 hover:text-green-900"
                        title="Duplicar"
                      >
                        📑
                      </button>
                      <button
                        onClick={() => handleDelete(evaluation.id, evaluation.title)}
                        className="text-red-600 hover:text-red-900"
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal QR */}
      {showQR && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">📱 Código QR</h3>
              <button
                onClick={() => setShowQR(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="text-center">
              <h4 className="font-semibold mb-2">{showQR.title}</h4>
              <div className="bg-gray-100 p-4 rounded-lg mb-4">
                <img
                  src={`${api.defaults.baseURL}/custom-evaluations/${showQR.id}/qr/`}
                  alt="QR Code"
                  className="mx-auto"
                  style={{ width: '256px', height: '256px' }}
                />
              </div>
              <p className="text-sm text-gray-600 mb-4 break-all">
                {showQR.qr_url}
              </p>
              <button
                onClick={() => handleDownloadQR(showQR.id, showQR.title)}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 w-full"
              >
                ⬇️ Descargar QR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Respuestas */}
      {showResponses && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full my-8 mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">📊 Respuestas: {showResponses.title}</h3>
              <button
                onClick={() => setShowResponses(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {loadingResponses ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
              </div>
            ) : responses.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">📭</div>
                <p>No hay respuestas aún</p>
              </div>
            ) : (
              <div className="space-y-4">
                {responses.map((response) => (
                  <div key={response.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {response.student_name || `Estudiante ${response.student}`}
                        </h4>
                        <p className="text-sm text-gray-500">
                          {formatDate(response.submitted_at)}
                        </p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      {Object.entries(response.responses).map(([questionId, answer]) => {
                        const question = showResponses.questions.find(q => q.id === parseInt(questionId));
                        return (
                          <div key={questionId} className="bg-gray-50 p-3 rounded">
                            <p className="text-sm font-medium text-gray-700 mb-1">
                              {question?.text || `Pregunta ${questionId}`}
                            </p>
                            <p className="text-sm text-gray-900">{answer}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TeacherEvaluations;
