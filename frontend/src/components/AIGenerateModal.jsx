import { useState } from 'react';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';

const AIGenerateModal = ({ isOpen, onClose, onGenerated }) => {
  const [prompt, setPrompt] = useState('');
  const [language, setLanguage] = useState('es');
  const [maxCriteria, setMaxCriteria] = useState(4);
  const [levelsPerCriterion, setLevelsPerCriterion] = useState(4);
  const [maxScore, setMaxScore] = useState(10);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedData, setGeneratedData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Por favor, describe la rúbrica que deseas generar');
      return;
    }

    if (prompt.length > 2000) {
      toast.error('El prompt no puede exceder 2000 caracteres');
      return;
    }

    setIsGenerating(true);
    setGeneratedData(null);

    try {
      const response = await api.post(
        '/rubrics/generate/',
        {
          prompt: prompt.trim(),
          language,
          max_criteria: maxCriteria,
          levels_per_criterion: levelsPerCriterion,
          max_score: maxScore,
          use_cache: true
        }
      );

      setGeneratedData(response.data);
      setShowPreview(true);
      
      if (response.data.generation_meta?.fallback) {
        toast.warning('Usando plantilla por defecto (API no disponible)');
      } else if (response.data.from_cache) {
        toast.success('Rúbrica obtenida de caché');
      } else {
        toast.success('¡Rúbrica generada con IA!');
      }
    } catch (error) {
      console.error('Error al generar rúbrica:', error);
      if (error.response?.status === 429) {
        toast.error('Límite de solicitudes alcanzado. Espera un momento.');
      } else {
        toast.error(error.response?.data?.error || 'Error al generar la rúbrica');
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUseGenerated = () => {
    if (generatedData) {
      onGenerated(generatedData);
      handleClose();
    }
  };

  const handleClose = () => {
    setPrompt('');
    setGeneratedData(null);
    setShowPreview(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-4xl">auto_awesome</span>
              <div>
                <h2 className="text-2xl font-bold">Generar con IA</h2>
                <p className="text-purple-100 text-sm mt-1">Powered by OpenRouter AI (Qwen3-235B)</p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:bg-white/20 rounded-full p-2 transition-colors"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {!showPreview ? (
            // Formulario de generación
            <div className="space-y-6">
              {/* Prompt Principal */}
              <div>
                <label htmlFor="rubric-description" className="block text-sm font-semibold text-gray-700 mb-2">
                  Describe la rúbrica que necesitas
                </label>
                <textarea
                  id="rubric-description"
                  name="rubric-description"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Ejemplo: rúbrica para evaluar comprensión oral en 6º de primaria, enfocada en claridad, vocabulario, argumentación y expresión"
                  className="w-full px-4 py-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none placeholder-gray-400"
                  rows={4}
                  maxLength={2000}
                  autoComplete="off"
                />
                <div className="flex justify-between items-center mt-1">
                  <p className="text-xs text-gray-500">
                    Sé específico: nivel educativo, materia, criterios deseados...
                  </p>
                  <span className="text-xs text-gray-400">
                    {prompt.length}/2000
                  </span>
                </div>
              </div>

              {/* Configuración Avanzada */}
              <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                  <span className="material-symbols-outlined text-lg">tune</span>
                  Configuración Avanzada
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Idioma */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Idioma
                    </label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="es">Español</option>
                      <option value="en">English</option>
                      <option value="ca">Català</option>
                      <option value="fr">Français</option>
                    </select>
                  </div>

                  {/* Número de criterios */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Número de criterios
                    </label>
                    <select
                      value={maxCriteria}
                      onChange={(e) => setMaxCriteria(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value={3}>3 criterios</option>
                      <option value={4}>4 criterios</option>
                      <option value={5}>5 criterios</option>
                      <option value={6}>6 criterios</option>
                      <option value={7}>7 criterios</option>
                    </select>
                  </div>

                  {/* Niveles por criterio */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Niveles por criterio
                    </label>
                    <select
                      value={levelsPerCriterion}
                      onChange={(e) => setLevelsPerCriterion(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value={3}>3 niveles</option>
                      <option value={4}>4 niveles</option>
                      <option value={5}>5 niveles</option>
                    </select>
                  </div>

                  {/* Puntuación máxima */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Puntuación máxima
                    </label>
                    <select
                      value={maxScore}
                      onChange={(e) => setMaxScore(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value={4}>4 puntos</option>
                      <option value={5}>5 puntos</option>
                      <option value={10}>10 puntos</option>
                      <option value={20}>20 puntos</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Ejemplos de prompts */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-lg">lightbulb</span>
                  Ejemplos de prompts
                </h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• "Rúbrica para presentaciones orales en 5º de primaria"</li>
                  <li>• "Evaluar proyectos de investigación científica en secundaria"</li>
                  <li>• "Comprensión lectora para 3º de primaria con énfasis en vocabulario"</li>
                  <li>• "Trabajo en equipo y colaboración para proyectos grupales"</li>
                </ul>
              </div>
            </div>
          ) : (
            // Vista previa de la rúbrica generada
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-green-600 text-3xl">check_circle</span>
                  <div className="flex-1">
                    <h3 className="font-bold text-green-900 text-lg mb-1">
                      {generatedData?.title || 'Rúbrica generada'}
                    </h3>
                    <p className="text-green-700 text-sm">
                      {generatedData?.description || 'Sin descripción'}
                    </p>
                    {generatedData?.generation_meta && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded-full text-xs text-gray-600">
                          <span className="material-symbols-outlined text-sm">psychology</span>
                          {generatedData.generation_meta.fallback ? 'Plantilla' : 'Gemini AI'}
                        </span>
                        {generatedData.from_cache && (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded-full text-xs text-gray-600">
                            <span className="material-symbols-outlined text-sm">storage</span>
                            Caché
                          </span>
                        )}
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded-full text-xs text-gray-600">
                          <span className="material-symbols-outlined text-sm">format_list_numbered</span>
                          {generatedData.criteria?.length || 0} criterios
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Criterios generados */}
              <div className="space-y-3">
                {generatedData?.criteria?.map((criterion, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-gray-900">
                        {idx + 1}. {criterion.name}
                      </h4>
                      <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full font-medium">
                        {criterion.weight}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{criterion.description}</p>
                    
                    {/* Niveles del criterio */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {criterion.levels?.map((level, levelIdx) => (
                        <div
                          key={levelIdx}
                          className="bg-gray-50 rounded p-2 text-center border border-gray-200"
                        >
                          <div className="font-semibold text-sm text-gray-900">
                            {level.level_name}
                          </div>
                          <div className="text-lg font-bold text-purple-600">
                            {level.score}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Botones de acción en preview */}
              <div className="flex gap-3">
                <button
                  onClick={() => setShowPreview(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Generar otra
                </button>
                <button
                  onClick={handleUseGenerated}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold"
                >
                  Usar esta rúbrica
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer con botones (solo si no está en preview) */}
        {!showPreview && (
          <div className="border-t border-gray-200 p-6 bg-gray-50">
            <div className="flex justify-end gap-3">
              <button
                onClick={handleClose}
                disabled={isGenerating}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generando...
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined">auto_awesome</span>
                    Generar Rúbrica
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIGenerateModal;
