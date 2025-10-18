import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../../lib/axios';

const WidgetComentarios = () => {
  const [comentarios, setComentarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchComentarios();
  }, []);

  const fetchComentarios = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/comentarios_recientes/?limit=5');
      setComentarios(response.data.comentarios || []);
    } catch (err) {
      setError('Error al cargar comentarios');
      console.error('Error fetching comments:', err);
    } finally {
      setLoading(false);
    }
  };

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
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
          <div className="text-3xl mr-3">💬</div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Comentarios Recientes</h3>
            <p className="text-sm text-slate-600">Últimas evaluaciones</p>
          </div>
        </div>
        <div className="text-sm text-slate-500">
          {comentarios.length} comentario{comentarios.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Lista de comentarios */}
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {comentarios.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <div className="text-4xl mb-2">💭</div>
            <p>No hay comentarios recientes</p>
          </div>
        ) : (
          comentarios.map((comentario, index) => (
            <motion.div
              key={comentario.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors"
            >
              <div className="flex items-start space-x-3">
                {/* Avatar */}
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-medium">
                    {getInitials(comentario.student_name)}
                  </div>
                </div>

                {/* Contenido */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <Link 
                      to={`/alumnos/${comentario.student_id}`}
                      className="font-medium text-slate-800 hover:text-blue-600 transition-colors"
                    >
                      {comentario.student_name}
                    </Link>
                    <span className="text-xs text-slate-500">{comentario.created_at}</span>
                  </div>
                  
                  <div className="text-sm text-slate-600 mb-1">
                    📚 {comentario.subject_name}
                  </div>
                  
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {comentario.text}
                  </p>
                  
                  <div className="text-xs text-slate-500 mt-1">
                    Por: {comentario.author_name}
                  </div>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Botón Ver más */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <button className="w-full text-sm text-slate-600 hover:text-slate-800 transition-colors">
          Ver todos los comentarios →
        </button>
      </div>
    </motion.div>
  );
};

export default WidgetComentarios;

