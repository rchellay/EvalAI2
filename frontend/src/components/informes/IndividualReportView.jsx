import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Download,
  FileSpreadsheet,
  Save,
  User,
  Calendar,
  MessageSquare,
  Sparkles,
  BookOpen,
  TrendingUp,
  AlertCircle,
  Loader,
  CheckCircle,
  Edit3
} from 'lucide-react';
import LoadingSpinner from '../LoadingSpinner';

const IndividualReportView = ({
  grupo,
  students,
  selectedStudent,
  onStudentSelect,
  trimestre,
  dateRange,
  onBack
}) => {
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [generatingAI, setGeneratingAI] = useState(false);
  const [aiComments, setAiComments] = useState({
    comentario_general: '',
    comentarios_asignaturas: {},
    comentario_autoevaluacion: '',
    comentario_asistencia: ''
  });
  const [editableComments, setEditableComments] = useState({});
  const [savingDraft, setSavingDraft] = useState(false);

  useEffect(() => {
    if (selectedStudent) {
      loadStudentReport();
    }
  }, [selectedStudent, trimestre, dateRange]);

  const loadStudentReport = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/informes/estudiante/?estudiante_id=${selectedStudent.id}&fecha_inicio=${dateRange.start}&fecha_fin=${dateRange.end}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const data = await response.json();
      setReportData(data);
      
      // Load existing comments if available
      if (data.comentarios_guardados) {
        setAiComments(data.comentarios_guardados);
        setEditableComments(data.comentarios_guardados);
      }
    } catch (error) {
      console.error('Error loading student report:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateAIComments = async () => {
    setGeneratingAI(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        'http://localhost:8000/api/informes/generar-comentarios-ia/',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            estudiante_id: selectedStudent.id,
            fecha_inicio: dateRange.start,
            fecha_fin: dateRange.end,
            trimestre: trimestre,
            datos_estudiante: reportData
          })
        }
      );
      const data = await response.json();
      setAiComments(data.comentarios);
      setEditableComments(data.comentarios);
    } catch (error) {
      console.error('Error generating AI comments:', error);
    } finally {
      setGeneratingAI(false);
    }
  };

  const saveDraft = async () => {
    setSavingDraft(true);
    try {
      const token = localStorage.getItem('token');
      await fetch(
        'http://localhost:8000/api/informes/guardar-borrador/',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            estudiante_id: selectedStudent.id,
            trimestre: trimestre,
            comentarios: editableComments
          })
        }
      );
      alert('Borrador guardado correctamente');
    } catch (error) {
      console.error('Error saving draft:', error);
      alert('Error al guardar el borrador');
    } finally {
      setSavingDraft(false);
    }
  };

  const exportPDF = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/informes/estudiante/pdf/?estudiante_id=${selectedStudent.id}&fecha_inicio=${dateRange.start}&fecha_fin=${dateRange.end}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ comentarios: editableComments })
        }
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `informe_${selectedStudent.nombre}_${trimestre}.pdf`;
      a.click();
    } catch (error) {
      console.error('Error exporting PDF:', error);
    }
  };

  const exportExcel = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/informes/estudiante/excel/?estudiante_id=${selectedStudent.id}&fecha_inicio=${dateRange.start}&fecha_fin=${dateRange.end}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `datos_${selectedStudent.nombre}_${trimestre}.xlsx`;
      a.click();
    } catch (error) {
      console.error('Error exporting Excel:', error);
    }
  };

  const handleCommentChange = (field, value, asignatura = null) => {
    setEditableComments(prev => {
      if (asignatura) {
        return {
          ...prev,
          comentarios_asignaturas: {
            ...prev.comentarios_asignaturas,
            [asignatura]: value
          }
        };
      }
      return {
        ...prev,
        [field]: value
      };
    });
  };

  if (!selectedStudent) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-md hover:shadow-lg transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Volver</span>
          </button>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <User className="w-6 h-6 text-purple-600" />
            Selecciona un Alumno
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {students.map(student => (
              <button
                key={student.id}
                onClick={() => onStudentSelect(student)}
                className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl hover:shadow-lg transition-all text-left"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-purple-200 rounded-full flex items-center justify-center">
                    <User className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">{student.nombre}</p>
                    <p className="text-sm text-gray-600">{grupo.nombre}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </motion.div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => onStudentSelect(null)}
          className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-md hover:shadow-lg transition-all"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Cambiar Alumno</span>
        </button>

        <div className="flex gap-3">
          <button
            onClick={saveDraft}
            disabled={savingDraft}
            className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-xl shadow-md hover:shadow-lg transition-all disabled:opacity-50"
          >
            {savingDraft ? <Loader className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
            <span>Guardar Borrador</span>
          </button>
          <button
            onClick={exportPDF}
            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-xl shadow-md hover:shadow-lg transition-all"
          >
            <Download className="w-5 h-5" />
            <span>Exportar PDF</span>
          </button>
          <button
            onClick={exportExcel}
            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-xl shadow-md hover:shadow-lg transition-all"
          >
            <FileSpreadsheet className="w-5 h-5" />
            <span>Exportar Excel</span>
          </button>
        </div>
      </div>

      {/* Student Header */}
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-white/20 rounded-xl">
              <User className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-3xl font-bold">✅ INFORME INDIVIDUAL: {selectedStudent.nombre}</h2>
              <p className="text-purple-100 mt-1">
                {grupo.nombre} • {trimestre}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Student Data */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          🔹 1. Datos del Alumno
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded-xl">
            <p className="text-sm text-gray-600 mb-1">Nombre</p>
            <p className="font-semibold text-gray-800">{selectedStudent.nombre}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-xl">
            <p className="text-sm text-gray-600 mb-1">Grupo</p>
            <p className="font-semibold text-gray-800">{grupo.nombre}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-xl">
            <p className="text-sm text-gray-600 mb-1">Trimestre</p>
            <p className="font-semibold text-gray-800">{trimestre}</p>
          </div>
        </div>
      </div>

      {/* Attendance */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Calendar className="w-6 h-6 text-red-600" />
          🔹 2. Ausencias
        </h3>
        <div className="p-6 bg-red-50 rounded-xl">
          <p className="text-4xl font-bold text-red-600">
            {reportData?.total_horas_ausencia || 0} h
          </p>
          <p className="text-gray-600 mt-2">Total de horas de ausencia</p>
        </div>
      </div>

      {/* AI Generated Comments Section */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl shadow-xl p-6 border-2 border-purple-200">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-600" />
            Comentarios Automáticos con IA
          </h3>
          <button
            onClick={generateAIComments}
            disabled={generatingAI || !reportData}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl shadow-md hover:shadow-lg transition-all disabled:opacity-50"
          >
            {generatingAI ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Generando...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Generar Comentarios IA</span>
              </>
            )}
          </button>
        </div>

        {generatingAI && (
          <div className="flex items-center gap-3 p-4 bg-purple-100 rounded-xl mb-6">
            <Loader className="w-6 h-6 text-purple-600 animate-spin" />
            <div>
              <p className="font-semibold text-purple-800">
                Generando comentarios personalizados...
              </p>
              <p className="text-sm text-purple-600">
                Analizando evaluaciones, autoevaluación, asistencia y tendencias
              </p>
            </div>
          </div>
        )}

        {/* General Comment */}
        <div className="mb-6">
          <h4 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            🔹 3. Comentario General del Tutor
          </h4>
          <textarea
            value={editableComments.comentario_general || ''}
            onChange={(e) => handleCommentChange('comentario_general', e.target.value)}
            placeholder="El comentario general se generará automáticamente con IA o puedes escribirlo manualmente..."
            className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[120px] resize-y"
          />
          {aiComments.comentario_general && (
            <div className="mt-2 flex items-center gap-2 text-sm text-green-600">
              <CheckCircle className="w-4 h-4" />
              <span>Comentario generado por IA</span>
            </div>
          )}
        </div>

        {/* Autoevaluación */}
        {reportData?.autoevaluacion && (
          <div className="mb-6">
            <h4 className="text-lg font-bold text-gray-800 mb-3">
              🔹 4. Autoevaluación del Alumno
            </h4>
            <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-200 mb-3">
              <p className="text-gray-700 italic">
                "{reportData.autoevaluacion.texto}"
              </p>
            </div>
            <textarea
              value={editableComments.comentario_autoevaluacion || ''}
              onChange={(e) => handleCommentChange('comentario_autoevaluacion', e.target.value)}
              placeholder="Comentario del tutor sobre la autoevaluación (generado por IA)..."
              className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[80px] resize-y"
            />
          </div>
        )}

        {/* Subject Comments */}
        <div className="mb-6">
          <h4 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-green-600" />
            🔹 5. Rendimiento por Asignatura
          </h4>
          <div className="space-y-4">
            {reportData?.evaluaciones_por_asignatura?.map((asignatura) => (
              <div key={asignatura.id} className="bg-white rounded-xl border-2 border-gray-200 p-4">
                <div className="flex items-center justify-between mb-3">
                  <h5 className="font-bold text-gray-800">{asignatura.nombre}</h5>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-600">Nota:</span>
                    <span className="text-2xl font-bold text-blue-600">
                      {asignatura.nota_trimestral?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                </div>
                
                <textarea
                  value={editableComments.comentarios_asignaturas?.[asignatura.nombre] || ''}
                  onChange={(e) => handleCommentChange('comentarios_asignaturas', e.target.value, asignatura.nombre)}
                  placeholder={`Comentario para ${asignatura.nombre} (generado por IA)...`}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[80px] resize-y"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Attendance Comment */}
        {reportData?.total_horas_ausencia > 0 && (
          <div>
            <h4 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              Observaciones sobre Asistencia
            </h4>
            <textarea
              value={editableComments.comentario_asistencia || ''}
              onChange={(e) => handleCommentChange('comentario_asistencia', e.target.value)}
              placeholder="Comentario sobre la asistencia (generado por IA)..."
              className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 min-h-[80px] resize-y"
            />
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
        <div className="flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-gray-700">
            <p className="font-semibold mb-1">💡 Acerca de los Comentarios IA</p>
            <p>
              Los comentarios se generan automáticamente basándose en: evaluaciones numéricas del trimestre, 
              evaluaciones cualitativas del profesor, registros de aula, competencias trabajadas, autoevaluación 
              del alumno, tendencias vs trimestre anterior y asistencia. Todos los comentarios son editables.
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default IndividualReportView;
