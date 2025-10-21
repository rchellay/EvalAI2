import React, { useState } from 'react';
import { Trash2, RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';

const AdminCleanupPage = () => {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);

  const handleCleanup = async () => {
    if (!window.confirm('¿Estás seguro de que quieres limpiar los datos duplicados? Esta acción eliminará asignaturas repetidas.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/admin/cleanup-duplicates/');
      setReport(response.data);
      toast.success('✅ Limpieza completada exitosamente');
    } catch (error) {
      console.error('Error en limpieza:', error);
      toast.error('Error al ejecutar la limpieza');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">🛠️ Limpieza de Datos</h1>
          <p className="text-gray-600 mt-1">Herramienta para limpiar asignaturas duplicadas y verificar grupos</p>
        </div>

        {/* Card principal */}
        <div className="bg-white rounded-2xl shadow-md p-6 mb-6">
          <div className="flex items-start gap-4 mb-6">
            <div className="p-3 bg-blue-50 rounded-lg">
              <Trash2 className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Limpieza Automática</h2>
              <p className="text-gray-600 text-sm mb-4">
                Esta herramienta realizará las siguientes acciones:
              </p>
              <ul className="space-y-2 text-sm text-gray-700 mb-4">
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Eliminar asignaturas duplicadas (mismo nombre y horario)</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Crear el grupo "4to" si no existe</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Generar un reporte con las acciones realizadas</span>
                </li>
              </ul>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <div className="flex items-start">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-yellow-800">
                    <strong>Advertencia:</strong> Esta acción eliminará permanentemente las asignaturas duplicadas. 
                    Se conservará la versión más antigua de cada asignatura duplicada.
                  </div>
                </div>
              </div>

              <button
                onClick={handleCleanup}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <RefreshCw className="h-5 w-5 animate-spin" />
                    Procesando...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-5 w-5" />
                    Ejecutar Limpieza
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Reporte */}
        {report && (
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
              Reporte de Limpieza
            </h3>

            <div className="space-y-4">
              {/* Usuario */}
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Usuario:</p>
                <p className="text-lg font-semibold text-gray-900">{report.user}</p>
              </div>

              {/* Acciones realizadas */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Acciones realizadas:</h4>
                <div className="space-y-2">
                  {report.actions.map((action, index) => (
                    <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-900">{action}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Duplicados eliminados */}
              {report.duplicates_removed && report.duplicates_removed.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">
                    Asignaturas eliminadas ({report.duplicates_removed.length}):
                  </h4>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                    <ul className="space-y-1 text-sm text-gray-700">
                      {report.duplicates_removed.map((item, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-gray-400 mr-2">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Resumen */}
              {report.summary && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-blue-900 mb-3">Resumen actual:</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-900">{report.summary.total_asignaturas}</p>
                      <p className="text-xs text-blue-700">Asignaturas</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-900">{report.summary.total_grupos}</p>
                      <p className="text-xs text-blue-700">Grupos</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-900">{report.summary.total_estudiantes}</p>
                      <p className="text-xs text-blue-700">Estudiantes</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Instrucciones */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">💡 Recomendaciones</h4>
          <ul className="space-y-1 text-sm text-blue-800">
            <li>• Ejecuta esta limpieza si notas asignaturas repetidas en tu lista</li>
            <li>• Después de la limpieza, recarga la página para ver los cambios</li>
            <li>• Este proceso solo afecta a tus datos, no a los de otros usuarios</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AdminCleanupPage;

