import { Calendar, MapPin } from 'lucide-react';

export default function EventsWidget({ events }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { 
      day: 'numeric', 
      month: 'long',
      year: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Próximos Eventos
      </h3>
      <ul className="space-y-4 max-h-64 overflow-y-auto">
        {events && events.length > 0 ? (
          events.map((event) => (
            <li key={event.id} className="flex items-start gap-4">
              <div 
                className="flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-lg"
                style={{ 
                  backgroundColor: `${event.color}20`,
                  color: event.color
                }}
              >
                <Calendar size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-800 dark:text-slate-200 truncate">
                  {event.title}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {formatDate(event.start_time)}
                  {!event.all_day && ` - ${formatTime(event.start_time)}`}
                </p>
                {event.location && (
                  <p className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1 mt-1">
                    <MapPin size={12} />
                    {event.location}
                  </p>
                )}
              </div>
            </li>
          ))
        ) : (
          <p className="text-center text-slate-500 dark:text-slate-400 py-4">
            No hay eventos próximos
          </p>
        )}
      </ul>
    </div>
  );
}
