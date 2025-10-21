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
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b86e3" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b86e3" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="date" 
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1e293b', 
                border: 'none', 
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="count" 
              stroke="#3b86e3" 
              strokeWidth={3}
              fill="url(#colorActivity)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
