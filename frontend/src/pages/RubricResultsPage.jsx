// frontend/src/pages/RubricResultsPage.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js';
import { Radar, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
);

const RubricResultsPage = () => {
  const navigate = useNavigate();
  const { id: rubricIdFromUrl } = useParams();
  
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  
  // Filters
  const [rubrics, setRubrics] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedRubricId, setSelectedRubricId] = useState(rubricIdFromUrl || '');
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  
  // Data
  const [results, setResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  
  // Charts data
  const [radarData, setRadarData] = useState(null);
  const [barData, setBarData] = useState(null);

  useEffect(() => {
    loadFiltersData();
  }, []);

  useEffect(() => {
    if (rubrics.length > 0) {
      loadResults();
    }
  }, [selectedRubricId, selectedStudentId, dateFrom, dateTo]);

  const loadFiltersData = async () => {
    try {
      const [rubricsRes, studentsRes] = await Promise.all([
        api.get('/rubrics/'),
        api.get('/students/')
      ]);
      
      setRubrics(rubricsRes.data.results || rubricsRes.data);
      setStudents(studentsRes.data.results || studentsRes.data);
    } catch (error) {
      console.error('Error loading filters:', error);
      toast.error('Error al cargar filtros');
    }
  };

  const loadResults = async () => {
    try {
      setLoading(true);
      
      const params = {};
      if (selectedRubricId) params.rubric = selectedRubricId;
      if (selectedStudentId) params.student = selectedStudentId;
      if (dateFrom) params.evaluated_at__gte = dateFrom;
      if (dateTo) params.evaluated_at__lte = dateTo;
      
      const response = await api.get('/rubric-scores/', { params });
      const scoresData = response.data.results || response.data;
      
      // Group scores by evaluation session
      const groupedResults = groupByEvaluationSession(scoresData);
      setResults(groupedResults);
      
      // Generate charts if we have a selected rubric
      if (selectedRubricId && groupedResults.length > 0) {
        await generateCharts(groupedResults, selectedRubricId);
      }
    } catch (error) {
      console.error('Error loading results:', error);
      toast.error('Error al cargar resultados');
    } finally {
      setLoading(false);
    }
  };

  const groupByEvaluationSession = (scores) => {
    const grouped = {};
    
    scores.forEach(score => {
      const sessionId = score.evaluation_session_id || `${score.student}-${score.rubric}`;
      
      if (!grouped[sessionId]) {
        grouped[sessionId] = {
          id: sessionId,
          rubric: score.rubric,
          rubric_title: score.rubric_title || 'Rúbrica',
          student: score.student,
          student_name: score.student_name || 'Estudiante',
          evaluator: score.evaluator,
          evaluated_at: score.evaluated_at,
          scores: [],
          total_score: 0,
          criteria_count: 0
        };
      }
      
      grouped[sessionId].scores.push(score);
    });
    
    // Calculate totals and averages
    Object.values(grouped).forEach(session => {
      let totalWeightedScore = 0;
      let totalWeight = 0;
      
      session.scores.forEach(score => {
        const weight = parseFloat(score.criterion_weight) || 1;
        const scoreValue = parseFloat(score.level_score) || 0;
        totalWeightedScore += scoreValue * weight;
        totalWeight += weight;
      });
      
      session.total_score = totalWeight > 0 ? (totalWeightedScore / totalWeight).toFixed(2) : 0;
      session.criteria_count = session.scores.length;
    });
    
    return Object.values(grouped).sort((a, b) => 
      new Date(b.evaluated_at) - new Date(a.evaluated_at)
    );
  };

  const generateCharts = async (resultsData, rubricId) => {
    try {
      // Load rubric details
      const rubricResponse = await api.get(`/rubrics/${rubricId}/`);
      const rubricData = rubricResponse.data;
      
      const criteriaResponse = await api.get(`/rubric-criteria/`, {
        params: { rubric: rubricId }
      });
      const criteriaData = criteriaResponse.data.results || criteriaResponse.data;
      
      // Prepare radar chart data
      const criteriaNames = criteriaData.sort((a, b) => a.order - b.order).map(c => c.name);
      
      // Get average scores per criterion across all evaluations
      const criteriaScores = {};
      criteriaData.forEach(criterion => {
        criteriaScores[criterion.id] = [];
      });
      
      resultsData.forEach(result => {
        result.scores.forEach(score => {
          if (criteriaScores[score.criterion]) {
            criteriaScores[score.criterion].push(parseFloat(score.level_score) || 0);
          }
        });
      });
      
      const averageScores = Object.keys(criteriaScores).map(criterionId => {
        const scores = criteriaScores[criterionId];
        return scores.length > 0 
          ? scores.reduce((a, b) => a + b, 0) / scores.length 
          : 0;
      });
      
      setRadarData({
        labels: criteriaNames,
        datasets: [{
          label: 'Puntuación Media',
          data: averageScores,
          backgroundColor: 'rgba(19, 127, 236, 0.2)',
          borderColor: 'rgba(19, 127, 236, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(19, 127, 236, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(19, 127, 236, 1)'
        }]
      });
      
      // Prepare bar chart data - top 10 students by score
      const studentAverages = {};
      resultsData.forEach(result => {
        if (!studentAverages[result.student_name]) {
          studentAverages[result.student_name] = [];
        }
        studentAverages[result.student_name].push(parseFloat(result.total_score));
      });
      
      const studentData = Object.entries(studentAverages)
        .map(([name, scores]) => ({
          name,
          average: scores.reduce((a, b) => a + b, 0) / scores.length
        }))
        .sort((a, b) => b.average - a.average)
        .slice(0, 10);
      
      setBarData({
        labels: studentData.map(s => s.name),
        datasets: [{
          label: 'Puntuación Media',
          data: studentData.map(s => s.average),
          backgroundColor: 'rgba(19, 127, 236, 0.6)',
          borderColor: 'rgba(19, 127, 236, 1)',
          borderWidth: 1
        }]
      });
      
    } catch (error) {
      console.error('Error generating charts:', error);
    }
  };

  const handleViewDetails = async (result) => {
    try {
      // Load full details including criterion and level names
      const scoresWithDetails = await Promise.all(
        result.scores.map(async (score) => {
          try {
            const [criterionRes, levelRes] = await Promise.all([
              api.get(`/rubric-criteria/${score.criterion}/`),
              api.get(`/rubric-levels/${score.level}/`)
            ]);
            return {
              ...score,
              criterion_name: criterionRes.data.name,
              criterion_description: criterionRes.data.description,
              level_name: levelRes.data.name,
              level_description: levelRes.data.description,
              level_score: levelRes.data.score,
              level_color: levelRes.data.color
            };
          } catch (err) {
            console.error('Error loading score details:', err);
            return score;
          }
        })
      );
      
      setSelectedResult({
        ...result,
        scores: scoresWithDetails
      });
      setDetailModalOpen(true);
    } catch (error) {
      console.error('Error loading details:', error);
      toast.error('Error al cargar detalles');
    }
  };

  const handleExport = async (format) => {
    try {
      setExporting(true);
      
      if (format === 'csv') {
        exportToCSV();
      } else if (format === 'pdf') {
        toast.info('Exportación a PDF en desarrollo');
      }
    } catch (error) {
      console.error('Error exporting:', error);
      toast.error('Error al exportar');
    } finally {
      setExporting(false);
    }
  };

  const exportToCSV = () => {
    if (results.length === 0) {
      toast.error('No hay resultados para exportar');
      return;
    }
    
    // CSV Headers
    const headers = [
      'Estudiante',
      'Rúbrica',
      'Fecha',
      'Puntuación Total',
      'Criterios Evaluados',
      'Evaluador'
    ];
    
    // CSV Rows
    const rows = results.map(result => [
      result.student_name,
      result.rubric_title,
      new Date(result.evaluated_at).toLocaleDateString(),
      result.total_score,
      result.criteria_count,
      result.evaluator || 'N/A'
    ]);
    
    // Generate CSV content
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `resultados_rubricas_${new Date().toISOString().slice(0, 10)}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast.success('CSV exportado correctamente');
  };

  const getLevelBadgeColor = (score) => {
    const percentage = (score / 10) * 100; // Assuming max score is 10
    if (percentage >= 75) return 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-400';
    if (percentage >= 50) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-400';
    if (percentage >= 25) return 'bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-400';
    return 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400';
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        ticks: {
          color: 'rgba(156, 163, 175, 1)'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.2)'
        },
        pointLabels: {
          color: 'rgba(107, 114, 128, 1)',
          font: {
            size: 12
          }
        }
      }
    },
    plugins: {
      legend: {
        labels: {
          color: 'rgba(107, 114, 128, 1)'
        }
      }
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: 'rgba(156, 163, 175, 1)'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.2)'
        }
      },
      x: {
        ticks: {
          color: 'rgba(156, 163, 175, 1)'
        },
        grid: {
          display: false
        }
      }
    },
    plugins: {
      legend: {
        labels: {
          color: 'rgba(107, 114, 128, 1)'
        }
      }
    }
  };

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
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Resultados de Rúbricas</h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Analiza y compara evaluaciones realizadas
              </p>
            </div>
          </div>
          <button
            onClick={() => loadResults()}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
          >
            <span className="material-symbols-outlined text-base">refresh</span>
            Actualizar
          </button>
        </div>

        {/* Filters */}
        <section className="bg-white dark:bg-card-dark p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Filtros
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Rúbrica
              </label>
              <select
                value={selectedRubricId}
                onChange={(e) => setSelectedRubricId(e.target.value)}
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              >
                <option value="">Todas</option>
                {rubrics.map(rubric => (
                  <option key={rubric.id} value={rubric.id}>
                    {rubric.title}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Estudiante
              </label>
              <select
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              >
                <option value="">Todos</option>
                {students.map(student => (
                  <option key={student.id} value={student.id}>
                    {student.name || student.username}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Desde
              </label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Hasta
              </label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-4 py-2 bg-background-light dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-primary focus:border-primary"
              />
            </div>
          </div>
        </section>

        {/* Charts */}
        {radarData && barData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <section className="bg-white dark:bg-card-dark p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Análisis por Criterios
              </h3>
              <div className="h-80">
                <Radar data={radarData} options={radarOptions} />
              </div>
            </section>
            
            <section className="bg-white dark:bg-card-dark p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Top 10 Estudiantes
              </h3>
              <div className="h-80">
                <Bar data={barData} options={barOptions} />
              </div>
            </section>
          </div>
        )}

        {/* Results Table */}
        <section className="bg-white dark:bg-card-dark p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Evaluaciones Realizadas ({results.length})
            </h3>
            <div className="flex gap-2">
              <button
                onClick={() => handleExport('csv')}
                disabled={exporting || results.length === 0}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <span className="material-symbols-outlined text-base">download</span>
                CSV
              </button>
              <button
                onClick={() => handleExport('pdf')}
                disabled={exporting || results.length === 0}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <span className="material-symbols-outlined text-base">picture_as_pdf</span>
                PDF
              </button>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : results.length === 0 ? (
            <div className="text-center py-12">
              <span className="material-symbols-outlined text-6xl text-gray-300 dark:text-gray-700">
                assessment
              </span>
              <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mt-4 mb-2">
                No hay evaluaciones registradas
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Aplica una rúbrica para ver los resultados aquí
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs uppercase bg-background-light dark:bg-background-dark">
                  <tr>
                    <th className="px-6 py-3 text-left">Estudiante</th>
                    <th className="px-6 py-3 text-left">Rúbrica</th>
                    <th className="px-6 py-3 text-left">Fecha</th>
                    <th className="px-6 py-3 text-center">Puntuación</th>
                    <th className="px-6 py-3 text-center">Criterios</th>
                    <th className="px-6 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => (
                    <tr 
                      key={result.id}
                      className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition"
                    >
                      <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                        {result.student_name}
                      </td>
                      <td className="px-6 py-4 text-gray-700 dark:text-gray-300">
                        {result.rubric_title}
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {new Date(result.evaluated_at).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getLevelBadgeColor(result.total_score)}`}>
                          {result.total_score}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center text-gray-700 dark:text-gray-300">
                        {result.criteria_count}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleViewDetails(result)}
                          className="text-primary hover:text-primary/80 font-medium transition"
                        >
                          Ver detalles
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>

      {/* Detail Modal */}
      {detailModalOpen && selectedResult && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-card-dark rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Detalles de Evaluación
                  </h2>
                  <p className="text-gray-500 dark:text-gray-400 mt-1">
                    {selectedResult.student_name} - {selectedResult.rubric_title}
                  </p>
                </div>
                <button
                  onClick={() => setDetailModalOpen(false)}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Summary */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-background-light dark:bg-background-dark p-4 rounded-lg">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Puntuación Total</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                    {selectedResult.total_score}
                  </p>
                </div>
                <div className="bg-background-light dark:bg-background-dark p-4 rounded-lg">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Criterios</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                    {selectedResult.criteria_count}
                  </p>
                </div>
                <div className="bg-background-light dark:bg-background-dark p-4 rounded-lg">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Fecha</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                    {new Date(selectedResult.evaluated_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                  </p>
                </div>
              </div>

              {/* Criteria Details */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Criterios Evaluados
                </h3>
                <div className="space-y-4">
                  {selectedResult.scores.map((score, index) => (
                    <div
                      key={index}
                      className="bg-background-light dark:bg-background-dark p-4 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {score.criterion_name || `Criterio ${score.criterion}`}
                          </h4>
                          {score.criterion_description && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              {score.criterion_description}
                            </p>
                          )}
                        </div>
                        <span
                          className="px-3 py-1 rounded-full text-xs font-semibold text-white"
                          style={{ backgroundColor: score.level_color || '#3b82f6' }}
                        >
                          {score.level_name || 'Nivel'}: {score.level_score}
                        </span>
                      </div>
                      {score.level_description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {score.level_description}
                        </p>
                      )}
                      {score.feedback && (
                        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            Comentario:
                          </p>
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            {score.feedback}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RubricResultsPage;
