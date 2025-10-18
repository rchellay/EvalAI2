import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, Calendar, User, BookOpen, CheckCircle, AlertCircle, 
  Clock, TrendingUp, BarChart3, Eye, Edit3, MessageSquare 
} from 'lucide-react';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';

const EvidenciasCorreccion = ({ studentId }) => {
  const [evidencias, setEvidencias] = useState([]);
  const [estadisticas, setEstadisticas] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtroEstado, setFiltroEstado] = useState('');

  useEffect(() => {
    if (studentId) {
      cargarEvidencias();
      cargarEstadisticas();
    }
  }, [studentId, filtroEstado]);

  const cargarEvidencias = async () => {
    try {
      setLoading(true);
      const params = filtroEstado ? { status: filtroEstado } : {};
      const response = await api.get(`/correccion/evidencias/estudiante/${studentId}/`, { params });
      setEvidencias(response.data.evidences);
    } catch (err) {
      console.error('Error cargando evidencias:', err);
      setError('Error al cargar las evidencias de corrección');
    } finally {
      setLoading(false);
    }
  };

  const cargarEstadisticas = async () => {
    try {
      const response = await api.get(`/correccion/estadisticas/estudiante/${studentId}/`);
      setEstadisticas(response.data.statistics);
    } catch (err) {
      console.error('Error cargando estadísticas:', err);
    }
  };

  const getEstadoColor = (estado) => {
    const colores = {
      'pendiente': 'bg-yellow-100 text-yellow-800',
      'revisada': 'bg-blue-100 text-blue-800',
      'aprobada': 'bg-green-100 text-green-800',
      'necesita_mejora': 'bg-red-100 text-red-800'
    };
    return colores[estado] || 'bg-gray-100 text-gray-800';
  };

  const getEstadoIcono = (estado) => {
    const iconos = {
      'pendiente': Clock,
      'revisada': Eye,
      'aprobada': CheckCircle,
      'necesita_mejora': AlertCircle
    };
    return iconos[estado] || Clock;
  };

  const formatearFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Cargando evidencias...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          <span className="text-red-800">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Estadísticas generales */}
      {estadisticas && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="mr-2 h-5 w-5 text-blue-600" />
            Estadísticas de Corrección
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{estadisticas.total_corrections}</div>
              <div className="text-sm text-gray-600">Total Correcciones</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{estadisticas.average_score}</div>
              <div className="text-sm text-gray-600">Puntuación Promedio</div>
            </div>
            <div className="text-center p-3 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{estadisticas.total_errors}</div>
              <div className="text-sm text-gray-600">Errores Totales</div>
            </div>
            <div className="text-center p-3 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{estadisticas.recent_corrections_30_days}</div>
              <div className="text-sm text-gray-600">Últimos 30 días</div>
            </div>
          </div>
          
          {/* Tendencia de mejora */}
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Tendencia de mejora:</span>
              <div className={`flex items-center px-2 py-1 rounded-full text-sm ${
                estadisticas.improvement_trend === 'positive' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                <TrendingUp className="h-4 w-4 mr-1" />
                {estadisticas.improvement_trend === 'positive' ? 'Positiva' : 'Necesita mejora'}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Evidencias de Corrección</h3>
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los estados</option>
            <option value="pendiente">Pendiente</option>
            <option value="revisada">Revisada</option>
            <option value="aprobada">Aprobada</option>
            <option value="necesita_mejora">Necesita mejora</option>
          </select>
        </div>
      </div>

      {/* Lista de evidencias */}
      <div className="space-y-4">
        {evidencias.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No hay evidencias de corrección disponibles</p>
          </div>
        ) : (
          evidencias.map((evidencia) => {
            const EstadoIcono = getEstadoIcono(evidencia.status);
            return (
              <motion.div
                key={evidencia.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">
                      {evidencia.title}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {formatearFecha(evidencia.created_at)}
                      </div>
                      <div className="flex items-center">
                        <BookOpen className="h-4 w-4 mr-1" />
                        {evidencia.correction_type_display}
                      </div>
                      {evidencia.subject_name && (
                        <div className="flex items-center">
                          <FileText className="h-4 w-4 mr-1" />
                          {evidencia.subject_name}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className={`flex items-center px-3 py-1 rounded-full text-sm ${getEstadoColor(evidencia.status)}`}>
                    <EstadoIcono className="h-4 w-4 mr-1" />
                    {evidencia.status_display}
                  </div>
                </div>

                {/* Métricas de la corrección */}
                <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">{evidencia.error_count}</div>
                    <div className="text-xs text-gray-600">Errores</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {evidencia.correction_score ? evidencia.correction_score.toFixed(1) : 'N/A'}
                    </div>
                    <div className="text-xs text-gray-600">Puntuación</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {evidencia.statistics?.num_palabras || 0}
                    </div>
                    <div className="text-xs text-gray-600">Palabras</div>
                  </div>
                </div>

                {/* Resumen de errores */}
                {evidencia.error_summary && typeof evidencia.error_summary === 'object' && (
                  <div className="mb-4">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Tipos de errores encontrados:</h5>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(evidencia.error_summary).map(([tipo, cantidad]) => (
                        <span
                          key={tipo}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {tipo}: {cantidad}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Sugerencias de mejora */}
                {evidencia.improvement_suggestions && evidencia.improvement_suggestions.length > 0 && (
                  <div className="mb-4">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Sugerencias de mejora:</h5>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {evidencia.improvement_suggestions.map((sugerencia, index) => (
                        <li key={index}>{sugerencia}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Feedback del profesor */}
                {evidencia.teacher_feedback && (
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <h5 className="text-sm font-medium text-blue-900 mb-2 flex items-center">
                      <MessageSquare className="h-4 w-4 mr-1" />
                      Comentarios del profesor:
                    </h5>
                    <p className="text-sm text-blue-800">{evidencia.teacher_feedback}</p>
                  </div>
                )}

                {/* Respuesta del estudiante */}
                {evidencia.student_response && (
                  <div className="p-3 bg-green-50 rounded-lg">
                    <h5 className="text-sm font-medium text-green-900 mb-2 flex items-center">
                      <User className="h-4 w-4 mr-1" />
                      Respuesta del estudiante:
                    </h5>
                    <p className="text-sm text-green-800">{evidencia.student_response}</p>
                  </div>
                )}
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default EvidenciasCorreccion;
