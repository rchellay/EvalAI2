import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/axios";
import { Users, ChevronRight } from 'lucide-react';

export default function Students() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/students")
      .then(res => {
        const studentsData = res.data.results || res.data;
        setStudents(studentsData || []);
        setLoading(false);
      })
      .catch(e => {
        console.error("Error loading students:", e);
        setError("No se pudieron cargar los alumnos");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Cargando estudiantes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Users size={28} />
            Estudiantes
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Gestiona la información de tus estudiantes
          </p>
        </div>
        <button 
          onClick={() => navigate('/estudiantes/nuevo')}
          className="flex items-center gap-1 text-primary font-semibold text-sm hover:text-primary/80 transition"
        >
          <span className="material-symbols-outlined text-base">add_circle</span>
          <span>Nuevo</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {students.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 p-8 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800 text-center">
          <Users size={48} className="mx-auto text-slate-400 mb-4" />
          <p className="text-slate-600 dark:text-slate-400">No hay estudiantes registrados</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {students.map(student => (
            <div 
              key={student.id}
              onClick={() => navigate(`/estudiantes/${student.id}`)}
              className="bg-white dark:bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800 hover:shadow-md hover:border-blue-500 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-lg">
                    {(student.name || student.username || '?')[0].toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white">
                      {student.name || student.username || 'Sin nombre'}
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {student.email || 'Sin email'}
                    </p>
                  </div>
                </div>
                <ChevronRight className="text-slate-400 group-hover:text-blue-500 transition-colors" size={20} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
