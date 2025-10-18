import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../../lib/axios';

const WidgetRubricas = () => {
  const [rubricas, setRubricas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRubricas();
  }, []);

  const fetchRubricas = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/rubricas_estadisticas/');
      setRubricas(response.data.rubricas || []);
    } catch (err) {
      setError('Error al cargar rúbricas');
      console.error('Error fetching rubrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const getMaxUsage = () => {
    return Math.max(...rubricas.map(r => r.usage_count), 1);
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

  const maxUsage = getMaxUsage();

  return (
    <motion.div 
      className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6 hover:shadow-lg transition-all duration-300"
      whileHover={{ scale: 1.02 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="text-3xl mr-3">📈</div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Rúbricas más usadas</h3>
            <p className="text-sm text-slate-600">Ranking de frecuencia</p>
          </div>
        </div>
        <div className="text-sm text-slate-500">
          {rubricas.length} rúbrica{rubricas.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Lista de rúbricas */}
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {rubricas.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <div className="text-4xl mb-2">📋</div>
            <p>No hay rúbricas creadas</p>
            <Link 
              to="/rubricas/nueva"
              className="text-blue-600 hover:text-blue-800 text-sm mt-2 inline-block"
            >
              Crear primera rúbrica
            </Link>
          </div>
        ) : (
          rubricas.map((rubrica, index) => {
            const percentage = (rubrica.usage_count / maxUsage) * 100;
            return (
              <motion.div
                key={rubrica.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold mr-3">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-medium text-slate-800">{rubrica.name}</h4>
                      <p className="text-xs text-slate-600">{rubrica.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-blue-600">{rubrica.usage_count}</div>
                    <div className="text-xs text-slate-500">usos</div>
                  </div>
                </div>
                
                {/* Barra de progreso */}
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ delay: index * 0.1 + 0.3, duration: 0.5 }}
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                  />
                </div>
                
                <div className="text-xs text-slate-500 mt-1">
                  Creada: {rubrica.created_at}
                </div>
              </motion.div>
            );
          })
        )}
      </div>

      {/* Botón Ver más */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <Link 
          to="/rubricas" 
          className="w-full text-sm text-slate-600 hover:text-slate-800 transition-colors block text-center"
        >
          Ver todas las rúbricas →
        </Link>
      </div>
    </motion.div>
  );
};

export default WidgetRubricas;