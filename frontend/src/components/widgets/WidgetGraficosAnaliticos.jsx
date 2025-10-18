import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const WidgetGraficosAnaliticos = ({ studentId, titleClassName }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeChart, setActiveChart] = useState('trend');

  useEffect(() => {
    loadAnalyticsData();
  }, [studentId]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/alumnos/${studentId}/analytics/`);
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('Error cargando datos analíticos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <span className="mr-2">📊</span>
          Análisis del Progreso
        </h3>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <span className="mr-2">📊</span>
          Análisis del Progreso
        </h3>
        <div className="text-center py-8 text-gray-500">
          No se pudieron cargar los datos analíticos
        </div>
      </div>
    );
  }

  // Asegurarse de que analyticsData.evaluation_trend siempre se trate como una matriz
  const safeEvaluationTrend = Array.isArray(analyticsData?.evaluation_trend)
    ? analyticsData.evaluation_trend
    : [];

  // Configuración de gráficos
  const evaluationTrendData = {
    labels: safeEvaluationTrend.map(item => {
      const [year, month] = item.month.split('-');
      return `${month}/${year}`;
    }),
    datasets: [
      {
        label: 'Número de Evaluaciones',
        data: safeEvaluationTrend.map(item => item.count),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        yAxisID: 'y',
      },
      {
        label: 'Puntuación Promedio',
        data: safeEvaluationTrend.map(item => item.avg_score),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        yAxisID: 'y1',
      },
    ],
  };

  const evaluationTrendOptions = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: 'Tendencia de Evaluaciones (Últimos 6 meses)',
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Número de Evaluaciones',
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Puntuación Promedio',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const scoreDistributionData = {
    labels: ['1-2', '3-4', '5-6', '7-8', '9-10'],
    datasets: [
      {
        data: analyticsData?.score_distribution ? Object.values(analyticsData.score_distribution) : [],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(234, 179, 8, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(16, 185, 129, 0.8)',
        ],
        borderColor: [
          'rgb(239, 68, 68)',
          'rgb(245, 158, 11)',
          'rgb(234, 179, 8)',
          'rgb(34, 197, 94)',
          'rgb(16, 185, 129)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const scoreDistributionOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Distribución de Puntuaciones (Últimas 20 evaluaciones)',
      },
    },
  };

  const objectiveStatusData = {
    labels: ['Pendientes', 'En Progreso', 'Completados', 'Cancelados'],
    datasets: [
      {
        data: analyticsData?.objective_status ? Object.values(analyticsData.objective_status) : [],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(156, 163, 175, 0.8)',
        ],
        borderColor: [
          'rgb(239, 68, 68)',
          'rgb(251, 191, 36)',
          'rgb(34, 197, 94)',
          'rgb(156, 163, 175)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const objectiveStatusOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Estado de Objetivos',
      },
    },
  };

  const attendanceData = {
    labels: analyticsData?.attendance_by_subject ? analyticsData.attendance_by_subject.map(item => item.subject) : [],
    datasets: [
      {
        label: 'Presente',
        data: analyticsData?.attendance_by_subject ? analyticsData.attendance_by_subject.map(item => item.present) : [],
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
      },
      {
        label: 'Ausente',
        data: analyticsData?.attendance_by_subject ? analyticsData.attendance_by_subject.map(item => item.absent) : [],
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
      },
    ],
  };

  const attendanceOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Asistencia por Asignatura (Último mes)',
      },
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
      },
    },
  };

  const renderChart = () => {
    switch (activeChart) {
      case 'trend':
        return <Line data={evaluationTrendData} options={evaluationTrendOptions} />;
      case 'scores':
        return <Doughnut data={scoreDistributionData} options={scoreDistributionOptions} />;
      case 'objectives':
        return <Doughnut data={objectiveStatusData} options={objectiveStatusOptions} />;
      case 'attendance':
        return <Bar data={attendanceData} options={attendanceOptions} />;
      default:
        return <Line data={evaluationTrendData} options={evaluationTrendOptions} />;
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
  <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
        <span className="mr-2">📊</span>
        Análisis del Progreso
      </h3>

      {/* Selector de gráficos */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-2">
          {[
            { key: 'trend', label: 'Tendencia', icon: '📈' },
            { key: 'scores', label: 'Puntuaciones', icon: '⭐' },
            { key: 'objectives', label: 'Objetivos', icon: '🎯' },
            { key: 'attendance', label: 'Asistencia', icon: '📅' },
          ].map((chart) => (
            <button
              key={chart.key}
              onClick={() => setActiveChart(chart.key)}
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                activeChart === chart.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <span className="mr-1">{chart.icon}</span>
              {chart.label}
            </button>
          ))}
        </div>
      </div>

      {/* Gráfico */}
      <div className="mb-4" style={{ height: '300px' }}>
        {renderChart()}
      </div>

      {/* Estadísticas resumen */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {analyticsData?.summary?.total_evaluations || 'N/A'}
          </div>
          <div className="text-xs text-blue-800">Evaluaciones Totales</div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {analyticsData?.summary?.avg_evaluation_score || 'N/A'}
          </div>
          <div className="text-xs text-green-800">Puntuación Promedio</div>
        </div>
        <div className="bg-purple-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {analyticsData?.summary?.completion_rate ? `${analyticsData.summary.completion_rate}%` : 'N/A'}
          </div>
          <div className="text-xs text-purple-800">Objetivos Completados</div>
        </div>
        <div className="bg-orange-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">
            {analyticsData?.summary?.attendance_percentage ? `${analyticsData.summary.attendance_percentage}%` : 'N/A'}
          </div>
          <div className="text-xs text-orange-800">Asistencia General</div>
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        💡 Los gráficos muestran el progreso del estudiante en diferentes áreas. Actualizado en tiempo real.
      </div>
    </div>
  );
};

export default WidgetGraficosAnaliticos;