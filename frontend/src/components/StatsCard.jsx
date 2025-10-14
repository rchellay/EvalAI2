export default function StatsCard({ title, value, icon: Icon, color = 'blue' }) {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    orange: 'bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
            {title}
          </p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {value}
          </p>
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg ${colorClasses[color] || colorClasses.blue}`}>
            <Icon size={24} />
          </div>
        )}
      </div>
    </div>
  );
}
