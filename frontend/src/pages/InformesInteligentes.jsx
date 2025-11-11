import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  User,
  Calendar,
  ChevronDown,
  FileText,
  TrendingUp,
  AlertCircle,
  Sparkles
} from 'lucide-react';
import api from '../lib/axios';
import GrupoReportView from '../components/informes/GrupoReportView';
import IndividualReportView from '../components/informes/IndividualReportView';

const InformesInteligentes = () => {
  const [niveles, setNiveles] = useState([]);
  const [grupos, setGrupos] = useState([]);
  const [students, setStudents] = useState([]);
  
  const [selectedNivel, setSelectedNivel] = useState(null);
  const [selectedGrupo, setSelectedGrupo] = useState(null);
  const [selectedTrimestre, setSelectedTrimestre] = useState('T1');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [reportMode, setReportMode] = useState(null); // 'grupo' | 'individual'

  const trimestres = [
    { id: 'T1', label: 'Trimestre 1', emoji: '🍂', months: 'Sep - Dic', dateRange: { start: '2024-09-01', end: '2024-12-31' } },
    { id: 'T2', label: 'Trimestre 2', emoji: '❄️', months: 'Ene - Mar', dateRange: { start: '2025-01-01', end: '2025-03-31' } },
    { id: 'T3', label: 'Trimestre 3', emoji: '🌸', months: 'Abr - Jun', dateRange: { start: '2025-04-01', end: '2025-06-30' } }
  ];

  // Load niveles on mount
  useEffect(() => {
    loadNiveles();
  }, []);

  // Load grupos when nivel changes
  useEffect(() => {
    if (selectedNivel) {
      loadGrupos(selectedNivel);
    }
  }, [selectedNivel]);

  // Load students when grupo changes
  useEffect(() => {
    if (selectedGrupo) {
      loadStudents(selectedGrupo);
    }
  }, [selectedGrupo]);

  // Update date range when trimestre changes
  useEffect(() => {
    const trimestre = trimestres.find(t => t.id === selectedTrimestre);
    if (trimestre) {
      setDateRange(trimestre.dateRange);
    }
  }, [selectedTrimestre]);

  const loadNiveles = async () => {
    try {
      const response = await api.get('/grupos/');
      const uniqueNiveles = [...new Set(response.data.map(g => g.course))];
      setNiveles(uniqueNiveles.map(nivel => ({ id: nivel, nombre: nivel })));
    } catch (error) {
      console.error('Error loading niveles:', error);
    }
  };

  const loadGrupos = async (nivel) => {
    try {
      const response = await api.get('/grupos/');
      const filtered = response.data.filter(g => g.course === nivel);
      setGrupos(filtered.map(g => ({ id: g.id, nombre: g.name, course: g.course })));
    } catch (error) {
      console.error('Error loading grupos:', error);
    }
  };

  const loadStudents = async (grupo) => {
    try {
      const response = await api.get(`/grupos/${grupo.id}/`);
      setStudents(response.data.alumnos || []);
    } catch (error) {
      console.error('Error loading students:', error);
    }
  };

  const handleGenerateGrupoReport = () => {
    if (!selectedGrupo || !selectedTrimestre) {
      alert('Selecciona un grupo y trimestre');
      return;
    }
    setReportMode('grupo');
  };

  const handleGenerateIndividualReport = () => {
    if (!selectedGrupo || !selectedTrimestre) {
      alert('Selecciona un grupo y trimestre');
      return;
    }
    setReportMode('individual');
  };

  const handleBack = () => {
    setReportMode(null);
    setSelectedStudent(null);
  };

  if (reportMode === 'grupo') {
    return (
      <GrupoReportView
        grupo={selectedGrupo}
        trimestre={selectedTrimestre}
        dateRange={dateRange}
        onBack={handleBack}
      />
    );
  }

  if (reportMode === 'individual') {
    return (
      <IndividualReportView
        grupo={selectedGrupo}
        students={students}
        selectedStudent={selectedStudent}
        onStudentSelect={setSelectedStudent}
        trimestre={selectedTrimestre}
        dateRange={dateRange}
        onBack={handleBack}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-2xl p-8 mb-8 text-white">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-white/20 rounded-xl">
              <FileText className="w-10 h-10" />
            </div>
            <div>
              <h1 className="text-4xl font-bold mb-2">📊 Informes Inteligentes 2.0</h1>
              <p className="text-blue-100 text-lg">
                Sistema de informes trimestrales con comentarios automáticos generados por IA
              </p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-blue-600" />
            Filtros de Selección
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Nivel Selector */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                1️⃣ Selecciona Nivel
              </label>
              <select
                value={selectedNivel || ''}
                onChange={(e) => {
                  setSelectedNivel(e.target.value);
                  setSelectedGrupo(null);
                  setStudents([]);
                }}
                className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              >
                <option value="">-- Selecciona un nivel --</option>
                {niveles.map(nivel => (
                  <option key={nivel.id} value={nivel.id}>
                    {nivel.nombre}
                  </option>
                ))}
              </select>
            </div>

            {/* Grupo Selector */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                2️⃣ Selecciona Grupo
              </label>
              <select
                value={selectedGrupo?.id || ''}
                onChange={(e) => {
                  const grupo = grupos.find(g => g.id === parseInt(e.target.value));
                  setSelectedGrupo(grupo);
                }}
                disabled={!selectedNivel}
                className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">-- Selecciona un grupo --</option>
                {grupos.map(grupo => (
                  <option key={grupo.id} value={grupo.id}>
                    {grupo.nombre}
                  </option>
                ))}
              </select>
            </div>

            {/* Trimestre Selector */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                3️⃣ Selecciona Trimestre
              </label>
              <div className="grid grid-cols-3 gap-2">
                {trimestres.map(trimestre => (
                  <button
                    key={trimestre.id}
                    onClick={() => setSelectedTrimestre(trimestre.id)}
                    className={`
                      px-3 py-3 rounded-xl font-semibold text-sm transition-all
                      ${selectedTrimestre === trimestre.id
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg scale-105'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    <div className="text-2xl mb-1">{trimestre.emoji}</div>
                    <div>{trimestre.id}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Date Range Display */}
          {dateRange.start && (
            <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <div className="flex items-center gap-2 text-blue-800">
                <Calendar className="w-5 h-5" />
                <span className="font-semibold">Rango de fechas:</span>
                <span>{dateRange.start} → {dateRange.end}</span>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        {selectedGrupo && selectedTrimestre && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-xl p-8"
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-purple-600" />
              Generar Informe
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Grupo Report */}
              <button
                onClick={handleGenerateGrupoReport}
                className="group relative p-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg hover:shadow-2xl transition-all hover:scale-105 text-white overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                <div className="relative z-10">
                  <Users className="w-12 h-12 mb-4" />
                  <h3 className="text-2xl font-bold mb-2">📊 Informe General de Grupo</h3>
                  <p className="text-blue-100 text-sm">
                    Análisis completo del rendimiento del grupo con estadísticas, tendencias y áreas de mejora
                  </p>
                  <div className="mt-4 flex items-center gap-2 text-blue-100 text-sm">
                    <FileText className="w-4 h-4" />
                    <span>Incluye exportación PDF y Excel</span>
                  </div>
                </div>
              </button>

              {/* Individual Report */}
              <button
                onClick={handleGenerateIndividualReport}
                className="group relative p-6 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg hover:shadow-2xl transition-all hover:scale-105 text-white overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                <div className="relative z-10">
                  <User className="w-12 h-12 mb-4" />
                  <h3 className="text-2xl font-bold mb-2">✅ Informe Individual del Alumno</h3>
                  <p className="text-purple-100 text-sm">
                    Informe personalizado con comentarios automáticos generados por IA para cada alumno
                  </p>
                  <div className="mt-4 flex items-center gap-2 text-purple-100 text-sm">
                    <Sparkles className="w-4 h-4" />
                    <span>Comentarios educativos con IA</span>
                  </div>
                </div>
              </button>
            </div>

            {/* Info Box */}
            <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="text-sm text-gray-700">
                  <p className="font-semibold mb-1">💡 Acerca de los Informes Inteligentes 2.0</p>
                  <p>
                    Los comentarios se generan automáticamente usando IA avanzada basándose en: evaluaciones del trimestre, 
                    tendencias vs trimestre anterior, autoevaluación del alumno, asistencia y registros de aula. 
                    Todos los comentarios son editables antes de exportar.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default InformesInteligentes;
