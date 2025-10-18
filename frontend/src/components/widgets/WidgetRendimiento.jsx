import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../../lib/axios';

const WidgetRendimiento = () => {
  const [chartData, setChartData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/evolucion/');
      setChartData(response.data.chart_data || []);
      setSummary(response.data.summary);
    } catch (err) {
      setError('Error al cargar datos');
      console.error('Error fetching performance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const analyzeTrends = async () => {
    try {
      setAnalyzing(true);
      const response = await api.post('/dashboard/analizar_tendencias/');
      setAnalysis(response.data.analysis);
    } catch (err) {
      console.error('Error analyzing trends:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-2">
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
          <div className="text-3xl mr-3">📊</div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Evolución del Rendimiento</h3>
            <p className="text-sm text-slate-600">Últimos 30 días</p>
          </div>
        </div>
        <button
          onClick={analyzeTrends}
          disabled={analyzing}
          className="bg-blue-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {analyzing ? '🔄' : '🪄'} Analizar
        </button>
      </div>

      {/* Gráfico */}
      <div className="h-48 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="date" 
              stroke="#64748b"
              fontSize={12}
              tickFormatter={(value) => new Date(value).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })}
            />
            <YAxis stroke="#64748b" fontSize={12} domain={[0, 10]} />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleDateString('es-ES')}
              formatter={(value) => [`${value}/10`, 'Promedio']}
            />
            <Line 
              type="monotone" 
              dataKey="avg_score" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Resumen estadístico */}
      {summary && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="text-lg font-semibold text-blue-600">{summary.avg_score_general}/10</div>
            <div className="text-xs text-blue-800">Promedio general</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-lg font-semibold text-green-600">{summary.total_evaluations}</div>
            <div className="text-xs text-green-800">Total evaluaciones</div>
          </div>
        </div>
      )}

      {/* Análisis de IA */}
      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-4"
        >
          <div className="flex items-start">
            <div className="text-2xl mr-3">🧠</div>
            <div>
              <h4 className="font-medium text-slate-800 mb-2">Análisis IA</h4>
              <p className="text-sm text-slate-700 leading-relaxed">{analysis}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Botón Ver más */}
      <div className="pt-4 border-t border-slate-200">
        <button className="w-full text-sm text-slate-600 hover:text-slate-800 transition-colors">
          Ver estadísticas detalladas →
        </button>
      </div>
    </motion.div>
  );
};

export default WidgetRendimiento;

