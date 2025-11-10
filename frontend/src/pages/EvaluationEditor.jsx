import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { Switch } from 'antd';
import api from '../lib/axios';

const EvaluationEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = id === 'new';

  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [groups, setGroups] = useState([]);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    group: '',
    questions: [],
    allow_multiple_attempts: false,
    is_active: true
  });

  const [editingQuestion, setEditingQuestion] = useState(null);
  const [questionForm, setQuestionForm] = useState({
    id: null,
    text: '',
    type: 'likert',
    options: ['']
  });

  useEffect(() => {
    fetchGroups();
    if (!isNew) {
      fetchEvaluation();
    }
  }, [id]);

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups/');
      // Manejar respuesta paginada o array directo
      const data = Array.isArray(response.data) ? response.data : (response.data.results || []);
      setGroups(data);
    } catch (error) {
      console.error('Error cargando grupos:', error);
      toast.error('Error al cargar grupos');
      setGroups([]);
    }
  };

  const fetchEvaluation = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/custom-evaluations/${id}/`);
      setFormData(response.data);
    } catch (error) {
      console.error('Error cargando autoevaluación:', error);
      toast.error('Error al cargar autoevaluación');
      navigate('/teacher/evaluations');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleAddQuestion = () => {
    setEditingQuestion(null);
    setQuestionForm({
      id: Date.now(),
      text: '',
      type: 'likert',
      options: ['']
    });
  };

  const handleEditQuestion = (question) => {
    setEditingQuestion(question.id);
    setQuestionForm({
      ...question,
      options: question.options || ['']
    });
  };

  const handleQuestionFormChange = (e) => {
    const { name, value } = e.target;
    setQuestionForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleOptionChange = (index, value) => {
    const newOptions = [...questionForm.options];
    newOptions[index] = value;
    setQuestionForm(prev => ({
      ...prev,
      options: newOptions
    }));
  };

  const handleAddOption = () => {
    setQuestionForm(prev => ({
      ...prev,
      options: [...prev.options, '']
    }));
  };

  const handleRemoveOption = (index) => {
    if (questionForm.options.length > 1) {
      setQuestionForm(prev => ({
        ...prev,
        options: prev.options.filter((_, i) => i !== index)
      }));
    }
  };

  const handleSaveQuestion = () => {
    if (!questionForm.text.trim()) {
      toast.error('El texto de la pregunta es obligatorio');
      return;
    }

    if (questionForm.type === 'multiple_choice' && questionForm.options.filter(o => o.trim()).length < 2) {
      toast.error('Debes agregar al menos 2 opciones');
      return;
    }

    const cleanedQuestion = {
      ...questionForm,
      options: questionForm.type === 'multiple_choice' ? questionForm.options.filter(o => o.trim()) : []
    };

    if (editingQuestion) {
      // Actualizar pregunta existente
      setFormData(prev => ({
        ...prev,
        questions: prev.questions.map(q => q.id === editingQuestion ? cleanedQuestion : q)
      }));
    } else {
      // Agregar nueva pregunta
      setFormData(prev => ({
        ...prev,
        questions: [...prev.questions, cleanedQuestion]
      }));
    }

    setEditingQuestion(null);
    setQuestionForm({
      id: null,
      text: '',
      type: 'likert',
      options: ['']
    });

    toast.success(editingQuestion ? 'Pregunta actualizada' : 'Pregunta agregada');
  };

  const handleCancelQuestion = () => {
    setEditingQuestion(null);
    setQuestionForm({
      id: null,
      text: '',
      type: 'likert',
      options: ['']
    });
  };

  const handleDeleteQuestion = (questionId) => {
    if (!window.confirm('¿Eliminar esta pregunta?')) return;

    setFormData(prev => ({
      ...prev,
      questions: prev.questions.filter(q => q.id !== questionId)
    }));
    toast.success('Pregunta eliminada');
  };

  const handleMoveQuestion = (index, direction) => {
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= formData.questions.length) return;

    const newQuestions = [...formData.questions];
    [newQuestions[index], newQuestions[newIndex]] = [newQuestions[newIndex], newQuestions[index]];
    
    setFormData(prev => ({
      ...prev,
      questions: newQuestions
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.title.trim()) {
      toast.error('El título es obligatorio');
      return;
    }

    if (!formData.group) {
      toast.error('Debes seleccionar un grupo');
      return;
    }

    if (formData.questions.length === 0) {
      toast.error('Debes agregar al menos una pregunta');
      return;
    }

    try {
      setSaving(true);
      if (isNew) {
        await api.post('/custom-evaluations/', formData);
        toast.success('Autoevaluación creada exitosamente');
      } else {
        await api.put(`/custom-evaluations/${id}/`, formData);
        toast.success('Autoevaluación actualizada exitosamente');
      }
      navigate('/teacher/evaluations');
    } catch (error) {
      console.error('Error guardando:', error);
      toast.error('Error al guardar autoevaluación');
    } finally {
      setSaving(false);
    }
  };

  const getQuestionTypeLabel = (type) => {
    switch (type) {
      case 'likert': return '⭐ Escala Likert (1-5)';
      case 'multiple_choice': return '☑️ Selección Múltiple';
      case 'text': return '📝 Texto Abierto';
      default: return type;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <button
          onClick={() => navigate('/teacher/evaluations')}
          className="text-gray-600 hover:text-gray-900 mb-4 flex items-center gap-2"
        >
          ← Volver a lista
        </button>
        <h1 className="text-3xl font-bold text-gray-800">
          {isNew ? '➕ Crear' : '✏️ Editar'} Autoevaluación
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Información básica */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">📋 Información Básica</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Título *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Ej: Autoevaluación Trimestre 1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción (opcional)
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 bg-white"
                rows="3"
                placeholder="Instrucciones para los alumnos..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Grupo *
              </label>
              <select
                name="group"
                value={formData.group}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 bg-white"
                required
              >
                <option value="">Selecciona un grupo</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>
                    {group.name} - {group.course}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Permitir múltiples intentos</span>
                <Switch
                  checked={formData.allow_multiple_attempts}
                  onChange={(checked) => setFormData(prev => ({ ...prev, allow_multiple_attempts: checked }))}
                />
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Activa (los alumnos pueden responder)</span>
                <Switch
                  checked={formData.is_active}
                  onChange={(checked) => setFormData(prev => ({ ...prev, is_active: checked }))}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Editor de preguntas */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">❓ Preguntas ({formData.questions.length})</h2>
            {!editingQuestion && questionForm.id === null && (
              <button
                type="button"
                onClick={handleAddQuestion}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                ➕ Agregar Pregunta
              </button>
            )}
          </div>

          {/* Formulario de pregunta */}
          {questionForm.id !== null && (
            <div className="border-2 border-purple-300 rounded-lg p-4 mb-4 bg-purple-50">
              <h3 className="font-semibold mb-3">
                {editingQuestion ? '✏️ Editar Pregunta' : '➕ Nueva Pregunta'}
              </h3>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Texto de la pregunta *
                  </label>
                  <input
                    type="text"
                    name="text"
                    value={questionForm.text}
                    onChange={handleQuestionFormChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="¿Cómo calificas tu participación?"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de pregunta *
                  </label>
                  <select
                    name="type"
                    value={questionForm.type}
                    onChange={handleQuestionFormChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 text-gray-900 bg-white"
                  >
                    <option value="likert">⭐ Escala Likert (1-5)</option>
                    <option value="multiple_choice">☑️ Selección Múltiple</option>
                    <option value="text">📝 Texto Abierto</option>
                  </select>
                </div>

                {questionForm.type === 'multiple_choice' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Opciones *
                    </label>
                    {questionForm.options.map((option, index) => (
                      <div key={index} className="flex gap-2 mb-2">
                        <input
                          type="text"
                          value={option}
                          onChange={(e) => handleOptionChange(index, e.target.value)}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                          placeholder={`Opción ${index + 1}`}
                        />
                        {questionForm.options.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveOption(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            ✕
                          </button>
                        )}
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={handleAddOption}
                      className="text-sm text-purple-600 hover:text-purple-800"
                    >
                      + Agregar opción
                    </button>
                  </div>
                )}

                <div className="flex gap-2 pt-2">
                  <button
                    type="button"
                    onClick={handleSaveQuestion}
                    className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
                  >
                    ✓ Guardar Pregunta
                  </button>
                  <button
                    type="button"
                    onClick={handleCancelQuestion}
                    className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Lista de preguntas */}
          {formData.questions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">❓</div>
              <p>No hay preguntas aún</p>
              <p className="text-sm">Haz clic en "Agregar Pregunta" para empezar</p>
            </div>
          ) : (
            <div className="space-y-3">
              {formData.questions.map((question, index) => (
                <div key={question.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-gray-700">#{index + 1}</span>
                        <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded">
                          {getQuestionTypeLabel(question.type)}
                        </span>
                      </div>
                      <p className="text-gray-900 mb-2">{question.text}</p>
                      {question.type === 'multiple_choice' && question.options && (
                        <div className="text-sm text-gray-600">
                          Opciones: {question.options.join(' • ')}
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      <button
                        type="button"
                        onClick={() => handleMoveQuestion(index, 'up')}
                        disabled={index === 0}
                        className="text-gray-600 hover:text-gray-900 disabled:opacity-30"
                        title="Subir"
                      >
                        ↑
                      </button>
                      <button
                        type="button"
                        onClick={() => handleMoveQuestion(index, 'down')}
                        disabled={index === formData.questions.length - 1}
                        className="text-gray-600 hover:text-gray-900 disabled:opacity-30"
                        title="Bajar"
                      >
                        ↓
                      </button>
                      <button
                        type="button"
                        onClick={() => handleEditQuestion(question)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteQuestion(question.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Botones de acción */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Guardando...
              </>
            ) : (
              <>💾 {isNew ? 'Crear' : 'Guardar'} Autoevaluación</>
            )}
          </button>
          <button
            type="button"
            onClick={() => navigate('/teacher/evaluations')}
            className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default EvaluationEditor;
