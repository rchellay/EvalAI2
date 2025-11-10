import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  School, 
  Users, 
  UsersRound,
  ClipboardList, 
  Calendar, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  ClipboardCheck,
  BookOpen,
  QrCode,
  BrainCircuit
} from 'lucide-react';

const menuItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/asignaturas', icon: School, label: 'Asignaturas' },
  { path: '/grupos', icon: UsersRound, label: 'Grupos' },
  { path: '/asistencia', icon: ClipboardCheck, label: 'Asistencia' },
  { path: '/rubricas', icon: ClipboardList, label: 'Rúbricas' },
  { path: '/teacher/evaluations', icon: QrCode, label: 'Autoevaluaciones' },
  { path: '/teacher/ai-expert', icon: BrainCircuit, label: 'ComeniusAI', highlight: true },
  { path: '/correccion', icon: BookOpen, label: 'Corrección' },
  { path: '/calendario', icon: Calendar, label: 'Calendario' },
  { path: '/informes', icon: BarChart3, label: 'Informes' },
  { path: '/ajustes', icon: Settings, label: 'Ajustes' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  return (
    <aside 
      className={`
        flex flex-col bg-slate-800 text-white transition-all duration-300 ease-in-out
        ${collapsed ? 'w-20' : 'w-64'}
      `}
    >
      {/* Logo Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-slate-700">
        {!collapsed && <h1 className="text-xl font-bold">EvalIA</h1>}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-lg hover:bg-slate-700 ml-auto"
          title={collapsed ? 'Expandir' : 'Colapsar'}
        >
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-2 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center px-4 py-2.5 text-sm font-medium rounded-lg
                transition-colors duration-150
                ${isActive 
                  ? (item.highlight ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'bg-blue-600 text-white')
                  : (item.highlight ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-600 hover:to-purple-600 text-blue-100' : 'hover:bg-slate-700 text-slate-300')
                }
                ${collapsed ? 'justify-center' : ''}
              `}
              title={collapsed ? item.label : ''}
            >
              <Icon size={20} className={collapsed ? '' : 'mr-3'} />
              {!collapsed && (
                <span className="flex items-center">
                  {item.label}
                  {item.highlight && (
                    <span className="ml-2 px-2 py-0.5 text-xs bg-yellow-400 text-gray-900 rounded-full font-bold">
                      NUEVO
                    </span>
                  )}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Logout Button */}
      <div className="px-2 py-4 mt-auto border-t border-slate-700">
        <button
          onClick={handleLogout}
          className={`
            flex items-center w-full px-4 py-2.5 text-sm font-medium rounded-lg
            hover:bg-slate-700 text-slate-300 transition-colors
            ${collapsed ? 'justify-center' : ''}
          `}
          title={collapsed ? 'Logout' : ''}
        >
          <LogOut size={20} className={collapsed ? '' : 'mr-3'} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
