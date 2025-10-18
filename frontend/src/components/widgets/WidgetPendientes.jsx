import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../../lib/axios';

const WidgetPendientes = () => {
  const [pendientes, setPendientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPendientes();
  }, []);

  const fetchPendientes = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/evaluaciones_pendientes/');
      setPendientes(response.data.pendientes || []);
    } catch (err) {
      setError('Error al cargar evaluaciones pendientes');
      console.error('Error fetching pending evaluations:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (lastEvaluationDate) => {
    if (lastEvaluationDate === 'Nunca') return 'bg-red-100 text-red-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  const getStatusText = (lastEvaluationDate) => {
    if (lastEvaluationDate === 'Nunca') return 'Sin evaluar';
    return 'Evaluación antigua';
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

  return (
    <motion.div 
      className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6 hover:shadow-lg transition-all duration-300"
      whileHover={{ scale: 1.02 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="text-3xl mr-3">📚</div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Evaluaciones Pendientes</h3>
            <p className="text-sm text-slate-600">Sin evaluar esta semana</p>
          </div>
        </div>
        <div className="text-sm text-slate-500">
          {pendientes.length} pendiente{pendientes.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Lista de pendientes */}
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {pendientes.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <div className="text-4xl mb-2">✅</div>
            <p>¡Todos los alumnos están al día!</p>
            <p className="text-sm">No hay evaluaciones pendientes</p>
          </div>
        ) : (
          pendientes.map((pendiente, index) => (
            <motion.div
              key={pendiente.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-1">
                    <h4 className="font-medium text-slate-800 mr-2">{pendiente.name}</h4>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(pendiente.last_evaluation_date)}`}>
                      {getStatusText(pendiente.last_evaluation_date)}
                    </span>
                  </div>
                  
                  <div className="text-sm text-slate-600 mb-1">
                    📚 {pendiente.group_name}
                  </div>
                  
                  <div className="text-xs text-slate-500">
                    Última evaluación: {pendiente.last_evaluation_date}
                    {pendiente.last_evaluation_score && (
                      <span className="ml-2 text-blue-600">
                        (Nota: {pendiente.last_evaluation_score}/10)
                      </span>
                    )}
                  </div>
                </div>
                
                <Link
                  to={`/alumnos/${pendiente.id}/evaluar`}
                  className="bg-blue-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                >
                  Evaluar
                </Link>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Botón Ver más */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <button className="w-full text-sm text-slate-600 hover:text-slate-800 transition-colors">
          Ver lista completa →
        </button>
      </div>
    </motion.div>
  );
};

export default WidgetPendientes;

