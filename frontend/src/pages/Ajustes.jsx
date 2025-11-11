import React, { useState, useEffect } from 'react';
import { 
  User, Mail, Building2, GraduationCap, Lock, LogOut, 
  Sun, Moon, Laptop, Type, Smartphone, Bell, Clock, 
  Download, Trash2, Shield, Database, Users, BookOpen,
  Calendar, Settings, ChevronRight, Save, Check
} from 'lucide-react';

const Ajustes = () => {
  const [activeSection, setActiveSection] = useState('perfil');
  const [saveStatus, setSaveStatus] = useState('');
  const [settings, setSettings] = useState({
    // Perfil y Cuenta
    displayName: '',
    email: '',
    centro: '',
    autoLogout: '30',
    
    // Centro y Año Académico
    añoAcademico: '2024-2025',
    nivelEducativo: 'Primaria',
    asignaturas: [],
    
    // Notificaciones
    notifInApp: {
      evaluaciones: true,
      informes: true,
      asistencia: true,
      grupos: true
    },
    notifEmail: true,
    recordatorios: '15',
    
    // Admin
    isAdmin: false
  });

  useEffect(() => {
    // Cargar ajustes del usuario
    const loadSettings = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${import.meta.env.VITE_API_URL}/user/settings/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setSettings(prev => ({ ...prev, ...data }));
        }
      } catch (error) {
        console.error('Error cargando ajustes:', error);
      }
    };
    loadSettings();
  }, []);

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/user/settings/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });
      
      if (response.ok) {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus(''), 3000);
      } else {
        setSaveStatus('error');
      }
    } catch (error) {
      console.error('Error guardando ajustes:', error);
      setSaveStatus('error');
    }
  };

  const sections = [
    { id: 'perfil', label: 'Perfil y Cuenta', icon: User },
    { id: 'centro', label: 'Centro y Año Académico', icon: Building2 },
    { id: 'notificaciones', label: 'Notificaciones', icon: Bell },
    { id: 'datos', label: 'Datos y Privacidad', icon: Shield },
    ...(settings.isAdmin ? [{ id: 'admin', label: 'Control Administrativo', icon: Database }] : [])
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar de navegación */}
      <div className="w-64 bg-white border-r border-gray-200 p-4">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Settings className="w-6 h-6" />
            Ajustes
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Personaliza tu entorno de trabajo
          </p>
        </div>

        <nav className="space-y-1">
          {sections.map(section => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  activeSection === section.id
                    ? 'bg-indigo-50 text-indigo-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm">{section.label}</span>
                {activeSection === section.id && (
                  <ChevronRight className="w-4 h-4 ml-auto" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Contenido principal */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-3xl mx-auto">
          {/* Perfil y Cuenta */}
          {activeSection === 'perfil' && (
            <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-1">Perfil y Cuenta</h2>
                <p className="text-sm text-gray-600">Información personal y configuración de sesión</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <User className="w-4 h-4" />
                    Nombre mostrado
                  </label>
                  <input
                    type="text"
                    value={settings.displayName}
                    onChange={(e) => setSettings({...settings, displayName: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Tu nombre"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Mail className="w-4 h-4" />
                    Correo electrónico
                  </label>
                  <input
                    type="email"
                    value={settings.email}
                    onChange={(e) => setSettings({...settings, email: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="tu@email.com"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Building2 className="w-4 h-4" />
                    Centro educativo asignado
                  </label>
                  <input
                    type="text"
                    value={settings.centro}
                    onChange={(e) => setSettings({...settings, centro: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Nombre del centro"
                  />
                </div>

                <div className="border-t pt-4">
                  <button className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium">
                    <Lock className="w-4 h-4" />
                    Cambiar contraseña
                  </button>
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <LogOut className="w-4 h-4" />
                    Cerrar sesión automáticamente tras
                  </label>
                  <select
                    value={settings.autoLogout}
                    onChange={(e) => setSettings({...settings, autoLogout: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="10">10 minutos</option>
                    <option value="20">20 minutos</option>
                    <option value="30">30 minutos</option>
                    <option value="60">1 hora</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Centro y Año Académico */}
          {activeSection === 'centro' && (
            <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-1">Centro y Año Académico</h2>
                <p className="text-sm text-gray-600">Configura el contexto educativo de tu trabajo</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="w-4 h-4" />
                    Año académico activo
                  </label>
                  <select
                    value={settings.añoAcademico}
                    onChange={(e) => setSettings({...settings, añoAcademico: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="2023-2024">2023–2024</option>
                    <option value="2024-2025">2024–2025</option>
                    <option value="2025-2026">2025–2026</option>
                  </select>
                  <button className="mt-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium">
                    + Crear nuevo año académico (clonar configuraciones)
                  </button>
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Building2 className="w-4 h-4" />
                    Centro educativo
                  </label>
                  <input
                    type="text"
                    value={settings.centro}
                    onChange={(e) => setSettings({...settings, centro: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Nombre del centro"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <GraduationCap className="w-4 h-4" />
                    Nivel educativo en el que trabajas
                  </label>
                  <select
                    value={settings.nivelEducativo}
                    onChange={(e) => setSettings({...settings, nivelEducativo: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="Educación Infantil">Educación Infantil</option>
                    <option value="Primaria">Primaria</option>
                    <option value="Secundaria">Secundaria</option>
                    <option value="Bachillerato">Bachillerato</option>
                  </select>
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <BookOpen className="w-4 h-4" />
                    Asignaturas habituales
                  </label>
                  <p className="text-sm text-gray-500 mb-2">Sugerencias basadas en tu uso</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm">Matemáticas</span>
                    <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm">Lengua</span>
                    <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm">Ciencias</span>
                    <button className="px-3 py-1 border-2 border-dashed border-gray-300 text-gray-600 rounded-full text-sm hover:border-indigo-400 hover:text-indigo-600">
                      + Añadir
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Notificaciones */}
          {activeSection === 'notificaciones' && (
            <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-1">Notificaciones</h2>
                <p className="text-sm text-gray-600">Controla cómo y cuándo recibes avisos</p>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="flex items-center gap-2 font-medium text-gray-800 mb-3">
                    <Bell className="w-5 h-5" />
                    Notificaciones en la app
                  </h3>
                  <div className="space-y-2">
                    {[
                      { key: 'evaluaciones', label: 'Evaluaciones pendientes' },
                      { key: 'informes', label: 'Informes generados' },
                      { key: 'asistencia', label: 'Recordatorios automáticos de asistencia' },
                      { key: 'grupos', label: 'Cambios en grupos' }
                    ].map(notif => (
                      <label key={notif.key} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                        <span className="text-gray-700">{notif.label}</span>
                        <input
                          type="checkbox"
                          checked={settings.notifInApp[notif.key]}
                          onChange={(e) => setSettings({
                            ...settings,
                            notifInApp: {
                              ...settings.notifInApp,
                              [notif.key]: e.target.checked
                            }
                          })}
                          className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                        />
                      </label>
                    ))}
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Mail className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="font-medium text-gray-800">Notificaciones por correo</p>
                        <p className="text-sm text-gray-600">Recibe resúmenes en tu email</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifEmail}
                        onChange={(e) => setSettings({...settings, notifEmail: e.target.checked})}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Clock className="w-4 h-4" />
                    Recordatorios previos a sesiones o evaluaciones
                  </label>
                  <select
                    value={settings.recordatorios}
                    onChange={(e) => setSettings({...settings, recordatorios: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="5">5 minutos antes</option>
                    <option value="15">15 minutos antes</option>
                    <option value="60">1 hora antes</option>
                    <option value="1440">1 día antes</option>
                  </select>
                </div>

                <button className="w-full py-2 px-4 border-2 border-indigo-200 text-indigo-600 rounded-lg hover:bg-indigo-50 font-medium transition-colors">
                  📩 Enviar notificación de prueba
                </button>
              </div>
            </div>
          )}

          {/* Datos y Privacidad */}
          {activeSection === 'datos' && (
            <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-1">Datos y Privacidad</h2>
                <p className="text-sm text-gray-600">Gestiona tu información personal de forma segura</p>
              </div>

              <div className="space-y-4">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="flex items-center gap-2 font-medium text-blue-900 mb-2">
                    <Shield className="w-5 h-5" />
                    Tratamiento de datos personales
                  </h3>
                  <p className="text-sm text-blue-800 mb-3">
                    Cumplimos con el RGPD y protegemos tu información educativa.
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 font-medium text-sm">
                    📄 Ver política completa de privacidad
                  </button>
                </div>

                <div className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="flex items-center gap-2 font-medium text-gray-800 mb-2">
                    <Download className="w-5 h-5" />
                    Exportar mis datos
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Descarga toda tu información en formato JSON
                  </p>
                  <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors">
                    📤 Descargar archivo JSON
                  </button>
                </div>

                <div className="p-4 border-2 border-red-200 bg-red-50 rounded-lg">
                  <h3 className="flex items-center gap-2 font-medium text-red-900 mb-2">
                    <Trash2 className="w-5 h-5" />
                    Solicitar eliminación de cuenta
                  </h3>
                  <p className="text-sm text-red-800 mb-3">
                    Esta acción es irreversible y eliminará todos tus datos permanentemente.
                  </p>
                  <button className="px-4 py-2 border-2 border-red-600 text-red-600 rounded-lg hover:bg-red-600 hover:text-white font-medium transition-colors">
                    🗑️ Eliminar mi cuenta
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Control Administrativo */}
          {activeSection === 'admin' && settings.isAdmin && (
            <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-1">Control Administrativo</h2>
                <p className="text-sm text-gray-600">Opciones avanzadas para administradores</p>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="flex items-center gap-2 font-medium text-gray-800 mb-3">
                    <Building2 className="w-5 h-5" />
                    Gestión del Centro
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <button className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left">
                      <Users className="w-5 h-5 text-indigo-600 mb-1" />
                      <p className="font-medium">Gestionar grupos</p>
                    </button>
                    <button className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left">
                      <BookOpen className="w-5 h-5 text-indigo-600 mb-1" />
                      <p className="font-medium">Gestionar asignaturas</p>
                    </button>
                    <button className="p-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left">
                      <GraduationCap className="w-5 h-5 text-indigo-600 mb-1" />
                      <p className="font-medium">Gestionar docentes</p>
                    </button>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h3 className="flex items-center gap-2 font-medium text-gray-800 mb-3">
                    <Database className="w-5 h-5" />
                    Base de datos
                  </h3>
                  <div className="space-y-2">
                    <button className="w-full p-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left flex items-center justify-between">
                      <span>Limpiar datos del año anterior</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                    <button className="w-full p-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left flex items-center justify-between">
                      <span>Archivar año académico</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                    <button className="w-full p-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left flex items-center justify-between">
                      <span>Sincronización manual</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Botón de guardar flotante */}
          <div className="sticky bottom-0 left-0 right-0 mt-6 p-4 bg-white border-t border-gray-200 rounded-lg shadow-lg">
            <button
              onClick={handleSave}
              className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors flex items-center justify-center gap-2"
            >
              {saveStatus === 'success' ? (
                <>
                  <Check className="w-5 h-5" />
                  Guardado correctamente
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Guardar cambios
                </>
              )}
            </button>
            {saveStatus === 'error' && (
              <p className="text-red-600 text-sm text-center mt-2">
                Error al guardar. Inténtalo de nuevo.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Ajustes;
