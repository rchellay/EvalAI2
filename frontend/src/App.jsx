import { BrowserRouter, Routes, Route, useNavigate, Outlet } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Students from "./pages/Students";
import StudentProfilePage from "./pages/StudentProfilePage";
import StudentEvaluationPanel from "./pages/StudentEvaluationPanel";
import StudentFormPage from "./pages/StudentFormPage";
import SubjectsPage from "./pages/SubjectsPage";
import GroupsPage from "./pages/GroupsPage";
import GroupDetailPage from "./pages/GroupDetailPage";
import SubjectDetailPage from "./pages/SubjectDetailPage";
import CalendarView from "./components/CalendarView";
import RubricsPage from "./pages/RubricsPage";
import RubricEditorPage from "./pages/RubricEditorPage";
import RubricApplyPage from "./pages/RubricApplyPage";
import RubricResultsPage from "./pages/RubricResultsPage";
import AttendancePage from "./pages/AttendancePage";
import ProtectedRoute from './auth/ProtectedRoute';
import InformesPage from './pages/InformesPage';
import CorreccionPage from './pages/CorreccionPage';
import EvidenciasCorreccionPage from './pages/EvidenciasCorreccionPage';
import SettingsPage from './pages/SettingsPage';
import ToasterProvider from './ui/ToasterProvider';
import Sidebar from './components/Sidebar';
import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import api from './lib/axios';

function TopBar() {
  const navigate = useNavigate();
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  const [user, setUser] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  
  useEffect(() => {
    const root = document.documentElement;    
    if (theme === 'dark') root.classList.add('dark'); else root.classList.remove('dark');
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.get('/auth/me')
        .then(r => setUser(r.data))
        .catch(() => setUser(null));
    }
  }, []);
  
  const logout = () => { 
    localStorage.removeItem('token'); 
    navigate('/'); 
  };

  return (
    <header className="flex items-center justify-between h-16 px-6 bg-white dark:bg-slate-900 shadow-sm border-b border-slate-200 dark:border-slate-800">
      <h2 className="text-lg font-semibold text-slate-900 dark:text-white">EvalIA</h2>
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-full text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
          title="Cambiar tema"
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <button className="p-2 rounded-full text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
          <Bell size={20} />
        </button>
        <div className="relative">
          <button 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 focus:outline-none"
          >
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              {user?.username || 'Usuario'}
            </span>
          </button>
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-xl z-10 border border-slate-200 dark:border-slate-700">
              <button
                onClick={logout}
                className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
              >
                Cerrar Sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <ToasterProvider />
      <div className="app-shell">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route element={<LayoutWithSidebar />}> 
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/students" element={<ProtectedRoute><Students /></ProtectedRoute>} />
            <Route path="/estudiantes" element={<ProtectedRoute><Students /></ProtectedRoute>} />
            <Route path="/estudiantes/nuevo" element={<ProtectedRoute><StudentFormPage /></ProtectedRoute>} />
            <Route path="/estudiantes/:id/editar" element={<ProtectedRoute><StudentFormPage /></ProtectedRoute>} />
            <Route path="/estudiantes/:id" element={<ProtectedRoute><StudentEvaluationPanel /></ProtectedRoute>} />
            <Route path="/asignaturas" element={<ProtectedRoute><SubjectsPage /></ProtectedRoute>} />
            <Route path="/asignaturas/:id" element={<ProtectedRoute><SubjectDetailPage /></ProtectedRoute>} />
            <Route path="/grupos" element={<ProtectedRoute><GroupsPage /></ProtectedRoute>} />
            <Route path="/grupos/:id" element={<ProtectedRoute><GroupDetailPage /></ProtectedRoute>} />
            <Route path="/transcripciones" element={<ProtectedRoute><PlaceholderPage title="Transcripciones" /></ProtectedRoute>} />
            <Route path="/rubricas" element={<ProtectedRoute><RubricsPage /></ProtectedRoute>} />
            <Route path="/rubricas/nueva" element={<ProtectedRoute><RubricEditorPage /></ProtectedRoute>} />
            <Route path="/rubricas/:id/editar" element={<ProtectedRoute><RubricEditorPage /></ProtectedRoute>} />
            <Route path="/rubricas/:id/aplicar" element={<ProtectedRoute><RubricApplyPage /></ProtectedRoute>} />
            <Route path="/rubricas/aplicar" element={<ProtectedRoute><RubricApplyPage /></ProtectedRoute>} />
            <Route path="/rubricas/:id/resultados" element={<ProtectedRoute><RubricResultsPage /></ProtectedRoute>} />
            <Route path="/rubricas/resultados" element={<ProtectedRoute><RubricResultsPage /></ProtectedRoute>} />
            <Route path="/asistencia" element={<ProtectedRoute><AttendancePage /></ProtectedRoute>} />
            <Route path="/correccion" element={<ProtectedRoute><CorreccionPage /></ProtectedRoute>} />
            <Route path="/evidencias-correccion/:studentId" element={<ProtectedRoute><EvidenciasCorreccionPage /></ProtectedRoute>} />
            <Route path="/calendario" element={<ProtectedRoute><CalendarView /></ProtectedRoute>} />
            <Route path="/informes" element={<ProtectedRoute><InformesPage /></ProtectedRoute>} />
            <Route path="/ajustes" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          </Route>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

function LayoutWithSidebar() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function PlaceholderPage({ title }) {
  return (
    <div className="p-6">
      <div className="bg-white dark:bg-slate-900 p-8 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">{title}</h1>
        <p className="text-slate-600 dark:text-slate-400">Esta sección está en desarrollo.</p>
      </div>
    </div>
  );
}

export default App;
