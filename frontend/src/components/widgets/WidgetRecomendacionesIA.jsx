import React, { useState } from 'react';
import api from '../../lib/axios';

const WidgetRecomendacionesIA = ({ studentId, titleClassName, onRecommendationsGenerated }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateRecommendations = async (forceRegenerate = false) => {
    try {
      setLoading(true);
      setError(null);

      const url = forceRegenerate 
        ? `/alumnos/${studentId}/recomendaciones/?force=true`
        : `/alumnos/${studentId}/recomendaciones/`;
      
      const response = await api.get(url);
      setRecommendations(response.data);

      if (onRecommendationsGenerated) {
        onRecommendationsGenerated(response.data);
      }
    } catch (error) {
      console.error('Error generando recomendaciones:', error);
      setError('Error al generar recomendaciones. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const getStrengthIcon = (index) => {
    const icons = ['💪', '🎯', '📚', '🤝', '✨'];
    return icons[index % icons.length];
  };

  const getWeaknessIcon = (index) => {
    const icons = ['🔍', '⏰', '📝', '🎯', '💭'];
    return icons[index % icons.length];
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
        <span className="mr-2">🧠</span>
        Recomendaciones IA
      </h3>

      {!recommendations ? (
        <div className="text-center">
          <p className="text-gray-600 mb-4">
            Genera recomendaciones personalizadas basadas en las evaluaciones recientes del alumno.
          </p>
          <button
            onClick={generateRecommendations}
            disabled={loading}
            className="bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Generando...
              </>
            ) : (
              <>
                <span className="mr-2">🧠</span>
                Generar Informe IA
              </>
            )}
          </button>
          {error && (
            <p className="text-red-600 text-sm mt-2">{error}</p>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h4 className="font-medium text-gray-800">Informe de Evaluación IA</h4>
            <button
              onClick={() => {
                setRecommendations(null);
                generateRecommendations(true); // Force regenerate
              }}
              disabled={loading}
              className="text-sm text-purple-600 hover:text-purple-800 disabled:opacity-50"
            >
              {loading ? '🔄 Regenerando...' : '🔄 Generar nuevo'}
            </button>
          </div>

          {recommendations.fortalezas && recommendations.fortalezas.length > 0 && (
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <h5 className="font-medium text-green-800 mb-3 flex items-center">
                <span className="mr-2">💪</span>
                Fortalezas
              </h5>
              <ul className="space-y-2">
                {recommendations.fortalezas.map((fortaleza, index) => (
                  <li key={index} className="flex items-start text-sm text-green-700">
                    <span className="mr-2 mt-1">{getStrengthIcon(index)}</span>
                    <span>{fortaleza}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {recommendations.debilidades && recommendations.debilidades.length > 0 && (
            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
              <h5 className="font-medium text-yellow-800 mb-3 flex items-center">
                <span className="mr-2">🔍</span>
                Áreas de Mejora
              </h5>
              <ul className="space-y-2">
                {recommendations.debilidades.map((debilidad, index) => (
                  <li key={index} className="flex items-start text-sm text-yellow-700">
                    <span className="mr-2 mt-1">{getWeaknessIcon(index)}</span>
                    <span>{debilidad}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {recommendations.recomendacion && (
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <h5 className="font-medium text-blue-800 mb-3 flex items-center">
                <span className="mr-2">💡</span>
                Recomendación Personalizada
              </h5>
              <p className="text-sm text-blue-700 leading-relaxed">
                {recommendations.recomendacion}
              </p>
            </div>
          )}

          <div className="text-xs text-gray-500 text-center pt-2 border-t">
            🤖 Generado por IA basado en las últimas evaluaciones del alumno
          </div>
        </div>
      )}
    </div>
  );
};

export default WidgetRecomendacionesIA;