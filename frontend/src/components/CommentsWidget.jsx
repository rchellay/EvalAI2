import { MessageSquare } from 'lucide-react';

export default function CommentsWidget({ comments }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;
    
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  const getColorFromName = (name) => {
    const colors = [
      '#3b86e3', '#f59e0b', '#10b981', '#8b5cf6', '#ef4444', 
      '#06b6d4', '#ec4899', '#f97316'
    ];
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Últimos Comentarios
      </h3>
      <ul className="space-y-4 max-h-64 overflow-y-auto">
        {comments && comments.length > 0 ? (
          comments.map((comment) => {
            const color = getColorFromName(comment.student_name);
            return (
              <li key={comment.id} className="flex items-start gap-3">
                <div 
                  className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold"
                  style={{ backgroundColor: color }}
                >
                  {getInitials(comment.student_name)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium text-slate-800 dark:text-slate-200 text-sm">
                      Comentario de {comment.student_name}
                    </p>
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex-shrink-0">
                      {formatDate(comment.created_at)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                    {comment.content}
                  </p>
                  {comment.subject && (
                    <span className="inline-block mt-1 px-2 py-0.5 text-xs rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                      {comment.subject}
                    </span>
                  )}
                </div>
              </li>
            );
          })
        ) : (
          <p className="text-center text-slate-500 dark:text-slate-400 py-4">
            No hay comentarios recientes
          </p>
        )}
      </ul>
    </div>
  );
}
