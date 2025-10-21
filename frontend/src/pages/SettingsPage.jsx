import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, School, Calendar, Globe, Sun, Moon, Monitor, 
  Type, Palette, Bell, Mail, Clock, Shield, Lock, 
  Key, AlertTriangle, CheckCircle, Save, Send, Wrench 
} from 'lucide-react';
import api from '../lib/axios';
import { toast } from 'react-hot-toast';

const SettingsPage = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Estados para cambio de contraseña
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await api.get('/settings/');
      setSettings(response.data);
    } catch (error) {
      console.error('Error cargando configuración:', error);
      toast.error('Error al cargar la configuración');
    } finally {
      setLoading(false);
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
      const response = await api.patch('/settings/', settings);
      setSettings(response.data);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">⚙️ Ajustes</h1>
            <p className="text-gray-600 mt-1">Personaliza tu experiencia en EvalAI</p>
          </div>
          <button
            onClick={saveSettings}
            disabled={saving}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition shadow-md disabled:opacity-50"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Guardando...
              </>
            ) : (
              <>
                <Save className="h-5 w-5" />
                Guardar Cambios
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* 1. AJUSTES GENERALES */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <User className="mr-2 h-5 w-5 text-blue-600" />
              Ajustes Generales
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  👤 Nombre mostrado
                </label>
                <input
                  type="text"
                  value={settings?.nombre_mostrado || ''}
                  onChange={(e) => handleChange('nombre_mostrado', e.target.value)}
                  placeholder={settings?.username || 'Tu nombre'}
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  🏫 Centro educativo
                </label>
                <input
                  type="text"
                  value={settings?.centro_educativo || ''}
                  onChange={(e) => handleChange('centro_educativo', e.target.value)}
                  placeholder="Nombre de tu centro"
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  📘 Curso / Periodo académico
                </label>
                <input
                  type="text"
                  value={settings?.curso_periodo || ''}
                  onChange={(e) => handleChange('curso_periodo', e.target.value)}
                  placeholder="2024-2025"
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  🌍 Idioma por defecto
                </label>
                <select
                  value={settings?.idioma || 'es'}
                  onChange={(e) => handleChange('idioma', e.target.value)}
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="es">Español</option>
                  <option value="ca">Català</option>
                  <option value="en">English</option>
                  <option value="fr">Français</option>
                </select>
              </div>
            </div>
          </div>

          {/* 2. INTERFAZ Y PERSONALIZACIÓN */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Palette className="mr-2 h-5 w-5 text-purple-600" />
              Interfaz y Personalización
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🌗 Tema visual
                </label>
                <div className="flex gap-2">
                  {['light', 'dark', 'system'].map(tema => (
                    <button
                      key={tema}
                      onClick={() => handleChange('tema', tema)}
                      className={`flex-1 p-3 rounded-lg border-2 transition ${
                        settings?.tema === tema
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {tema === 'light' && <Sun className="h-5 w-5 mx-auto text-gray-700" />}
                      {tema === 'dark' && <Moon className="h-5 w-5 mx-auto text-gray-700" />}
                      {tema === 'system' && <Monitor className="h-5 w-5 mx-auto text-gray-700" />}
                      <span className="block text-xs mt-1 capitalize text-gray-900">{tema === 'light' ? 'Claro' : tema === 'dark' ? 'Oscuro' : 'Sistema'}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  🔠 Tamaño de fuente
                </label>
                <select
                  value={settings?.tamano_fuente || 'medium'}
                  onChange={(e) => handleChange('tamano_fuente', e.target.value)}
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="small">Pequeña</option>
                  <option value="medium">Media</option>
                  <option value="large">Grande</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  🔍 Escala general UI: {settings?.escala_ui || 100}%
                </label>
                <input
                  type="range"
                  min="50"
                  max="120"
                  value={settings?.escala_ui || 100}
                  onChange={(e) => handleChange('escala_ui', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>50%</span>
                  <span>100%</span>
                  <span>120%</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  🎨 Color principal
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={settings?.color_principal || '#4f46e5'}
                    onChange={(e) => handleChange('color_principal', e.target.value)}
                    className="h-10 w-20 rounded border border-gray-300 cursor-pointer"
                  />
                  <input
                    type="text"
                    value={settings?.color_principal || '#4f46e5'}
                    onChange={(e) => handleChange('color_principal', e.target.value)}
                    className="flex-1 p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* 3. NOTIFICACIONES */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Bell className="mr-2 h-5 w-5 text-yellow-600" />
              Notificaciones y Recordatorios
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Mail className="mr-2 h-5 w-5 text-gray-600" />
                  <span className="text-sm font-medium text-gray-900">Notificaciones por correo</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings?.notif_email || false}
                    onChange={(e) => handleChange('notif_email', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Bell className="mr-2 h-5 w-5 text-gray-600" />
                  <span className="text-sm font-medium text-gray-900">Notificaciones en la app</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings?.notif_in_app || false}
                    onChange={(e) => handleChange('notif_in_app', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ⏰ Tiempo previo de recordatorio
                </label>
                <select
                  value={settings?.recordatorio_minutos || 15}
                  onChange={(e) => handleChange('recordatorio_minutos', parseInt(e.target.value))}
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={5}>5 minutos</option>
                  <option value={15}>15 minutos</option>
                  <option value={30}>30 minutos</option>
                  <option value={60}>1 hora</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  📋 Tipos de notificaciones
                </label>
                
                <label className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings?.notif_evaluaciones_pendientes || false}
                    onChange={(e) => handleChange('notif_evaluaciones_pendientes', e.target.checked)}
                    className="mr-2 h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-900">Evaluaciones pendientes</span>
                </label>

                <label className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings?.notif_informes_listos || false}
                    onChange={(e) => handleChange('notif_informes_listos', e.target.checked)}
                    className="mr-2 h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-900">Informes listos</span>
                </label>

                <label className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings?.notif_asistencias || false}
                    onChange={(e) => handleChange('notif_asistencias', e.target.checked)}
                    className="mr-2 h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-900">Asistencias no marcadas</span>
                </label>
              </div>

              <button
                onClick={sendTestNotification}
                className="w-full mt-3 flex items-center justify-center gap-2 bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition"
              >
                <Send className="h-4 w-4" />
                Enviar notificación de prueba
              </button>
            </div>
          </div>

          {/* 4. SEGURIDAD Y PRIVACIDAD */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Shield className="mr-2 h-5 w-5 text-green-600" />
              Seguridad y Privacidad
            </h2>
            
            <div className="space-y-4">
              <button
                onClick={() => setShowPasswordModal(true)}
                className="w-full flex items-center justify-center gap-2 bg-gray-100 text-gray-900 px-4 py-3 rounded-lg hover:bg-gray-200 transition border border-gray-300"
              >
                <Key className="h-5 w-5" />
                Cambiar contraseña
              </button>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  🧍‍♂️ Cierre automático por inactividad
                </label>
                <select
                  value={settings?.auto_logout_minutos || 30}
                  onChange={(e) => handleChange('auto_logout_minutos', parseInt(e.target.value))}
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={15}>15 minutos</option>
                  <option value={30}>30 minutos</option>
                  <option value={60}>1 hora</option>
                </select>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="flex items-center">
                    <Lock className="mr-2 h-5 w-5 text-gray-600" />
                    <span className="text-sm font-medium text-gray-900">Cifrado de datos sensibles</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 ml-7">Encripta transcripciones y audios</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings?.cifrar_datos || false}
                    onChange={(e) => handleChange('cifrar_datos', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div>
                  <div className="flex items-center">
                    <CheckCircle className="mr-2 h-5 w-5 text-blue-600" />
                    <span className="text-sm font-medium text-blue-900">Consentimiento de uso de IA</span>
                  </div>
                  <p className="text-xs text-blue-700 mt-1 ml-7">
                    Procesamiento local, sin envío externo
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings?.consentimiento_ia || false}
                    onChange={(e) => handleChange('consentimiento_ia', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

        </div>

        {/* Información del usuario */}
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl shadow-md p-6 border border-blue-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">📧 Información de la cuenta</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Usuario:</span>
              <span className="ml-2 font-medium text-gray-900">{settings?.username}</span>
            </div>
            <div>
              <span className="text-gray-600">Email:</span>
              <span className="ml-2 font-medium text-gray-900">{settings?.email}</span>
            </div>
          </div>
        </div>

        {/* Herramientas de administración */}
        <div className="mt-6 bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl shadow-md p-6 border border-orange-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <Wrench className="h-5 w-5 mr-2 text-orange-600" />
            Herramientas de Administración
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Herramientas para limpiar y mantener tus datos en orden
          </p>
          <button
            onClick={() => navigate('/admin/cleanup')}
            className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition shadow-sm"
          >
            <Wrench className="h-4 w-4" />
            Limpiar Datos Duplicados
          </button>
        </div>
      </div>

      {/* Modal de cambio de contraseña */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <Key className="mr-2 h-6 w-6 text-blue-600" />
              Cambiar Contraseña
            </h3>
            
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contraseña actual
                </label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                  required
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nueva contraseña
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                  required
                  minLength={8}
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Mínimo 8 caracteres</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirmar nueva contraseña
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
                  required
                  className="w-full p-2 bg-white text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordModal(false);
                    setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  Actualizar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;

