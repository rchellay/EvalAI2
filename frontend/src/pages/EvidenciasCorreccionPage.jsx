import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, User, BookOpen, Calendar, TrendingUp } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import EvidenciasCorreccion from '../components/EvidenciasCorreccion';
import api from '../lib/axios';

const EvidenciasCorreccionPage = () => {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (studentId) {
      cargarEstudiante();
    }
  }, [studentId]);

  const cargarEstudiante = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/students/${studentId}/`);
      setStudent(response.data);
    } catch (err) {
      console.error('Error cargando estudiante:', err);
      setError('Error al cargar la información del estudiante');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando información del estudiante...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <User className="h-12 w-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200">
      {/* Header */}
      <div className="bg-white/70 backdrop-blur-sm shadow-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => navigate(-1)}
                className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Evidencias de Corrección
                </h1>
                <p className="text-gray-600">
                  Seguimiento del progreso de escritura de {student?.name}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm text-gray-600">Estudiante</div>
                <div className="font-semibold text-gray-900">{student?.name}</div>
              </div>
              {student?.photo && (
                <img
                  src={student.photo}
                  alt={student.name}
                  className="h-12 w-12 rounded-full object-cover"
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="max-w-7xl mx-auto p-6">
        {/* Información del estudiante */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg mr-4">
                <User className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Nombre</div>
                <div className="font-semibold text-gray-900">{student?.name}</div>
              </div>
            </div>
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg mr-4">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Curso</div>
                <div className="font-semibold text-gray-900">{student?.course || 'No especificado'}</div>
              </div>
            </div>
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg mr-4">
                <Calendar className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Asistencia</div>
                <div className="font-semibold text-gray-900">{student?.attendance_percentage}%</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Evidencias de corrección */}
        <EvidenciasCorreccion studentId={studentId} />
      </div>
    </div>
  );
};

export default EvidenciasCorreccionPage;
