import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function ScheduleWidget({ schedule }) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  const daysOfWeek = ['D', 'L', 'M', 'X', 'J', 'V', 'S'];
  const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  
  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    return { firstDay, daysInMonth };
  };
  
  const { firstDay, daysInMonth } = getDaysInMonth(currentMonth);
  const today = new Date().getDate();
  const isCurrentMonth = currentMonth.getMonth() === new Date().getMonth() && 
                         currentMonth.getFullYear() === new Date().getFullYear();
  
  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };
  
  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Horario del día
      </h3>
      
      {/* Calendar Navigator */}
      <div className="flex items-center justify-between mb-4">
        <button 
          onClick={prevMonth}
          className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <ChevronLeft size={20} />
        </button>
        <p className="font-semibold text-slate-900 dark:text-white">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </p>
        <button 
          onClick={nextMonth}
          className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <ChevronRight size={20} />
        </button>
      </div>
      
      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1 text-center text-sm mb-4">
        {daysOfWeek.map(day => (
          <span key={day} className="text-slate-500 dark:text-slate-400 font-medium p-2">
            {day}
          </span>
        ))}
        
        {/* Empty cells for days before month starts */}
        {Array.from({ length: firstDay }).map((_, i) => (
          <span key={`empty-${i}`} className="p-2"></span>
        ))}
        
        {/* Days of month */}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1;
          const isToday = isCurrentMonth && day === today;
          
          return (
            <span
              key={day}
              className={`
                p-2 rounded-full transition-colors
                ${isToday 
                  ? 'bg-blue-600 text-white font-bold' 
                  : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'
                }
              `}
            >
              {day}
            </span>
          );
        })}
      </div>
      
      {/* Today's Schedule */}
      <div className="mt-4 space-y-3 max-h-64 overflow-y-auto">
        {schedule && schedule.length > 0 ? (
          schedule.map((item, index) => (
            <div
              key={index}
              className="flex items-center gap-4 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20"
            >
              <div 
                className="w-2 h-12 rounded-full"
                style={{ backgroundColor: item.color || '#3b86e3' }}
              ></div>
              <div className="flex-1">
                <p className="font-semibold text-slate-900 dark:text-white">
                  {item.subject}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {item.start_time} - {item.end_time}
                </p>
                {item.classroom && (
                  <p className="text-xs text-slate-400 dark:text-slate-500">
                    {item.classroom}
                  </p>
                )}
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-slate-500 dark:text-slate-400 py-4">
            No hay clases programadas para hoy
          </p>
        )}
      </div>
    </div>
  );
}
