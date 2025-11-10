import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import axios from 'axios';

const PublicAutoeval = () => {
  const { evaluationId } = useParams();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [responses, setResponses] = useState({});
  const [error, setError] = useState(null);

  // URL base del API (sin autenticación)
  const API_URL = import.meta.env.VITE_API_URL || 'https://eval-ai-backend.onrender.com/api';

  useEffect(() => {
    fetchEvaluation();
  }, [evaluationId]);

  const fetchEvaluation = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/custom-evaluations/${evaluationId}/public/`);
      setEvaluation(response.data);
      setStudents(response.data.students);
    } catch (error) {
      console.error('Error cargando autoevaluación:', error);
      if (error.response?.status === 404) {
        setError('Esta autoevaluación no está disponible o ha sido desactivada.');
      } else {
        setError('Error al cargar la autoevaluación. Verifica el código QR.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStudentChange = (e) => {
    setSelectedStudent(e.target.value);
  };

  const handleResponseChange = (questionId, value) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedStudent) {
      toast.error('Debes seleccionar tu nombre');
      return;
    }

    // Verificar que todas las preguntas tengan respuesta
    const allQuestionsAnswered = evaluation.questions.every(q => {
      const response = responses[q.id];
      return response !== undefined && response !== '';
    });

    if (!allQuestionsAnswered) {
      toast.error('Debes responder todas las preguntas');
      return;
    }

    try {
      setSubmitting(true);
      await axios.post(`${API_URL}/custom-evaluations/${evaluationId}/submit/`, {
        student_id: selectedStudent,
        responses: responses
      });

      setSubmitted(true);
      toast.success('¡Autoevaluación enviada correctamente!');
    } catch (error) {
      console.error('Error enviando autoevaluación:', error);
      if (error.response?.data?.error) {
        toast.error(error.response.data.error);
      } else {
        toast.error('Error al enviar. Inténtalo de nuevo.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const renderQuestion = (question) => {
    switch (question.type) {
      case 'likert':
        return (
          <div className="space-y-2">
            <div className="flex justify-between items-center gap-2">
              {[1, 2, 3, 4, 5].map(value => (
                <label
                  key={value}
                  className={`flex-1 text-center py-3 px-2 border-2 rounded-lg cursor-pointer transition-colors ${
                    responses[question.id] === value.toString()
                      ? 'border-purple-600 bg-purple-100 text-purple-900'
                      : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={value}
                    checked={responses[question.id] === value.toString()}
                    onChange={(e) => handleResponseChange(question.id, e.target.value)}
                    className="sr-only"
                  />
                  <div className="text-2xl mb-1">{value === 1 ? '😞' : value === 2 ? '😐' : value === 3 ? '🙂' : value === 4 ? '😊' : '😄'}</div>
                  <div className="text-sm font-medium">{value}</div>
                </label>
              ))}
            </div>
            <div className="flex justify-between text-xs text-gray-500 px-1">
              <span>Muy bajo</span>
              <span>Excelente</span>
            </div>
          </div>
        );

      case 'multiple_choice':
        return (
          <div className="space-y-2">
            {question.options.map((option, index) => (
              <label
                key={index}
                className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  responses[question.id] === option
                    ? 'border-purple-600 bg-purple-100'
                    : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={option}
                  checked={responses[question.id] === option}
                  onChange={(e) => handleResponseChange(question.id, e.target.value)}
                  className="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
                />
                <span className="ml-3 text-gray-900">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'text':
        return (
          <textarea
            value={responses[question.id] || ''}
            onChange={(e) => handleResponseChange(question.id, e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900 bg-white"
            rows="4"
            placeholder="Escribe tu respuesta aquí..."
          />
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando autoevaluación...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Error</h1>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-3xl font-bold text-gray-800 mb-4">¡Gracias!</h1>
          <p className="text-lg text-gray-600 mb-6">
            Tu autoevaluación ha sido enviada correctamente.
          </p>
          <div className="bg-purple-100 text-purple-800 p-4 rounded-lg">
            <p className="text-sm">
              <strong>{evaluation.title}</strong>
            </p>
            <p className="text-sm mt-2">
              Tu profesor recibirá tus respuestas.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            📝 {evaluation.title}
          </h1>
          {evaluation.description && (
            <p className="text-gray-600">{evaluation.description}</p>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Selector de estudiante */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <label className="block text-lg font-semibold text-gray-800 mb-3">
              👤 Selecciona tu nombre *
            </label>
            <select
              value={selectedStudent}
              onChange={handleStudentChange}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-lg text-gray-900 bg-white"
              required
            >
              <option value="">-- Busca tu nombre --</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.apellidos}, {student.name}
                </option>
              ))}
            </select>
          </div>

          {/* Preguntas */}
          {evaluation.questions.map((question, index) => (
            <div key={question.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="mb-4">
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                    {index + 1}
                  </span>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">
                      {question.text}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {question.type === 'likert' && 'Escala del 1 al 5'}
                      {question.type === 'multiple_choice' && 'Selecciona una opción'}
                      {question.type === 'text' && 'Respuesta abierta'}
                    </p>
                  </div>
                </div>
              </div>
              {renderQuestion(question)}
            </div>
          ))}

          {/* Botón enviar */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <button
              type="submit"
              disabled={submitting || !selectedStudent}
              className="w-full bg-purple-600 text-white py-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg font-semibold transition-colors"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  Enviando...
                </>
              ) : (
                <>
                  ✓ Enviar Autoevaluación
                </>
              )}
            </button>
            {!selectedStudent && (
              <p className="text-sm text-gray-500 text-center mt-2">
                Selecciona tu nombre para poder enviar
              </p>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default PublicAutoeval;
