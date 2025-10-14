import { useState, useEffect } from "react";
import api from "../lib/axios";
import { Users, FileText, TrendingUp } from 'lucide-react';
import StatsCard from '../components/StatsCard';
import ActivityChart from '../components/ActivityChart';
import RubricsDistribution from '../components/RubricsDistribution';
import ScheduleWidget from '../components/ScheduleWidget';
import EventsWidget from '../components/EventsWidget';
import CommentsWidget from '../components/CommentsWidget';

export default function Dashboard() {
  const [stats, setStats] = useState({
    studentsCount: 0,
    transcriptsCount: 0,
    attendance: 0,
    activity: [],
    rubrics: { applied: 0, pending: 0, percent_applied: 0 },
    schedule: [],
    events: [],
    comments: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [
          studentsRes,
          transcriptsRes,
          attendanceRes,
          activityRes,
          rubricsRes,
          scheduleRes,
          eventsRes,
          commentsRes
        ] = await Promise.all([
          api.get("/dashboard/stats/students-count"),
          api.get("/dashboard/stats/transcripts-count"),
          api.get("/dashboard/stats/attendance"),
          api.get("/dashboard/stats/activity-last-7-days"),
          api.get("/dashboard/stats/rubrics-distribution"),
          api.get("/dashboard/schedule/today"),
          api.get("/dashboard/events/upcoming"),
          api.get("/dashboard/comments/latest")
        ]);

        setStats({
          studentsCount: studentsRes.data.count,
          transcriptsCount: transcriptsRes.data.count,
          attendance: attendanceRes.data.percent,
          activity: activityRes.data.activity || [],
          rubrics: rubricsRes.data,
          schedule: scheduleRes.data.schedule || [],
          events: eventsRes.data.events || [],
          comments: commentsRes.data.comments || []
        });
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatsCard 
          title="Estudiantes" 
          value={stats.studentsCount}
          icon={Users}
          color="blue"
        />
        <StatsCard 
          title="Transcripciones" 
          value={stats.transcriptsCount}
          icon={FileText}
          color="green"
        />
        <StatsCard 
          title="Asistencia" 
          value={`${stats.attendance}%`}
          icon={TrendingUp}
          color="orange"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActivityChart data={stats.activity} />
        </div>
        <div>
          <RubricsDistribution data={stats.rubrics} />
        </div>
      </div>

      {/* Schedule and Events Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ScheduleWidget schedule={stats.schedule} />
        </div>
        <div className="space-y-6">
          <EventsWidget events={stats.events} />
          <CommentsWidget comments={stats.comments} />
        </div>
      </div>
    </div>
  );
}
