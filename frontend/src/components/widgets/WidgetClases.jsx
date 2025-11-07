import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../../lib/axios';

const WidgetClases = () => {
  const [clases, setClases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchClases();
  }, []);

  const fetchClases = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/proximas_clases/');
      console.log('[WidgetClases] Response:', response.data);
      setClases(response.data.clases || []);
    } catch (err) {
      setError('Error al cargar clases');
      console.error('Error fetching classes:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (time) => {
    if (!time || time === '--:--') return '--:--';
    return time;
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
          <div className="text-3xl mr-3">📅</div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Próximas Clases</h3>
            <p className="text-sm text-slate-600">Horario de hoy</p>
          </div>
        </div>
        <div className="text-sm text-slate-500">
          {clases.length} clase{clases.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Lista de clases */}
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {clases.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <div className="text-4xl mb-2">📚</div>
            <p>No hay clases programadas para hoy</p>
          </div>
        ) : (
          clases.map((clase, index) => (
            <motion.div
              key={clase.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors cursor-pointer border-l-4"
              style={{ borderLeftColor: clase.color || '#3B82F6' }}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-medium text-slate-800">{clase.subject_name}</div>
                  <div className="text-sm text-slate-600">{clase.group_name}</div>
                  {clase.description && (
                    <div className="text-xs text-slate-500 mt-1">{clase.description}</div>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-blue-600">
                    {formatTime(clase.start_time)} - {formatTime(clase.end_time)}
                  </div>
                  {clase.event_type && clase.event_type !== 'class' && (
                    <div className="text-xs text-slate-500 mt-1">
                      {clase.event_type === 'exam' ? '📝 Examen' : 
                       clase.event_type === 'meeting' ? '👥 Reunión' : 
                       clase.event_type === 'holiday' ? '🎉 Festivo' : '📅 Evento'}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Botón Ver más */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <Link 
          to="/calendario" 
          className="w-full text-sm text-slate-600 hover:text-slate-800 transition-colors block text-center"
        >
          Ver calendario completo →
        </Link>
      </div>
    </motion.div>
  );
};

export default WidgetClases;

