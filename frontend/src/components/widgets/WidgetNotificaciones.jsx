import React, { useState, useEffect } from 'react';
import axios from 'axios';

const WidgetNotificaciones = ({ teacherId, titleClassName }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
  }, []);

  const loadNotifications = async () => {
    try {
      // TODO: Implementar endpoint /api/notifications/ en el backend
      // const response = await axios.get('/api/notifications/');
      // setNotifications(response.data);
      setNotifications([]); // Temporal: sin notificaciones hasta implementar endpoint
    } catch (error) {
      console.error('Error cargando notificaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      // TODO: Implementar endpoint /api/notifications/unread_count/ en el backend
      // const response = await axios.get('/api/notifications/unread_count/');
      // setUnreadCount(response.data.unread_count);
      setUnreadCount(0); // Temporal: 0 notificaciones hasta implementar endpoint
    } catch (error) {
      console.error('Error cargando conteo de no leídas:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await axios.post(`/api/notifications/${notificationId}/mark_as_read/`);
      // Actualizar estado local
      setNotifications(notifications.map(notif =>
        notif.id === notificationId ? { ...notif, is_read: true } : notif
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marcando como leída:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await axios.post('/api/notifications/mark_all_as_read/');
      setNotifications(notifications.map(notif => ({ ...notif, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marcando todas como leídas:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'objective_reminder':
        return '⏰';
      case 'evaluation_alert':
        return '📝';
      case 'achievement':
        return '🏆';
      case 'system_alert':
      default:
        return '🔔';
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'objective_reminder':
        return 'border-orange-200 bg-orange-50';
      case 'evaluation_alert':
        return 'border-blue-200 bg-blue-50';
      case 'achievement':
        return 'border-green-200 bg-green-50';
      case 'system_alert':
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold mb-4 flex items-center"}>
          <span className="mr-2">🔔</span>
          Notificaciones
        </h3>
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  const safeNotifications = Array.isArray(notifications) ? notifications : [];

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex items-center justify-between mb-4">
        <h3 className={titleClassName ? `${titleClassName} flex items-center` : "text-lg font-semibold flex items-center"}>
          <span className="mr-2">🔔</span>
          Notificaciones
          {unreadCount > 0 && (
            <span className="ml-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
              {unreadCount}
            </span>
          )}
        </h3>
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Marcar todas como leídas
          </button>
        )}
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {safeNotifications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <span className="text-4xl mb-2 block">📭</span>
            No tienes notificaciones
          </div>
        ) : (
          safeNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`p-4 rounded-lg border-l-4 ${
                notification.is_read
                  ? 'border-gray-300 bg-gray-50'
                  : `border-l-4 ${getNotificationColor(notification.notification_type)}`
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <span className="text-lg mr-2">
                      {getNotificationIcon(notification.notification_type)}
                    </span>
                    <h4 className={`font-medium ${!notification.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                      {notification.title}
                    </h4>
                    {!notification.is_read && (
                      <span className="ml-2 w-2 h-2 bg-blue-500 rounded-full"></span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {notification.message}
                  </p>
                  {notification.related_student && (
                    <p className="text-xs text-gray-500">
                      Estudiante: {notification.related_student.name}
                    </p>
                  )}
                  <p className="text-xs text-gray-400">
                    {new Date(notification.created_at).toLocaleDateString('es-ES', {
                      day: 'numeric',
                      month: 'short',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
                {!notification.is_read && (
                  <button
                    onClick={() => markAsRead(notification.id)}
                    className="text-xs text-blue-600 hover:text-blue-800 ml-2"
                  >
                    ✓ Marcar como leída
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        💡 Las notificaciones incluyen recordatorios de objetivos y alertas importantes.
      </div>
    </div>
  );
};

export default WidgetNotificaciones;