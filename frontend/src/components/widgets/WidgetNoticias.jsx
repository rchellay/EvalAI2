import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../../lib/axios';

const WidgetNoticias = () => {
  const [noticias, setNoticias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNoticias();
  }, []);

  const fetchNoticias = async () => {
    try {
      setLoading(true);
      const response = await api.get('/noticias/educacion/');
      setNoticias(response.data.noticias || []);
    } catch (err) {
      setError('Error al cargar noticias');
      console.error('Error fetching news:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const openNews = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
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
          <div className="text-3xl mr-3">🗞️</div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Noticias Educativas</h3>
            <p className="text-sm text-slate-600">Evaluación y educación - Actualización cada 2 días</p>
          </div>
        </div>
        <div className="text-sm text-slate-500">
          {noticias.length} noticia{noticias.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Lista de noticias */}
      <div className="space-y-4 max-h-80 overflow-y-auto">
        {noticias.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <div className="text-4xl mb-2">📰</div>
            <p>No hay noticias disponibles</p>
          </div>
        ) : (
          noticias.map((noticia, index) => (
            <motion.div
              key={noticia.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-50 rounded-lg p-4 hover:bg-slate-100 transition-colors cursor-pointer border-l-4 border-blue-500"
              onClick={() => openNews(noticia.url)}
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-slate-800 hover:text-blue-600 transition-colors flex-1 mr-3">
                  {noticia.title}
                </h4>
                <span className="text-xs text-slate-500 whitespace-nowrap">
                  {formatDate(noticia.date)}
                </span>
              </div>
              
              <p className="text-sm text-slate-600 mb-2 leading-relaxed">
                {noticia.summary}
              </p>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-blue-600 font-medium">
                  📰 {noticia.source}
                </span>
                <span className="text-xs text-slate-500">
                  Leer más →
                </span>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            <span>Evaluación educativa y pedagogía</span>
          </div>
          <span>🔄 Actualización cada 2 días</span>
        </div>
      </div>
    </motion.div>
  );
};

export default WidgetNoticias;

