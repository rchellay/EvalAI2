// frontend/src/pages/RubricEditorPage.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';
import AIGenerateModal from '../components/AIGenerateModal';

const RubricEditorPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = !!id;

  const [loading, setLoading] = useState(isEditing);
  const [saving, setSaving] = useState(false);
  const [subjects, setSubjects] = useState([]);
  
  const [rubric, setRubric] = useState({
    title: '',
    description: '',
    subject: null,
    status: 'draft'
  });

  const [criteria, setCriteria] = useState([]);
  const [expandedCriterion, setExpandedCriterion] = useState(null);
  const [showAIModal, setShowAIModal] = useState(false);

  useEffect(() => {
    loadSubjects();
    if (isEditing) {
      loadRubric();
    }
  }, [id]);

  const loadSubjects = async () => {
    try {
      const response = await api.get('/subjects/');
      const subjectsData = response.data.results || response.data;
      setSubjects(Array.isArray(subjectsData) ? subjectsData : []);
    } catch (error) {
      console.error('Error loading subjects:', error);
    }
  };

  const loadRubric = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/rubrics/${id}/`);
      setRubric(response.data);
      
      // Load criteria with levels
      const criteriaResponse = await api.get(`/rubric-criteria/`, {
        params: { rubric: id }
      });
      const criteriaData = criteriaResponse.data.results || criteriaResponse.data;
      
      // Load levels for each criterion
      const criteriaWithLevels = await Promise.all(
        criteriaData.map(async (criterion) => {
          const levelsResponse = await api.get(`/rubric-levels/`, {
            params: { criterion: criterion.id }
          });
          const levelsData = levelsResponse.data.results || levelsResponse.data;
          return {
            ...criterion,
            levels: levelsData.sort((a, b) => a.order - b.order)
          };
        })
      );
      
      setCriteria(criteriaWithLevels.sort((a, b) => a.order - b.order));
    } catch (error) {
      console.error('Error loading rubric:', error);
      toast.error('Error al cargar rúbrica');
    } finally {
      setLoading(false);
    }
  };

  const addCriterion = () => {
    const newCriterion = {
      id: `temp-${Date.now()}`,
      name: '',
      description: '',
      weight: 0,
      order: criteria.length,
      levels: [],
      isNew: true
    };
    setCriteria([...criteria, newCriterion]);
    setExpandedCriterion(newCriterion.id);
  };

  const removeCriterion = async (criterionId) => {
    if (!window.confirm('¿Eliminar este criterio y todos sus niveles?')) return;
    
    if (typeof criterionId === 'string' && criterionId.startsWith('temp-')) {
      setCriteria(criteria.filter(c => c.id !== criterionId));
    } else {
      try {
        await api.delete(`/rubric-criteria/${criterionId}/`);
        setCriteria(criteria.filter(c => c.id !== criterionId));
        toast.success('Criterio eliminado');
      } catch (error) {
        console.error('Error deleting criterion:', error);
        toast.error('Error al eliminar criterio');
      }
    }
  };

  const updateCriterion = (criterionId, field, value) => {
    setCriteria(criteria.map(c =>
      c.id === criterionId ? { ...c, [field]: value } : c
    ));
  };

  const addLevel = (criterionId) => {
    setCriteria(criteria.map(c => {
      if (c.id === criterionId) {
        const newLevel = {
          id: `temp-${Date.now()}`,
          name: '',
          description: '',
          score: 0,
          order: c.levels.length,
          color: '#3b82f6',
          isNew: true
        };
        return { ...c, levels: [...c.levels, newLevel] };
      }
      return c;
    }));
  };

  const removeLevel = async (criterionId, levelId) => {
    if (typeof levelId === 'string' && levelId.startsWith('temp-')) {
      setCriteria(criteria.map(c =>
        c.id === criterionId
          ? { ...c, levels: c.levels.filter(l => l.id !== levelId) }
          : c
      ));
    } else {
      try {
        await api.delete(`/rubric-levels/${levelId}/`);
        setCriteria(criteria.map(c =>
          c.id === criterionId
            ? { ...c, levels: c.levels.filter(l => l.id !== levelId) }
            : c
        ));
        toast.success('Nivel eliminado');
      } catch (error) {
        console.error('Error deleting level:', error);
        toast.error('Error al eliminar nivel');
      }
    }
  };

  const updateLevel = (criterionId, levelId, field, value) => {
    setCriteria(criteria.map(c => {
      if (c.id === criterionId) {
        return {
          ...c,
          levels: c.levels.map(l =>
            l.id === levelId ? { ...l, [field]: value } : l
          )
        };
      }
      return c;
    }));
  };

  const getTotalWeight = () => {
    return criteria.reduce((sum, c) => sum + (parseFloat(c.weight) || 0), 0);
  };

  const handleAIGenerated = (aiData) => {
    // Poblar el formulario con los datos generados por IA
    setRubric({
      ...rubric,
      title: aiData.title || rubric.title,
      description: aiData.description || rubric.description
    });

    // Convertir criterios de IA a formato interno
    const newCriteria = aiData.criteria?.map((criterion, idx) => ({
      id: `temp-ai-${Date.now()}-${idx}`,
      name: criterion.name,
      description: criterion.description || '',
      weight: criterion.weight.toFixed(1), // El peso ya viene como porcentaje
      levels: criterion.levels?.map((level, levelIdx) => ({
        id: `temp-ai-level-${Date.now()}-${idx}-${levelIdx}`,
        name: level.level_name,
        description: level.description || '',
        score: level.score,
        order: levelIdx,
        color: levelIdx === 0 ? '#22c55e' : levelIdx === 1 ? '#3b82f6' : levelIdx === 2 ? '#f59e0b' : '#ef4444'
      })) || []
    })) || [];

    setCriteria(newCriteria);
    toast.success('Rúbrica cargada desde IA. Puedes editarla antes de guardar.');
  };

  const handleSave = async () => {
    // Validations
    if (!rubric.title.trim()) {
      toast.error('El título es obligatorio');
      return;
    }
    if (criteria.length === 0) {
      toast.error('Añade al menos un criterio');
      return;
    }
    if (Math.abs(getTotalWeight() - 100) > 0.01) {
      toast.error('Los pesos deben sumar 100%');
      return;
    }
    for (const criterion of criteria) {
      if (!criterion.name.trim()) {
        toast.error('Todos los criterios deben tener nombre');
        return;
      }
      if (criterion.levels.length === 0) {
        toast.error(`El criterio "${criterion.name}" debe tener al menos un nivel`);
        return;
      }
    }

    try {
      setSaving(true);
      
      // Save rubric
      let rubricResponse;
      if (isEditing) {
        rubricResponse = await api.put(`/rubrics/${id}/`, rubric);
      } else {
        rubricResponse = await api.post('/rubrics/', rubric);
      }
      const rubricId = rubricResponse.data.id;

      // Save criteria and levels
      for (let i = 0; i < criteria.length; i++) {
        const criterion = criteria[i];
        const criterionData = {
          rubric: rubricId,
          name: criterion.name,
          description: criterion.description,
          weight: parseFloat(criterion.weight),
          order: i
        };

        let criterionResponse;
        if (typeof criterion.id === 'string' && criterion.id.startsWith('temp-')) {
          criterionResponse = await api.post('/rubric-criteria/', criterionData);
        } else {
          criterionResponse = await api.put(`/rubric-criteria/${criterion.id}/`, criterionData);
        }
        const criterionId = criterionResponse.data.id;

        // Save levels
        for (let j = 0; j < criterion.levels.length; j++) {
          const level = criterion.levels[j];
          const levelData = {
            criterion: criterionId,
            name: level.name,
            description: level.description,
            score: parseFloat(level.score),
            order: j,
            color: level.color
          };

          if (typeof level.id === 'string' && level.id.startsWith('temp-')) {
            await api.post('/rubric-levels/', levelData);
          } else {
            await api.put(`/rubric-levels/${level.id}/`, levelData);
          }
        }
      }

      toast.success(isEditing ? 'Rúbrica actualizada' : 'Rúbrica creada correctamente');
      navigate('/rubricas');
    } catch (error) {
      console.error('Error saving rubric:', error);
      toast.error('Error al guardar rúbrica');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background-light dark:bg-background-dark">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto bg-background-light dark:bg-background-dark">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/rubricas')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
            >
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {isEditing ? 'Editar Rúbrica' : 'Nueva Rúbrica'}
              </h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Define criterios y niveles de evaluación
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/rubricas')}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Guardando...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-base">save</span>
                  Guardar
                </>
              )}
            </button>
          </div>
        </div>

        {/* Basic Info */}
        <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Información Básica
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Título *
              </label>
              <input
                type="text"
                value={rubric.title}
                onChange={(e) => setRubric({ ...rubric, title: e.target.value })}
                placeholder="Ej: Rúbrica de Escritura Creativa"
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Descripción
              </label>
              <textarea
                value={rubric.description}
                onChange={(e) => setRubric({ ...rubric, description: e.target.value })}
                rows={3}
                placeholder="Descripción de la rúbrica y su propósito..."
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Asignatura
              </label>
              <select
                value={rubric.subject || ''}
                onChange={(e) => setRubric({ ...rubric, subject: e.target.value || null })}
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              >
                <option value="">Ninguna</option>
                {subjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Estado
              </label>
              <select
                value={rubric.status}
                onChange={(e) => setRubric({ ...rubric, status: e.target.value })}
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              >
                <option value="draft">Borrador</option>
                <option value="active">Activa</option>
                <option value="inactive">Inactiva</option>
              </select>
            </div>
          </div>
        </div>

        {/* Criteria */}
        <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Criterios de Evaluación
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Peso total: {getTotalWeight().toFixed(1)}% {getTotalWeight() !== 100 && (
                  <span className="text-red-500 font-medium">(debe ser 100%)</span>
                )}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowAIModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition font-semibold shadow-md"
              >
                <span className="material-symbols-outlined text-base">auto_awesome</span>
                Generar con IA
              </button>
              <button
                onClick={addCriterion}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
              >
                <span className="material-symbols-outlined text-base">add</span>
                Añadir Criterio
              </button>
            </div>
          </div>

          {criteria.length === 0 ? (
            <div className="text-center py-12">
              <span className="material-symbols-outlined text-6xl text-gray-300 dark:text-gray-700">
                list_alt
              </span>
              <p className="text-gray-500 dark:text-gray-400 mt-4">
                No hay criterios. Añade el primero para empezar.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {criteria.map((criterion, index) => (
                <div
                  key={criterion.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                >
                  {/* Criterion Header */}
                  <div className="bg-gray-50 dark:bg-gray-800/50 p-4">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-8 h-8 bg-primary text-white rounded-full font-semibold text-sm">
                        {index + 1}
                      </span>
                      <div className="flex-1 flex gap-3">
                        <input
                          type="text"
                          value={criterion.name}
                          onChange={(e) => updateCriterion(criterion.id, 'name', e.target.value)}
                          placeholder="Nombre del criterio"
                          className="w-1/4 px-3 py-2 bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded text-sm placeholder-gray-400"
                        />
                        <textarea
                          value={criterion.description}
                          onChange={(e) => updateCriterion(criterion.id, 'description', e.target.value)}
                          placeholder="Descripción detallada"
                          rows="2"
                          className="flex-1 px-3 py-2 bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded text-sm placeholder-gray-400 resize-none"
                        />
                        <div className="flex items-center gap-2 w-24">
                          <input
                            type="number"
                            value={criterion.weight}
                            onChange={(e) => updateCriterion(criterion.id, 'weight', e.target.value)}
                            placeholder="Peso %"
                            min="0"
                            max="100"
                            step="0.1"
                            className="w-full px-2 py-2 bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded text-sm placeholder-gray-400"
                          />
                          <span className="text-sm text-gray-500">%</span>
                        </div>
                      </div>
                      <button
                        onClick={() => setExpandedCriterion(
                          expandedCriterion === criterion.id ? null : criterion.id
                        )}
                        className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition"
                      >
                        <span className="material-symbols-outlined">
                          {expandedCriterion === criterion.id ? 'expand_less' : 'expand_more'}
                        </span>
                      </button>
                      <button
                        onClick={() => removeCriterion(criterion.id)}
                        className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition"
                      >
                        <span className="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </div>

                  {/* Levels */}
                  {expandedCriterion === criterion.id && (
                    <div className="p-4 bg-white dark:bg-card-dark">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
                          Niveles de Desempeño
                        </h3>
                        <button
                          onClick={() => addLevel(criterion.id)}
                          className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded transition font-medium"
                        >
                          <span className="material-symbols-outlined text-sm">add</span>
                          Añadir Nivel
                        </button>
                      </div>

                      {criterion.levels.length === 0 ? (
                        <p className="text-sm text-gray-500 text-center py-4">
                          No hay niveles. Añade al menos uno.
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {criterion.levels.map((level, levelIndex) => (
                            <div
                              key={level.id}
                              className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded border border-gray-200 dark:border-gray-700"
                            >
                              <input
                                type="color"
                                value={level.color}
                                onChange={(e) => updateLevel(criterion.id, level.id, 'color', e.target.value)}
                                className="w-10 h-10 rounded cursor-pointer"
                              />
                              <input
                                type="text"
                                value={level.name}
                                onChange={(e) => updateLevel(criterion.id, level.id, 'name', e.target.value)}
                                placeholder="Nivel (Ej: Excelente)"
                                className="flex-1 px-3 py-2 bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded text-sm placeholder-gray-400"
                              />
                              <input
                                type="number"
                                value={level.score}
                                onChange={(e) => updateLevel(criterion.id, level.id, 'score', e.target.value)}
                                placeholder="Puntos"
                                min="0"
                                step="0.1"
                                className="w-24 px-3 py-2 bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded text-sm placeholder-gray-400"
                              />
                              <input
                                type="text"
                                value={level.description}
                                onChange={(e) => updateLevel(criterion.id, level.id, 'description', e.target.value)}
                                placeholder="Descripción"
                                className="flex-1 px-3 py-2 bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded text-sm placeholder-gray-400"
                              />
                              <button
                                onClick={() => removeLevel(criterion.id, level.id)}
                                className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition"
                              >
                                <span className="material-symbols-outlined text-sm">close</span>
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Modal de generación con IA */}
        <AIGenerateModal
          isOpen={showAIModal}
          onClose={() => setShowAIModal(false)}
          onGenerated={handleAIGenerated}
        />
      </div>
    </div>
  );
};

export default RubricEditorPage;
