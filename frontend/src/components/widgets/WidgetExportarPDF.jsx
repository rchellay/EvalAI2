import React, { useState } from 'react';
import api from '../../lib/axios';

const WidgetExportarPDF = ({ studentId, studentName, titleClassName }) => {
  const [exporting, setExporting] = useState(false);
  const [exportType, setExportType] = useState('full'); // 'full' o 'summary'
  const [includeObjectives, setIncludeObjectives] = useState(true);
  const [includeSelfEvaluations, setIncludeSelfEvaluations] = useState(true);
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  });

  const handleFullReportExport = async () => {
    try {
      setExporting(true);

      const params = new URLSearchParams({
        include_objectives: includeObjectives,
        include_self_evaluations: includeSelfEvaluations
      });

      const response = await api.get(`/alumnos/${studentId}/informe-pdf/?${params}`, {
        responseType: 'blob', // Importante para archivos binarios
      });

      // Crear URL del blob y descargar
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `informe_${studentName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('Error exportando PDF:', error);
      const errorMessage = error.response?.data?.error || 'Error al generar el PDF. Verifica tu conexión.';
      alert(errorMessage);
    } finally {
      setExporting(false);
    }
  };

  const handleSummaryExport = async () => {
    try {
      setExporting(true);

      const params = new URLSearchParams();
      if (dateRange.startDate) params.append('start_date', dateRange.startDate);
      if (dateRange.endDate) params.append('end_date', dateRange.endDate);

      const response = await api.get(`/alumnos/${studentId}/resumen-pdf/?${params}`, {
        responseType: 'blob',
      });

      // Crear URL del blob y descargar
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const dateSuffix = dateRange.startDate || dateRange.endDate
        ? `_${dateRange.startDate || 'inicio'}_a_${dateRange.endDate || 'hoy'}`
        : '_completo';
      link.setAttribute('download', `resumen_evaluaciones_${studentName.replace(/\s+/g, '_')}${dateSuffix}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('Error exportando resumen PDF:', error);
      const errorMessage = error.response?.data?.error || 'Error al generar el resumen PDF.';
      alert(errorMessage);
    } finally {
      setExporting(false);
    }
  };

  const handleExport = () => {
    if (exportType === 'full') {
      handleFullReportExport();
    } else {
      handleSummaryExport();
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
        <span className="mr-2">📄</span>
        Exportar Informes PDF
      </h3>

      <div className="space-y-4">
        {/* Tipo de exportación */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Informe
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                value="full"
                checked={exportType === 'full'}
                onChange={(e) => setExportType(e.target.value)}
                className="mr-2 h-5 w-5 border-2 border-gray-700 bg-white focus:ring-2 focus:ring-blue-500"
                style={{ accentColor: '#2563eb', backgroundColor: '#fff', borderColor: '#222' }}
              />
              <span className="text-sm">Informe Completo</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="summary"
                checked={exportType === 'summary'}
                onChange={(e) => setExportType(e.target.value)}
                className="mr-2 h-5 w-5 border-2 border-gray-700 bg-white focus:ring-2 focus:ring-blue-500"
                style={{ accentColor: '#2563eb', backgroundColor: '#fff', borderColor: '#222' }}
              />
              <span className="text-sm">Resumen de Evaluaciones</span>
            </label>
          </div>
        </div>

        {/* Opciones para informe completo */}
        {exportType === 'full' && (
          <div className="space-y-3">
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeObjectives}
                  onChange={(e) => setIncludeObjectives(e.target.checked)}
                  className="mr-2 h-5 w-5 border-2 border-gray-700 bg-white focus:ring-2 focus:ring-blue-500"
                  style={{ accentColor: '#2563eb', backgroundColor: '#fff', borderColor: '#222' }}
                />
                <span className="text-sm">Incluir objetivos</span>
              </label>
            </div>
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeSelfEvaluations}
                  onChange={(e) => setIncludeSelfEvaluations(e.target.checked)}
                  className="mr-2 h-5 w-5 border-2 border-gray-700 bg-white focus:ring-2 focus:ring-blue-500"
                  style={{ accentColor: '#2563eb', backgroundColor: '#fff', borderColor: '#222' }}
                />
                <span className="text-sm">Incluir autoevaluaciones</span>
              </label>
            </div>
          </div>
        )}

        {/* Opciones para resumen */}
        {exportType === 'summary' && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rango de Fechas (opcional)
              </label>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-600">Desde</label>
                  <input
                    type="date"
                    value={dateRange.startDate}
                    onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600">Hasta</label>
                  <input
                    type="date"
                    value={dateRange.endDate}
                    onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Botón de exportación */}
        <button
          onClick={handleExport}
          disabled={exporting}
          className="w-full bg-red-600 text-white py-3 px-4 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {exporting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Generando PDF...
            </>
          ) : (
            <>
              <span className="mr-2">📄</span>
              Exportar PDF
            </>
          )}
        </button>

        {/* Información adicional */}
        <div className="text-xs text-gray-500 text-center">
          💡 Los informes PDF incluyen evaluaciones, objetivos y estadísticas detalladas del estudiante.
        </div>
      </div>
    </div>
  );
};

export default WidgetExportarPDF;