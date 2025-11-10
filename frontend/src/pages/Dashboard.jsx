import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../lib/axios';

// Importar todos los widgets
import WidgetResumen from '../components/widgets/WidgetResumen';
import WidgetClases from '../components/widgets/WidgetClases';
import WidgetRendimiento from '../components/widgets/WidgetRendimiento';
import WidgetComentarios from '../components/widgets/WidgetComentarios';
import WidgetIA from '../components/widgets/WidgetIA';
import WidgetPendientes from '../components/widgets/WidgetPendientes';
import WidgetNoticias from '../components/widgets/WidgetNoticias';
import FloatingChatWidget from '../components/FloatingChatWidget';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Verificar autenticación y obtener datos del usuario
    const checkAuth = async () => {
      try {
        const response = await api.get('/auth/me');
        setUser(response.data);
        setLoading(false);
      } catch (err) {
        setError('No autorizado');
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Cargando Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Acceso Denegado</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <Link 
            to="/login" 
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Iniciar Sesión
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white/70 backdrop-blur-sm shadow-md border-b border-white/20"
      >
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-4xl font-bold text-slate-800 flex items-center">
            <span className="mr-3">🎓</span>
            {user?.first_name ? `Hola ${user.first_name}` : 'Panel del Profesor'}
          </h1>
          <p className="text-slate-600 mt-2">
            {user?.profile?.welcome_message || 'Bienvenido'} a tu centro de control educativo
          </p>
        </div>
      </motion.div>

      {/* Grid de Widgets */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Widget Resumen de Clase */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <WidgetResumen />
          </motion.div>

          {/* Widget Próximas Clases */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <WidgetClases />
          </motion.div>

          {/* Widget Evolución del Rendimiento */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <WidgetRendimiento />
          </motion.div>

          {/* Widget Comentarios Recientes */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <WidgetComentarios />
          </motion.div>

          {/* Widget Insights IA */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <WidgetIA />
          </motion.div>

          {/* Widget Evaluaciones Pendientes */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <WidgetPendientes />
          </motion.div>

          {/* Widget Noticias Educativas */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="md:col-span-2"
          >
            <WidgetNoticias />
          </motion.div>

        </div>
      </div>

      {/* Floating Chat Widget */}
      <FloatingChatWidget />
    </div>
  );
};

export default Dashboard;