import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Download,
  FileSpreadsheet,
  TrendingUp,
  TrendingDown,
  Minus,
  Users,
  AlertCircle,
  Award,
  Calendar,
  Target,
  BarChart3
} from 'lucide-react';
import LoadingSpinner from '../LoadingSpinner';

const GrupoReportView = ({ grupo, trimestre, dateRange, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadGroupReport();
  }, [grupo, trimestre, dateRange]);

  const loadGroupReport = async () => {
    setLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://evalai2.onrender.com';
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${API_URL}/api/informes/grupo/?grupo_id=${grupo.id}&fecha_inicio=${dateRange.start}&fecha_fin=${dateRange.end}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const data = await response.json();
      setReportData(data);
    } catch (error) {
      console.error('Error loading group report:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = async () => {
    setExporting(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://evalai2.onrender.com';
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${API_URL}/api/informes/grupo/pdf/?grupo_id=${grupo.id}&fecha_inicio=${dateRange.start}&fecha_fin=${dateRange.end}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `informe_grupo_${grupo.nombre}_${trimestre}.pdf`;
      a.click();
    } catch (error) {
      console.error('Error exporting PDF:', error);
    } finally {
      setExporting(false);
    }
  };

  const exportToExcel = async () => {
    setExporting(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://evalai2.onrender.com';
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${API_URL}/api/informes/grupo/excel/?grupo_id=${grupo.id}&fecha_inicio=${dateRange.start}&fecha_fin=${dateRange.end}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `datos_grupo_${grupo.nombre}_${trimestre}.xlsx`;
      a.click();
    } catch (error) {
      console.error('Error exporting Excel:', error);
    } finally {
      setExporting(false);
    }
  };

  const getTrendIcon = (trend) => {
    if (trend > 0) return <TrendingUp className="w-5 h-5 text-green-500" />;
    if (trend < 0) return <TrendingDown className="w-5 h-5 text-red-500" />;
    return <Minus className="w-5 h-5 text-gray-400" />;
  };

  const getDistributionColor = (category) => {
    const colors = {
      'Excelente': 'bg-green-500',
      'Notable': 'bg-blue-500',
      'Aprobado': 'bg-yellow-500',
      'Insuficiente': 'bg-red-500'
    };
    return colors[category] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600">No se pudieron cargar los datos del informe</p>
        <button onClick={onBack} className="mt-4 text-blue-600 hover:underline">
          Volver
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header with Back Button */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-xl shadow-md hover:shadow-lg hover:bg-gray-50 transition-all"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Volver</span>
        </button>

        <div className="flex gap-3">
          <button
            onClick={exportPDF}
            disabled={exporting}
            className="flex items-center gap-2 px-6 py-3 bg-red-500 text-white rounded-xl shadow-md hover:shadow-lg transition-all disabled:opacity-50"
          >
            <Download className="w-5 h-5" />
            <span>Exportar PDF</span>
          </button>
          <button
            onClick={exportExcel}
            disabled={exporting}
            className="flex items-center gap-2 px-6 py-3 bg-green-500 text-white rounded-xl shadow-md hover:shadow-lg transition-all disabled:opacity-50"
          >
            <FileSpreadsheet className="w-5 h-5" />
            <span>Exportar Excel</span>
          </button>
        </div>
      </div>

      {/* Report Title */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex items-center gap-4">
          <div className="p-4 bg-white/20 rounded-xl">
            <Users className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-3xl font-bold">Informe General de Grupo</h2>
            <p className="text-blue-100 mt-1">
              {grupo.nombre} • {trimestre} • {reportData.total_estudiantes} estudiantes
            </p>
          </div>
        </div>
      </div>

      {/* Global Performance */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          🍎 Rendimiento del Grupo
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Media Global */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
            <p className="text-sm text-gray-600 mb-2">Media Global del Grupo</p>
            <p className="text-4xl font-bold text-blue-600">
              {reportData.media_global?.toFixed(2) || 'N/A'}
            </p>
            <div className="flex items-center gap-2 mt-2 text-sm">
              {getTrendIcon(reportData.tendencia_global)}
              <span className={reportData.tendencia_global > 0 ? 'text-green-600' : reportData.tendencia_global < 0 ? 'text-red-600' : 'text-gray-600'}>
                {reportData.tendencia_global > 0 ? '+' : ''}{reportData.tendencia_global?.toFixed(2) || '0'} vs anterior
              </span>
            </div>
          </div>

          {/* Tasa de Aprobados */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6">
            <p className="text-sm text-gray-600 mb-2">Tasa de Aprobados</p>
            <p className="text-4xl font-bold text-green-600">
              {reportData.tasa_aprobados?.toFixed(0) || '0'}%
            </p>
            <p className="text-sm text-gray-600 mt-2">
              {reportData.total_aprobados || 0} de {reportData.total_estudiantes || 0} estudiantes
            </p>
          </div>

          {/* Asistencia Media */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6">
            <p className="text-sm text-gray-600 mb-2">Asistencia Media</p>
            <p className="text-4xl font-bold text-purple-600">
              {reportData.asistencia_media?.toFixed(0) || '0'}%
            </p>
            <p className="text-sm text-gray-600 mt-2">
              {reportData.total_horas_falta || 0} horas de ausencia total
            </p>
          </div>
        </div>

        {/* Distribution */}
        <div className="mt-6">
          <p className="text-sm font-medium text-gray-700 mb-3">Distribución de Notas</p>
          <div className="space-y-2">
            {reportData.distribucion_notas?.map((dist) => (
              <div key={dist.categoria} className="flex items-center gap-3">
                <div className="w-32 text-sm font-medium text-gray-700">
                  {dist.categoria}
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-8 overflow-hidden">
                  <div
                    className={`${getDistributionColor(dist.categoria)} h-full flex items-center justify-end px-3 text-white text-sm font-bold transition-all`}
                    style={{ width: `${dist.porcentaje}%` }}
                  >
                    {dist.porcentaje > 10 ? `${dist.porcentaje}%` : ''}
                  </div>
                </div>
                <div className="w-16 text-sm text-gray-600 text-right">
                  {dist.cantidad} alum.
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Performance by Subject */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Target className="w-6 h-6 text-purple-600" />
          📊 Media por Asignatura
        </h3>

        <div className="space-y-3">
          {reportData.medias_por_asignatura?.map((asignatura) => (
            <div key={asignatura.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
              <div className="flex-1">
                <p className="font-semibold text-gray-800">{asignatura.nombre}</p>
              </div>
              <div className="flex items-center gap-3">
                {getTrendIcon(asignatura.tendencia)}
                <span className="text-2xl font-bold text-blue-600">
                  {asignatura.media?.toFixed(2) || 'N/A'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Best and Worst Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Áreas Destacadas */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl shadow-xl p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Award className="w-6 h-6 text-green-600" />
            🚀 Áreas Destacadas
          </h3>
          <ul className="space-y-2">
            {reportData.areas_destacadas?.map((area, index) => (
              <li key={index} className="flex items-start gap-2 text-gray-700">
                <span className="text-green-600 font-bold">✓</span>
                <span>{area}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Áreas de Mejora */}
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl shadow-xl p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-orange-600" />
            🚨 Áreas de Mejora
          </h3>
          <ul className="space-y-2">
            {reportData.areas_mejora?.map((area, index) => (
              <li key={index} className="flex items-start gap-2 text-gray-700">
                <span className="text-orange-600 font-bold">!</span>
                <span>{area}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Autoevaluación del Grupo */}
      {reportData.autoevaluacion_grupo && (
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-600" />
            🧑‍🤝‍🧑 Autoevaluación Global del Grupo
          </h3>

          <div className="space-y-4">
            {reportData.autoevaluacion_grupo.competencias_principales?.map((comp) => (
              <div key={comp.nombre} className="flex items-center gap-4">
                <div className="flex-1">
                  <p className="font-medium text-gray-700">{comp.nombre}</p>
                </div>
                <div className="w-48 bg-gray-200 rounded-full h-6 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full flex items-center justify-center text-white text-xs font-bold"
                    style={{ width: `${(comp.media / 10) * 100}%` }}
                  >
                    {comp.media?.toFixed(1)}
                  </div>
                </div>
              </div>
            ))}

            {reportData.autoevaluacion_grupo.percepciones && (
              <div className="mt-6 p-4 bg-indigo-50 rounded-xl">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Principales Percepciones del Alumnado:
                </p>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {reportData.autoevaluacion_grupo.percepciones}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Attendance Summary */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Calendar className="w-6 h-6 text-red-600" />
          🚦 Faltas de Asistencia del Grupo
        </h3>

        <div className="mb-4 p-4 bg-red-50 rounded-xl">
          <p className="text-3xl font-bold text-red-600">
            {reportData.total_horas_falta || 0} horas
          </p>
          <p className="text-sm text-gray-600 mt-1">Total de ausencias del grupo</p>
        </div>

        {reportData.ranking_absentismo?.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">
              Estudiantes con Mayor Absentismo:
            </p>
            <div className="space-y-2">
              {reportData.ranking_absentismo.slice(0, 5).map((estudiante, index) => (
                <div key={estudiante.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                  <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center text-red-600 font-bold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-800">{estudiante.nombre}</p>
                  </div>
                  <div className="text-red-600 font-bold">
                    {estudiante.horas_falta}h
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default GrupoReportView;
