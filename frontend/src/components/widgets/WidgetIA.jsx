import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../../lib/axios';

const WidgetIA = () => {
  const [insights, setInsights] = useState(null);
  const [dataSummary, setDataSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/insights/');
      setInsights(response.data.insights);
      setDataSummary(response.data.data_summary);
    } catch (err) {
      setError('Error al generar insights');
      console.error('Error fetching insights:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshInsights = async () => {
    try {
      setRefreshing(true);
      const response = await api.post('/dashboard/insights/');
      setInsights(response.data.insights);
      setDataSummary(response.data.data_summary);
    } catch (err) {
      console.error('Error refreshing insights:', err);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6">
        <div className="text-center text-red-600">
          <div className="text-4xl mb-2">⚠️</div>
          <p>{error}</p>
          <button 
            onClick={fetchInsights}
            className="mt-2 bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6 hover:shadow-lg transition-all duration-300"
      whileHover={{ scale: 1.02 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="text-3xl mr-3">🧠</div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Insights IA del Aula</h3>
            <p className="text-sm text-slate-600">Análisis inteligente</p>
          </div>
        </div>
        <button
          onClick={refreshInsights}
          disabled={refreshing}
          className="bg-purple-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50 transition-colors"
        >
          {refreshing ? '🔄' : '🔄'} Actualizar
        </button>
      </div>

      {/* Contenido principal */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4 mb-4">
        <div className="flex items-start">
          <div className="text-2xl mr-3">📊</div>
          <div className="flex-1">
            <h4 className="font-medium text-slate-800 mb-2">Informe del Aula</h4>
            <p className="text-sm text-slate-700 leading-relaxed">
              {insights || 'Generando análisis del aula...'}
            </p>
          </div>
        </div>
      </div>

      {/* Resumen de datos */}
      {dataSummary && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="text-lg font-semibold text-blue-600">{dataSummary.total_students}</div>
            <div className="text-xs text-blue-800">Total alumnos</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-lg font-semibold text-green-600">{dataSummary.avg_score}/10</div>
            <div className="text-xs text-green-800">Promedio general</div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-3">
            <div className="text-lg font-semibold text-purple-600">{dataSummary.total_evaluations}</div>
            <div className="text-xs text-purple-800">Evaluaciones (30d)</div>
          </div>
          
          <div className="bg-orange-50 rounded-lg p-3">
            <div className="text-lg font-semibold text-orange-600">{dataSummary.attendance_rate}%</div>
            <div className="text-xs text-orange-800">Asistencia</div>
          </div>
        </div>
      )}

      {/* Indicador de estado */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          <span>IA activa - DeepSeek R1T2</span>
        </div>
        <span>Última actualización: Ahora</span>
      </div>

      {/* Botón Ver más */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <button className="w-full text-sm text-slate-600 hover:text-slate-800 transition-colors">
          Ver análisis detallado →
        </button>
      </div>
    </motion.div>
  );
};

export default WidgetIA;

