// TEMPORALMENTE COMENTADO PARA VERCEL BUILD  
// import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

export default function ActivityChart({ data }) {
  // Transform data for chart
  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
    count: item.count
  }));

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Actividad
      </h3>
      <div className="h-64">
      {/* Gráfico temporalmente deshabilitado */}
      <div className="h-full flex items-center justify-center bg-gray-50 rounded">
        <div className="text-center">
          <div className="text-lg font-bold text-blue-600">
            {chartData.length > 0 ? chartData[chartData.length - 1]?.count || 0 : 0}
          </div>
          <div className="text-sm text-blue-800">Actividad Reciente</div>
          <div className="text-xs text-gray-500 mt-1">
            {chartData.length} registros
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
