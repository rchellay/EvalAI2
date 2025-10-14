import React, { useState, useEffect } from "react";
import api from "../lib/axios";

export default function CalendarStats() {
  const [stats, setStats] = useState({
    totalEvents: 0,
    classesScheduled: 0,
    upcomingEvents: 0,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const now = new Date();
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);

      const res = await api.get("/calendar/events", {
        params: {
          start: startOfMonth.toISOString(),
          end: endOfMonth.toISOString(),
        },
      });

      const events = res.data;
      const classes = events.filter((e) => e.event_type === "class");
      const upcoming = events.filter(
        (e) => new Date(e.start_at) > now
      );

      setStats({
        totalEvents: events.length,
        classesScheduled: classes.length,
        upcomingEvents: upcoming.length,
      });
    } catch (e) {
      console.error("Error loading stats:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Total Events Card */}
      <div className="p-6 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
              Eventos Este Mes
            </h4>
            <p className="mt-2 text-3xl font-bold text-gray-800 dark:text-white">
              {loading ? "..." : stats.totalEvents}
            </p>
          </div>
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <svg
              className="w-6 h-6 text-blue-600 dark:text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Classes Scheduled Card */}
      <div className="p-6 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
              Clases Programadas
            </h4>
            <p className="mt-2 text-3xl font-bold text-gray-800 dark:text-white">
              {loading ? "..." : stats.classesScheduled}
            </p>
          </div>
          <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
            <svg
              className="w-6 h-6 text-green-600 dark:text-green-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Upcoming Events Card */}
      <div className="p-6 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
              Eventos Próximos
            </h4>
            <p className="mt-2 text-3xl font-bold text-gray-800 dark:text-white">
              {loading ? "..." : stats.upcomingEvents}
            </p>
          </div>
          <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
            <svg
              className="w-6 h-6 text-orange-600 dark:text-orange-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
