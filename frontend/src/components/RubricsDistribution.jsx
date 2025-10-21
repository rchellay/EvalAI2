// TEMPORALMENTE COMENTADO PARA VERCEL BUILD
// import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = ['#3b86e3', '#e2e8f0'];

export default function RubricsDistribution({ data }) {
  const chartData = [
    { name: 'Aplicadas', value: data.applied },
    { name: 'Pendientes', value: data.pending }
  ];

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Distribución de Rúbricas
      </h3>
      <div className="h-64 flex items-center justify-center relative">
        {/* Gráfico temporalmente deshabilitado */}
        <div className="text-center">
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {data.percent_applied}%
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">Aplicadas</p>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
            Aplicadas: {data.applied} | Pendientes: {data.pending}
          </p>
        </div>
      </div>
    </div>
  );
}
