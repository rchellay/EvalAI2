import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, School, Calendar, Palette, Bell, Mail, Clock, Shield, 
  Lock, Key, Download, Trash2, Database, Users, BookOpen, 
  CheckCircle, Sun, Moon, Monitor, Settings as SettingsIcon,
  ChevronRight, Save, AlertTriangle, Info
} from 'lucide-react';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';

const SettingsPageNew = () => {
  const [settings, setSettings] = useState({
    // Perfil
    display_name: '',
    email: '',
    centro_educativo: '',
    
    // Centro y Año Académico
    año_academico: '2024-2025',
    nivel_educativo: '',
    asignaturas_habituales: [],
    
    // Interfaz
    theme: 'light',
    font_size: 'medium',
    compact_mode: false,
    
    // Notificaciones
    notifications_app: true,
    notifications_evaluaciones: true,
    notifications_informes: true,
    notifications_asistencia: true,
    notifications_grupos: true,
    notifications_email: false,
    reminder_time: '1-day',
    
    // Seguridad
    auto_logout_time: '30-min',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeSection, setActiveSection] = useState('perfil');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  useEffect(() => {
    loadSettings();
    checkAdminStatus();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await api.get('/settings/');
      setSettings(prev => ({ ...prev, ...response.data }));
    } catch (error) {
      console.error('Error cargando configuración:', error);
      toast.error('Error al cargar la configuración');
    } finally {
      setLoading(false);
    }
  };

  const checkAdminStatus = async () => {
    try {
      const response = await api.get('/auth/me/');
      setIsAdmin(response.data.is_staff || response.data.is_superuser);
    } catch (error) {
      console.error('Error verificando admin:', error);
    }
  };

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      await api.patch('/settings/', settings);
      toast.success('✅ Configuración guardada correctamente');
    } catch (error) {
      console.error('Error guardando configuración:', error);
      toast.error('Error al guardar la configuración');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('Las contraseñas no coinciden');
      return;
    }
    
    if (passwordData.new_password.length < 8) {
      toast.error('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    try {
      await api.post('/settings/change-password/', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      
      toast.success('✅ Contraseña actualizada correctamente');
      setShowPasswordModal(false);
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al cambiar la contraseña');
    }
  };

  const sendTestNotification = async () => {
    try {
      await api.post('/settings/test-notification/');
      toast.success('🔔 Notificación de prueba enviada');
    } catch (error) {
      toast.error('Error al enviar notificación de prueba');
    }
  };

  const exportData = async () => {
    try {
      const response = await api.get('/settings/export-data/', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `evalai-data-${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('📤 Datos exportados correctamente');
    } catch (error) {
      toast.error('Error al exportar datos');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const sections = [
    { id: 'perfil', name: 'Perfil y Cuenta', icon: User },
    { id: 'centro', name: 'Centro y Año Académico', icon: School },
    { id: 'interfaz', name: 'Interfaz y Personalización', icon: Palette },
    { id: 'notificaciones', name: 'Notificaciones', icon: Bell },
    { id: 'datos', name: 'Datos y Privacidad', icon: Shield },
    ...(isAdmin ? [{ id: 'admin', name: 'Control Administrativo', icon: Key }] : [])
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-2xl p-8 mb-8 text-white"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-4 bg-white/20 rounded-xl">
                <SettingsIcon className="w-10 h-10" />
              </div>
              <div>
                <h1 className="text-4xl font-bold mb-2">⚙️ Ajustes</h1>
                <p className="text-blue-100 text-lg">
                  Personaliza cómo funciona tu entorno de trabajo educativo
                </p>
              </div>
            </div>
            <button
              onClick={saveSettings}
              disabled={saving}
              className="px-6 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition-all flex items-center gap-2 shadow-lg disabled:opacity-50"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <div className="bg-white rounded-2xl shadow-xl p-4 sticky top-6">
              <nav className="space-y-2">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${
                        activeSection === section.id
                          ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="w-5 h-5" />
                        <span className="font-medium text-sm">{section.name}</span>
                      </div>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  );
                })}
              </nav>
            </div>
          </motion.div>

          {/* Content Area */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-3"
          >
            <div className="bg-white rounded-2xl shadow-xl p-8">
              
              {/* SECCIÓN 1: PERFIL Y CUENTA */}
              {activeSection === 'perfil' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <User className="w-6 h-6 text-blue-600" />
                      Perfil y Cuenta
                    </h2>
                    <p className="text-gray-600">Gestiona tu información personal y preferencias de cuenta</p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        👤 Nombre mostrado
                      </label>
                      <input
                        type="text"
                        value={settings.display_name}
                        onChange={(e) => handleChange('display_name', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Nombre que aparecerá en la aplicación"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        📧 Correo electrónico
                      </label>
                      <input
                        type="email"
                        value={settings.email}
                        onChange={(e) => handleChange('email', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="tu@email.com"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        🏫 Centro educativo asignado
                      </label>
                      <input
                        type="text"
                        value={settings.centro_educativo}
                        onChange={(e) => handleChange('centro_educativo', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Nombre del centro"
                      />
                    </div>

                    <div className="pt-4 border-t">
                      <button
                        onClick={() => setShowPasswordModal(true)}
                        className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all flex items-center gap-2"
                      >
                        <Lock className="w-5 h-5" />
                        🔐 Cambiar contraseña
                      </button>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        🚪 Cerrar sesión automáticamente tras:
                      </label>
                      <select
                        value={settings.auto_logout_time}
                        onChange={(e) => handleChange('auto_logout_time', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="10-min">10 minutos</option>
                        <option value="20-min">20 minutos</option>
                        <option value="30-min">30 minutos</option>
                        <option value="1-hour">1 hora</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* SECCIÓN 2: CENTRO Y AÑO ACADÉMICO */}
              {activeSection === 'centro' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <School className="w-6 h-6 text-blue-600" />
                      Centro y Año Académico
                    </h2>
                    <p className="text-gray-600">Configura el año académico y tu centro educativo</p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        📘 Año académico activo
                      </label>
                      <select
                        value={settings.año_academico}
                        onChange={(e) => handleChange('año_academico', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="2024-2025">2024–2025</option>
                        <option value="2025-2026">2025–2026</option>
                        <option value="2026-2027">2026–2027</option>
                      </select>
                      <p className="text-xs text-gray-500 mt-2">
                        💡 Crear nuevo año académico → (clonar grupos, asignaturas, configuraciones)
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        👥 Nivel educativo en el que trabajas
                      </label>
                      <select
                        value={settings.nivel_educativo}
                        onChange={(e) => handleChange('nivel_educativo', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Selecciona un nivel</option>
                        <option value="infantil">Educación Infantil</option>
                        <option value="primaria">Primaria</option>
                        <option value="secundaria">Secundaria</option>
                        <option value="bachillerato">Bachillerato</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        📚 Asignaturas habituales
                      </label>
                      <div className="p-4 bg-blue-50 rounded-xl border border-blue-200">
                        <p className="text-sm text-blue-800">
                          <Info className="w-4 h-4 inline mr-2" />
                          Las sugerencias de IA se basarán en tus asignaturas más utilizadas
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* SECCIÓN 3: INTERFAZ Y PERSONALIZACIÓN */}
              {activeSection === 'interfaz' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <Palette className="w-6 h-6 text-blue-600" />
                      Interfaz y Personalización
                    </h2>
                    <p className="text-gray-600">Ajusta la apariencia de la aplicación</p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        🌗 Tema visual
                      </label>
                      <div className="grid grid-cols-3 gap-3">
                        <button
                          onClick={() => handleChange('theme', 'light')}
                          className={`p-4 rounded-xl border-2 transition-all ${
                            settings.theme === 'light'
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-blue-300'
                          }`}
                        >
                          <Sun className="w-6 h-6 mx-auto mb-2 text-yellow-500" />
                          <p className="text-sm font-medium">Claro</p>
                        </button>
                        <button
                          onClick={() => handleChange('theme', 'dark')}
                          className={`p-4 rounded-xl border-2 transition-all ${
                            settings.theme === 'dark'
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-blue-300'
                          }`}
                        >
                          <Moon className="w-6 h-6 mx-auto mb-2 text-indigo-500" />
                          <p className="text-sm font-medium">Oscuro</p>
                        </button>
                        <button
                          onClick={() => handleChange('theme', 'auto')}
                          className={`p-4 rounded-xl border-2 transition-all ${
                            settings.theme === 'auto'
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-blue-300'
                          }`}
                        >
                          <Monitor className="w-6 h-6 mx-auto mb-2 text-gray-500" />
                          <p className="text-sm font-medium">Automático</p>
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        🔠 Tamaño de fuente (accesibilidad)
                      </label>
                      <div className="grid grid-cols-3 gap-3">
                        {['small', 'medium', 'large'].map((size) => (
                          <button
                            key={size}
                            onClick={() => handleChange('font_size', size)}
                            className={`p-4 rounded-xl border-2 transition-all ${
                              settings.font_size === size
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 hover:border-blue-300'
                            }`}
                          >
                            <p className={`font-medium ${
                              size === 'small' ? 'text-sm' : 
                              size === 'medium' ? 'text-base' : 'text-lg'
                            }`}>
                              {size === 'small' ? 'Pequeño' : 
                               size === 'medium' ? 'Medio' : 'Grande'}
                            </p>
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-semibold text-gray-900">📲 Modo compacto</p>
                        <p className="text-sm text-gray-600">Ideal para tablets y portátiles</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.compact_mode}
                          onChange={(e) => handleChange('compact_mode', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* SECCIÓN 4: NOTIFICACIONES */}
              {activeSection === 'notificaciones' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <Bell className="w-6 h-6 text-blue-600" />
                      Notificaciones
                    </h2>
                    <p className="text-gray-600">Controla cómo y cuándo recibir notificaciones</p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">🔔 Notificaciones en la app</h3>
                      <div className="space-y-3">
                        {[
                          { key: 'notifications_evaluaciones', label: 'Evaluaciones pendientes' },
                          { key: 'notifications_informes', label: 'Informes generados' },
                          { key: 'notifications_asistencia', label: 'Recordatorios de asistencia' },
                          { key: 'notifications_grupos', label: 'Cambios en grupos' }
                        ].map((notif) => (
                          <div key={notif.key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">{notif.label}</span>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={settings[notif.key]}
                                onChange={(e) => handleChange(notif.key, e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">📧 Notificaciones por correo electrónico</h3>
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <span className="text-gray-700">Activar notificaciones por email</span>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.notifications_email}
                            onChange={(e) => handleChange('notifications_email', e.target.checked)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        ⏰ Recordatorios previos a sesiones o evaluaciones
                      </label>
                      <select
                        value={settings.reminder_time}
                        onChange={(e) => handleChange('reminder_time', e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="5-min">5 minutos</option>
                        <option value="15-min">15 minutos</option>
                        <option value="1-hour">1 hora</option>
                        <option value="1-day">1 día</option>
                      </select>
                    </div>

                    <div className="pt-4">
                      <button
                        onClick={sendTestNotification}
                        className="px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-all flex items-center gap-2"
                      >
                        <Send className="w-5 h-5" />
                        📩 Enviar notificación de prueba
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* SECCIÓN 5: DATOS Y PRIVACIDAD */}
              {activeSection === 'datos' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <Shield className="w-6 h-6 text-blue-600" />
                      Datos y Privacidad
                    </h2>
                    <p className="text-gray-600">Gestiona tus datos personales y privacidad</p>
                  </div>

                  <div className="space-y-4">
                    <div className="p-6 bg-blue-50 rounded-xl border border-blue-200">
                      <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                        <Info className="w-5 h-5" />
                        🔐 Tratamiento de datos personales
                      </h3>
                      <p className="text-sm text-blue-800 mb-3">
                        Tus datos son tratados de forma segura y confidencial según la GDPR y LOPDGDD.
                      </p>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-all">
                        Ver política de privacidad
                      </button>
                    </div>

                    <div className="p-6 bg-green-50 rounded-xl border border-green-200">
                      <h3 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
                        <Download className="w-5 h-5" />
                        💾 Exportar mis datos
                      </h3>
                      <p className="text-sm text-green-800 mb-3">
                        Descarga una copia completa de tus datos en formato JSON
                      </p>
                      <button
                        onClick={exportData}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-all flex items-center gap-2"
                      >
                        <Download className="w-4 h-4" />
                        📤 Descargar datos
                      </button>
                    </div>

                    <div className="p-6 bg-red-50 rounded-xl border border-red-200">
                      <h3 className="font-semibold text-red-900 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5" />
                        🗑️ Solicitar eliminación de cuenta
                      </h3>
                      <p className="text-sm text-red-800 mb-3">
                        Esta acción es irreversible y eliminará todos tus datos permanentemente
                      </p>
                      <button className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-all flex items-center gap-2">
                        <Trash2 className="w-4 h-4" />
                        Solicitar eliminación
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* SECCIÓN 6: CONTROL ADMINISTRATIVO (solo admin) */}
              {activeSection === 'admin' && isAdmin && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <Key className="w-6 h-6 text-blue-600" />
                      Control Administrativo
                    </h2>
                    <p className="text-gray-600">Herramientas de gestión para administradores</p>
                  </div>

                  <div className="space-y-4">
                    <div className="p-6 bg-purple-50 rounded-xl border border-purple-200">
                      <h3 className="font-semibold text-purple-900 mb-3">🗂️ Gestión del Centro</h3>
                      <div className="space-y-2">
                        <button className="w-full px-4 py-2 bg-white border border-purple-300 rounded-lg text-sm font-medium hover:bg-purple-50 transition-all text-left flex items-center justify-between">
                          <span>📚 Gestionar grupos</span>
                          <ChevronRight className="w-4 h-4" />
                        </button>
                        <button className="w-full px-4 py-2 bg-white border border-purple-300 rounded-lg text-sm font-medium hover:bg-purple-50 transition-all text-left flex items-center justify-between">
                          <span>📖 Gestionar asignaturas</span>
                          <ChevronRight className="w-4 h-4" />
                        </button>
                        <button className="w-full px-4 py-2 bg-white border border-purple-300 rounded-lg text-sm font-medium hover:bg-purple-50 transition-all text-left flex items-center justify-between">
                          <span>👥 Gestionar docentes</span>
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="p-6 bg-yellow-50 rounded-xl border border-yellow-200">
                      <h3 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
                        <Database className="w-5 h-5" />
                        🧮 Base de datos
                      </h3>
                      <div className="space-y-2">
                        <button className="w-full px-4 py-2 bg-white border border-yellow-300 rounded-lg text-sm font-medium hover:bg-yellow-50 transition-all text-left">
                          Limpiar datos del año anterior
                        </button>
                        <button className="w-full px-4 py-2 bg-white border border-yellow-300 rounded-lg text-sm font-medium hover:bg-yellow-50 transition-all text-left">
                          Archivar año académico
                        </button>
                        <button className="w-full px-4 py-2 bg-white border border-yellow-300 rounded-lg text-sm font-medium hover:bg-yellow-50 transition-all text-left">
                          Sincronización manual
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </motion.div>
        </div>
      </div>

      {/* Modal de Cambiar Contraseña */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full"
          >
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Lock className="w-6 h-6 text-blue-600" />
              Cambiar Contraseña
            </h3>
            
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Contraseña actual
                </label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Nueva contraseña
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Confirmar nueva contraseña
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordModal(false);
                    setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
                  }}
                  className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all"
                >
                  Cambiar
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default SettingsPageNew;
