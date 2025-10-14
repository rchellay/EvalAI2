import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  School, 
  Users, 
  UsersRound,
  ClipboardList, 
  MessageSquare, 
  Calendar, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  ClipboardCheck
} from 'lucide-react';

const menuItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/asignaturas', icon: School, label: 'Asignaturas' },
  { path: '/grupos', icon: UsersRound, label: 'Grupos' },
  { path: '/asistencia', icon: ClipboardCheck, label: 'Asistencia' },
  { path: '/rubricas', icon: ClipboardList, label: 'Rúbricas' },
  { path: '/comentarios', icon: MessageSquare, label: 'Comentarios' },
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
                  ? 'bg-blue-600 text-white' 
                  : 'hover:bg-slate-700 text-slate-300'
                }
                ${collapsed ? 'justify-center' : ''}
              `}
              title={collapsed ? item.label : ''}
            >
              <Icon size={20} className={collapsed ? '' : 'mr-3'} />
              {!collapsed && <span>{item.label}</span>}
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
