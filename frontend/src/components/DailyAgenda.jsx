import React, { useState, useEffect } from "react";
import api from "../lib/axios";
import { toast } from "react-hot-toast";
import { format, startOfDay, endOfDay } from "date-fns";
import { es } from "date-fns/locale";

export default function DailyAgenda() {
  const [todayEvents, setTodayEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const today = new Date();

  useEffect(() => {
    fetchTodayEvents();
  }, []);

  const fetchTodayEvents = async () => {
    setLoading(true);
    try {
      const dayStart = startOfDay(today);
      const dayEnd = endOfDay(today);

      const res = await api.get("/calendar/events", {
        params: {
          start: dayStart.toISOString(),
          end: dayEnd.toISOString(),
        },
      });

      // Sort events by start time
      const sorted = res.data.sort((a, b) => 
        new Date(a.start_at) - new Date(b.start_at)
      );
      
      setTodayEvents(sorted);
    } catch (e) {
      console.error("Error loading today's events:", e);
      toast.error("Error cargando agenda del día");
    } finally {
      setLoading(false);
    }
  };

  const formatEventTime = (event) => {
    if (event.all_day) return "Todo el día";
    
    const start = new Date(event.start_at);
    const end = new Date(event.end_at);
    
    return `${format(start, "h:mm a", { locale: es })} - ${format(end, "h:mm a", { locale: es })}`;
  };

  const getEventColor = (event) => {
    if (event.color) return event.color;
    
    // Default colors based on event type
    const colorMap = {
      class: "#10b981", // green
      exam: "#ef4444", // red
      assignment: "#f59e0b", // orange
      meeting: "#3b82f6", // blue
      other: "#6b7280", // gray
    };
    
    return colorMap[event.event_type] || colorMap.other;
  };

  const isCurrentEvent = (event) => {
    if (event.all_day) return false;
    
    const now = new Date();
    const start = new Date(event.start_at);
    const end = new Date(event.end_at);
    
    return now >= start && now <= end;
  };

  return (
    <aside className="w-80 flex-shrink-0 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <h2 className="text-xl font-bold text-gray-800 dark:text-white">
          StudyFlow
        </h2>
      </div>

      {/* Date Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
        <h3 className="text-lg font-bold text-gray-800 dark:text-white">
          {format(today, "EEEE, MMMM d", { locale: es })}
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Agenda de Hoy
        </p>
      </div>

      {/* Events List */}
      <div className="flex-grow overflow-y-auto px-2">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : todayEvents.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-gray-500 dark:text-gray-400">
              No hay eventos programados para hoy
            </p>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {todayEvents.map((event) => (
              <div
                key={event.id}
                className={`flex items-start gap-4 p-3 rounded-lg transition-all ${
                  isCurrentEvent(event)
                    ? "bg-blue-50 dark:bg-blue-900/20 ring-2 ring-blue-500"
                    : "hover:bg-gray-100 dark:hover:bg-gray-800/50"
                }`}
              >
                {/* Color indicator */}
                <div
                  className="w-1.5 h-16 rounded-full flex-shrink-0"
                  style={{ backgroundColor: getEventColor(event) }}
                ></div>

                {/* Event details */}
                <div className="flex-grow min-w-0">
                  <p className="font-semibold text-gray-800 dark:text-white truncate">
                    {event.title}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {formatEventTime(event)}
                  </p>
                  {event.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                      {event.description}
                    </p>
                  )}
                </div>

                {/* Drag indicator */}
                <svg
                  className="w-5 h-5 text-gray-400 dark:text-gray-500 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M9 5h2v2H9V5zm0 6h2v2H9v-2zm0 6h2v2H9v-2zm6-12h2v2h-2V5zm0 6h2v2h-2v-2zm0 6h2v2h-2v-2z" />
                </svg>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800">
        <button
          onClick={fetchTodayEvents}
          disabled={loading}
          className="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Cargando..." : "Actualizar Agenda"}
        </button>
      </div>
    </aside>
  );
}
