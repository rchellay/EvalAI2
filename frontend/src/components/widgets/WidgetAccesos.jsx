import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const WidgetAccesos = () => {
  const quickActions = [
    {
      id: 'evaluacion',
      icon: '➕',
      title: 'Crear Evaluación',
      description: 'Nueva evaluación rápida',
      link: '/evaluaciones/nueva',
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'informe',
      icon: '🧾',
      title: 'Generar Informe',
      description: 'Reportes y estadísticas',
      link: '/informes',
      color: 'from-green-500 to-green-600'
    },
    {
      id: 'rubrica',
      icon: '🧩',
      title: 'Crear Rúbrica',
      description: 'Nueva rúbrica de evaluación',
      link: '/rubricas/nueva',
      color: 'from-purple-500 to-purple-600'
    },
    {
      id: 'ajustes',
      icon: '⚙️',
      title: 'Ajustes',
      description: 'Configuración del sistema',
      link: '/ajustes',
      color: 'from-gray-500 to-gray-600'
    }
  ];

  return (
    <motion.div 
      className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-md p-6 hover:shadow-lg transition-all duration-300"
      whileHover={{ scale: 1.02 }}
    >
      {/* Header */}
      <div className="flex items-center mb-6">
        <div className="text-3xl mr-3">⚙️</div>
        <div>
          <h3 className="text-xl font-semibold text-slate-800">Accesos Rápidos</h3>
          <p className="text-sm text-slate-600">Atajos principales</p>
        </div>
      </div>

      {/* Grid de acciones */}
      <div className="grid grid-cols-2 gap-3">
        {quickActions.map((action, index) => (
          <motion.div
            key={action.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link
              to={action.link}
              className={`block bg-gradient-to-br ${action.color} rounded-lg p-4 text-white hover:shadow-lg transition-all duration-300`}
            >
              <div className="text-center">
                <div className="text-2xl mb-2">{action.icon}</div>
                <h4 className="font-medium text-sm mb-1">{action.title}</h4>
                <p className="text-xs opacity-90">{action.description}</p>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* Acciones adicionales */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="grid grid-cols-2 gap-2">
          <Link
            to="/calendario"
            className="text-center text-sm text-slate-600 hover:text-slate-800 transition-colors py-2 hover:bg-slate-50 rounded-lg"
          >
            📅 Calendario
          </Link>
          <Link
            to="/alumnos"
            className="text-center text-sm text-slate-600 hover:text-slate-800 transition-colors py-2 hover:bg-slate-50 rounded-lg"
          >
            👥 Alumnos
          </Link>
          <Link
            to="/asignaturas"
            className="text-center text-sm text-slate-600 hover:text-slate-800 transition-colors py-2 hover:bg-slate-50 rounded-lg"
          >
            📚 Asignaturas
          </Link>
          <Link
            to="/grupos"
            className="text-center text-sm text-slate-600 hover:text-slate-800 transition-colors py-2 hover:bg-slate-50 rounded-lg"
          >
            🏫 Grupos
          </Link>
        </div>
      </div>

      {/* Información adicional */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="text-center">
          <p className="text-xs text-slate-500">
            💡 Usa estos accesos para navegar rápidamente por la aplicación
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default WidgetAccesos;

