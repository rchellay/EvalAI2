// frontend/src/pages/RubricApplyPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const RubricApplyPage = () => {
  const navigate = useNavigate();
  const { id: rubricIdFromUrl } = useParams();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Data sources
  const [rubrics, setRubrics] = useState([]);
  const [students, setStudents] = useState([]);
  const [groups, setGroups] = useState([]);
  
  // Selection context
  const [selectedRubricId, setSelectedRubricId] = useState(rubricIdFromUrl || '');
  const [selectedRubric, setSelectedRubric] = useState(null);
  const [targetType, setTargetType] = useState('student'); // 'student' or 'group'
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [evidence, setEvidence] = useState('');
  
  // Evaluation state
  const [evaluationStarted, setEvaluationStarted] = useState(false);
  const [criteriaScores, setCriteriaScores] = useState({}); // {criterionId: {levelId, score, feedback}}
  const [generalObservations, setGeneralObservations] = useState('');
  
  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedRubricId) {
      loadRubricDetails(selectedRubricId);
    }
  }, [selectedRubricId]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [rubricsRes, studentsRes, groupsRes] = await Promise.all([
        api.get('/rubrics/'),
        api.get('/students/'),
        api.get('/groups/')
      ]);
      
      setRubrics(rubricsRes.data.results || rubricsRes.data);
      setStudents(studentsRes.data.results || studentsRes.data);
      setGroups(groupsRes.data.results || groupsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  const loadRubricDetails = async (rubricId) => {
    try {
      const response = await api.get(`/rubrics/${rubricId}/`);
      const rubricData = response.data;
      
      // Load criteria with levels
      const criteriaResponse = await api.get(`/rubric-criteria/`, {
        params: { rubric: rubricId }
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
            levels: levelsData.sort((a, b) => b.score - a.score) // Sort by score descending
          };
        })
      );
      
      rubricData.criteria = criteriaWithLevels.sort((a, b) => a.order - b.order);
      setSelectedRubric(rubricData);
    } catch (error) {
      console.error('Error loading rubric details:', error);
      toast.error('Error al cargar detalles de la rúbrica');
    }
  };

  const handleStartEvaluation = () => {
    if (!selectedRubricId) {
      toast.error('Selecciona una rúbrica');
      return;
    }
    if (targetType === 'student' && !selectedStudentId) {
      toast.error('Selecciona un estudiante');
      return;
    }
    if (targetType === 'group' && !selectedGroupId) {
      toast.error('Selecciona un grupo');
      return;
    }
    
    setEvaluationStarted(true);
    setCriteriaScores({});
    toast.success('Evaluación iniciada');
  };

  const handleSelectLevel = (criterionId, level) => {
    setCriteriaScores({
      ...criteriaScores,
      [criterionId]: {
        levelId: level.id,
        score: level.score,
        feedback: criteriaScores[criterionId]?.feedback || ''
      }
    });
  };

  const handleFeedbackChange = (criterionId, feedback) => {
    if (criteriaScores[criterionId]) {
      setCriteriaScores({
        ...criteriaScores,
        [criterionId]: {
          ...criteriaScores[criterionId],
          feedback
        }
      });
    }
  };

  const calculateTotalScore = () => {
    if (!selectedRubric || !selectedRubric.criteria) return 0;
    
    let totalWeightedScore = 0;
    let totalWeight = 0;
    
    selectedRubric.criteria.forEach(criterion => {
      if (criteriaScores[criterion.id]) {
        const weight = parseFloat(criterion.weight) || 1;
        const score = parseFloat(criteriaScores[criterion.id].score) || 0;
        totalWeightedScore += score * weight;
        totalWeight += weight;
      }
    });
    
    return totalWeight > 0 ? (totalWeightedScore / totalWeight).toFixed(2) : 0;
  };

  const getEvaluatedCount = () => {
    return Object.keys(criteriaScores).length;
  };

  const getProgressPercentage = () => {
    if (!selectedRubric || !selectedRubric.criteria || selectedRubric.criteria.length === 0) {
      return 0;
    }
    return (getEvaluatedCount() / selectedRubric.criteria.length) * 100;
  };

  const handleSaveEvaluation = async () => {
    // Validation
    if (!selectedRubric || !selectedRubric.criteria) {
      toast.error('No hay rúbrica seleccionada');
      return;
    }
    
    if (getEvaluatedCount() < selectedRubric.criteria.length) {
      toast.error('Debes evaluar todos los criterios antes de guardar');
      return;
    }

    try {
      setSaving(true);
      
      // Get target students (single or group members)
      let targetStudents = [];
      if (targetType === 'student') {
        targetStudents = [parseInt(selectedStudentId)];
      } else {
        // Get group members
        const groupResponse = await api.get(`/groups/${selectedGroupId}/`);
        const groupData = groupResponse.data;
        targetStudents = (groupData.students || []).map(s => s.id);
      }

      if (targetStudents.length === 0) {
        toast.error('No hay estudiantes para evaluar');
        return;
      }

      // Generate evaluation session ID for grouping
      const evaluationSessionId = `${Date.now()}-${selectedRubricId}`;

      // Save scores for each student
      const savePromises = [];
      
      for (const studentId of targetStudents) {
        for (const [criterionId, scoreData] of Object.entries(criteriaScores)) {
          const criterion = selectedRubric.criteria.find(c => c.id === parseInt(criterionId));
          
          savePromises.push(
            api.post('/rubric-scores/', {
              rubric: selectedRubric.id,
              criterion: parseInt(criterionId),
              level: scoreData.levelId,
              student: studentId,
              feedback: scoreData.feedback || generalObservations || '',
              evaluation_session_id: evaluationSessionId
            })
          );
        }
      }

      await Promise.all(savePromises);

      toast.success(`Evaluación guardada para ${targetStudents.length} estudiante(s)`);
      navigate('/rubricas');
    } catch (error) {
      console.error('Error saving evaluation:', error);
      toast.error('Error al guardar evaluación');
    } finally {
      setSaving(false);
    }
  };

  const getLevelColor = (level) => {
    // Use custom color or default based on score
    if (level.color) return level.color;
    
    const maxScore = Math.max(...(selectedRubric?.criteria.flatMap(c => c.levels.map(l => l.score)) || [10]));
    const percentage = (level.score / maxScore) * 100;
    
    if (percentage >= 75) return '#10b981'; // green
    if (percentage >= 50) return '#f59e0b'; // yellow
    if (percentage >= 25) return '#f97316'; // orange
    return '#ef4444'; // red
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
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/rubricas')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
            >
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Aplicar Rúbrica</h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Evalúa a estudiantes utilizando rúbricas estructuradas
              </p>
            </div>
          </div>
        </div>

        {/* Selection Context */}
        <section className="bg-white dark:bg-card-dark p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Selección de Contexto
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            {/* Rubric Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Rúbrica
              </label>
              <select
                value={selectedRubricId}
                onChange={(e) => setSelectedRubricId(e.target.value)}
                className="w-full px-4 py-2.5 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:outline-none"
              >
                <option value="">Seleccionar...</option>
                {rubrics.map(rubric => (
                  <option key={rubric.id} value={rubric.id}>
                    {rubric.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Target Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Evaluar
              </label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                className="w-full px-4 py-2.5 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:outline-none"
              >
                <option value="student">Estudiante individual</option>
                <option value="group">Grupo completo</option>
              </select>
            </div>

            {/* Student/Group Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {targetType === 'student' ? 'Estudiante' : 'Grupo'}
              </label>
              {targetType === 'student' ? (
                <select
                  value={selectedStudentId}
                  onChange={(e) => setSelectedStudentId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:outline-none"
                >
                  <option value="">Seleccionar...</option>
                  {students.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.name || student.username}
                    </option>
                  ))}
                </select>
              ) : (
                <select
                  value={selectedGroupId}
                  onChange={(e) => setSelectedGroupId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:outline-none"
                >
                  <option value="">Seleccionar...</option>
                  {groups.map(group => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Start Button */}
            <button
              onClick={handleStartEvaluation}
              disabled={evaluationStarted}
              className="flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition"
            >
              <span className="material-symbols-outlined text-base">
                {evaluationStarted ? 'check_circle' : 'play_arrow'}
              </span>
              {evaluationStarted ? 'Evaluación iniciada' : 'Iniciar evaluación'}
            </button>
          </div>
        </section>

        {/* Evaluation Grid */}
        {evaluationStarted && selectedRubric && (
          <>
            <section className="bg-white dark:bg-card-dark p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Evaluación de la Rúbrica: {selectedRubric.title}
                </h3>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {getEvaluatedCount()}/{selectedRubric.criteria.length} Criterios Evaluados
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-background-light dark:bg-background-dark rounded-full h-2.5 mb-6">
                <div 
                  className="bg-primary h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${getProgressPercentage()}%` }}
                ></div>
              </div>

              {/* Criteria Table */}
              <div className="space-y-4">
                {selectedRubric.criteria.map((criterion, criterionIndex) => (
                  <div key={criterion.id} className="bg-white dark:bg-card-dark border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden">
                    {/* Criterion Header */}
                    <div className="bg-gray-50 dark:bg-gray-800/50 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                      <h4 className="font-semibold text-gray-900 dark:text-white">
                        {criterion.name}
                      </h4>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {criterion.description}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                        Peso: {criterion.weight}%
                      </p>
                    </div>

                    {/* Levels Grid */}
                    <div className="p-6">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {criterion.levels.map((level) => (
                          <button
                            key={level.id}
                            onClick={() => handleSelectLevel(criterion.id, level)}
                            className={`p-4 rounded-lg border-2 transition-all text-center ${
                              criteriaScores[criterion.id]?.levelId === level.id
                                ? 'border-transparent text-white scale-105 shadow-lg'
                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:scale-102'
                            }`}
                            style={{
                              backgroundColor: criteriaScores[criterion.id]?.levelId === level.id 
                                ? getLevelColor(level)
                                : 'transparent'
                            }}
                            title={level.description}
                          >
                            <div className={`font-semibold mb-1 ${
                              criteriaScores[criterion.id]?.levelId === level.id
                                ? 'text-white'
                                : 'text-gray-900 dark:text-white'
                            }`}>
                              {level.name}
                            </div>
                            <div className={`text-2xl font-bold ${
                              criteriaScores[criterion.id]?.levelId === level.id
                                ? 'text-white'
                                : 'text-primary'
                            }`}>
                              {level.score}
                            </div>
                            {level.description && (
                              <div className={`text-xs mt-2 ${
                                criteriaScores[criterion.id]?.levelId === level.id
                                  ? 'text-white/90'
                                  : 'text-gray-500 dark:text-gray-400'
                              }`}>
                                {level.description.substring(0, 50)}{level.description.length > 50 ? '...' : ''}
                              </div>
                            )}
                            {criteriaScores[criterion.id]?.levelId === level.id && (
                              <span className="material-symbols-outlined mt-2">check_circle</span>
                            )}
                          </button>
                        ))}
                      </div>

                      {/* Feedback for this criterion */}
                      {criteriaScores[criterion.id] && (
                        <div className="mt-4">
                          <textarea
                            value={criteriaScores[criterion.id]?.feedback || ''}
                            onChange={(e) => handleFeedbackChange(criterion.id, e.target.value)}
                            placeholder={`Añadir comentario para ${criterion.name}...`}
                            rows={3}
                            className="w-full bg-white dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-lg p-3 text-sm placeholder-gray-400 focus:ring-2 focus:ring-primary focus:outline-none resize-none"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Results and Actions */}
            <section className="bg-white dark:bg-card-dark p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Resultados y Acciones
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-background-light dark:bg-background-dark p-4 rounded-lg border border-gray-200 dark:border-gray-800">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Puntuación Ponderada
                  </h4>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                    {calculateTotalScore()}
                    <span className="text-lg font-medium text-gray-500 dark:text-gray-400 ml-1">
                      / {Math.max(...(selectedRubric?.criteria.flatMap(c => c.levels.map(l => l.score)) || [10]))}
                    </span>
                  </p>
                </div>
                
                <div className="bg-background-light dark:bg-background-dark p-4 rounded-lg border border-gray-200 dark:border-gray-800">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Progreso
                  </h4>
                  <div className="flex items-baseline gap-2 mt-2">
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {getProgressPercentage().toFixed(0)}%
                    </p>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      ({getEvaluatedCount()} de {selectedRubric.criteria.length})
                    </span>
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Observaciones Generales
                </label>
                <textarea
                  value={generalObservations}
                  onChange={(e) => setGeneralObservations(e.target.value)}
                  placeholder="Escribe aquí tus observaciones generales sobre la evaluación..."
                  rows={4}
                  className="w-full bg-background-light dark:bg-background-dark text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-lg p-2.5 placeholder-gray-400 focus:ring-2 focus:ring-primary focus:outline-none resize-none"
                />
              </div>

              <div className="flex justify-end gap-4">
                <button
                  onClick={() => navigate('/rubricas')}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSaveEvaluation}
                  disabled={saving || getEvaluatedCount() < selectedRubric.criteria.length}
                  className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Guardando...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-base">save</span>
                      Guardar Evaluación
                    </>
                  )}
                </button>
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
};

export default RubricApplyPage;
