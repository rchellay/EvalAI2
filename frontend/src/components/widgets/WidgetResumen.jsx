import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
// TEMPORALMENTE COMENTADO PARA VERCEL BUILD
// import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import api from '../../lib/axios';

const WidgetResumen = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/resumen/');
      setData(response.data);
    } catch (err) {
      setError('Error al cargar datos');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
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
        </div>
      </div>
    );
  }

  // Datos para el gráfico circular
  const chartData = [
    { name: 'Presentes', value: data.asistencias_hoy, color: '#10B981' },
    { name: 'Ausentes', value: data.total_asistencias_hoy - data.asistencias_hoy, color: '#EF4444' }
  ];

  return (
    <motion.div 
      className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6 hover:shadow-lg transition-all duration-300"
      whileHover={{ scale: 1.02 }}
    >
      {/* Header */}
      <div className="flex items-center mb-6">
        <div className="text-3xl mr-3">🧍‍♂️</div>
        <div>
          <h3 className="text-xl font-semibold text-slate-800">Resumen de Clase</h3>
          <p className="text-sm text-slate-600">Datos generales del día</p>
        </div>
      </div>

      {/* Contenido */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Estadísticas principales */}
        <div className="space-y-3">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-blue-600">{data.total_alumnos}</div>
            <div className="text-sm text-blue-800">Alumnos Activos</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-green-600">{data.total_asignaturas}</div>
            <div className="text-sm text-green-800">Asignaturas</div>
          </div>
        </div>

        {/* Gráfico circular */}
        <div className="flex items-center justify-center">
          <ResponsiveContainer width="100%" height={120}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={30}
                outerRadius={50}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Estadísticas adicionales */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-purple-50 rounded-lg p-3">
          <div className="text-lg font-semibold text-purple-600">{data.evaluaciones_semana}</div>
          <div className="text-xs text-purple-800">Evaluaciones esta semana</div>
        </div>
        
        <div className="bg-orange-50 rounded-lg p-3">
          <div className="text-lg font-semibold text-orange-600">{data.porcentaje_asistencia}%</div>
          <div className="text-xs text-orange-800">Asistencia hoy</div>
        </div>
      </div>

      {/* Botón Ver más */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <button className="w-full text-sm text-slate-600 hover:text-slate-800 transition-colors">
          Ver más detalles →
        </button>
      </div>
    </motion.div>
  );
};

export default WidgetResumen;

