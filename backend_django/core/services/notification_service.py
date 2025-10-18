"""
Servicio para gestión de notificaciones push.
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Notification, Objective, Student

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para crear y gestionar notificaciones"""

    @staticmethod
    def create_objective_reminder(objective, days_before=1):
        """
        Crear recordatorio para un objetivo próximo a vencer.

        Args:
            objective: Instancia del modelo Objective
            days_before: Días antes del deadline para enviar el recordatorio
        """
        try:
            if not objective.deadline:
                return None

            reminder_date = objective.deadline - timedelta(days=days_before)

            # Solo crear si la fecha de recordatorio es futura
            if reminder_date <= timezone.now().date():
                return None

            notification, created = Notification.objects.get_or_create(
                recipient=objective.created_by,
                related_objective=objective,
                notification_type='objective_reminder',
                scheduled_at=reminder_date,
                defaults={
                    'title': f'Recordatorio: Objetivo próximo a vencer',
                    'message': f'El objetivo "{objective.title}" vence el {objective.deadline.strftime("%d/%m/%Y")}. '
                              f'Revisa el progreso de {objective.student.name}.',
                    'related_student': objective.student,
                }
            )

            if created:
                logger.info(f'Recordatorio creado para objetivo {objective.id}')
                return notification
            return None

        except Exception as e:
            logger.error(f'Error creando recordatorio para objetivo {objective.id}: {str(e)}')
            return None

    @staticmethod
    def create_evaluation_alert(student, subject, message):
        """
        Crear alerta de evaluación para un profesor.

        Args:
            student: Instancia del modelo Student
            subject: Instancia del modelo Subject
            message: Mensaje de la alerta
        """
        try:
            # Encontrar al profesor de la asignatura
            teacher = subject.teacher

            notification = Notification.objects.create(
                recipient=teacher,
                title='Nueva evaluación pendiente',
                message=message,
                notification_type='evaluation_alert',
                related_student=student,
            )

            logger.info(f'Alerta de evaluación creada para profesor {teacher.username}')
            return notification

        except Exception as e:
            logger.error(f'Error creando alerta de evaluación: {str(e)}')
            return None

    @staticmethod
    def create_achievement_notification(student, achievement_title, message):
        """
        Crear notificación de logro desbloqueado.

        Args:
            student: Instancia del modelo Student
            achievement_title: Título del logro
            message: Mensaje descriptivo
        """
        try:
            # Encontrar profesores relacionados con el estudiante
            teachers = User.objects.filter(
                subjects__groups__students=student
            ).distinct()

            notifications = []
            for teacher in teachers:
                notification = Notification.objects.create(
                    recipient=teacher,
                    title=f'🏆 {achievement_title}',
                    message=message,
                    notification_type='achievement',
                    related_student=student,
                )
                notifications.append(notification)

            logger.info(f'Notificaciones de logro creadas para {len(notifications)} profesores')
            return notifications

        except Exception as e:
            logger.error(f'Error creando notificación de logro: {str(e)}')
            return []

    @staticmethod
    def send_scheduled_notifications():
        """
        Enviar notificaciones programadas que ya vencieron.
        Esta función debería ejecutarse periódicamente (ej: con Celery o cron).
        """
        try:
            now = timezone.now()

            # Encontrar notificaciones programadas que ya vencieron y no han sido enviadas
            scheduled_notifications = Notification.objects.filter(
                scheduled_at__lte=now.date(),
                sent_at__isnull=True
            )

            sent_count = 0
            for notification in scheduled_notifications:
                # Aquí iría la lógica real de envío (email, push notification, etc.)
                # Por ahora solo marcamos como enviadas
                notification.mark_as_sent()
                sent_count += 1

            if sent_count > 0:
                logger.info(f'Enviadas {sent_count} notificaciones programadas')

            return sent_count

        except Exception as e:
            logger.error(f'Error enviando notificaciones programadas: {str(e)}')
            return 0

    @staticmethod
    def create_bulk_objective_reminders():
        """
        Crear recordatorios para todos los objetivos próximos a vencer.
        """
        try:
            # Objetivos que vencen en los próximos 7 días
            upcoming_deadlines = timezone.now().date() + timedelta(days=7)

            objectives = Objective.objects.filter(
                deadline__lte=upcoming_deadlines,
                deadline__gte=timezone.now().date(),
                status__in=['pending', 'in_progress']
            )

            created_count = 0
            for objective in objectives:
                if NotificationService.create_objective_reminder(objective):
                    created_count += 1

            logger.info(f'Creados {created_count} recordatorios de objetivos')
            return created_count

        except Exception as e:
            logger.error(f'Error creando recordatorios masivos: {str(e)}')
            return 0

    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=50):
        """
        Obtener notificaciones de un usuario.

        Args:
            user: Instancia del modelo User
            unread_only: Solo notificaciones no leídas
            limit: Límite de resultados
        """
        try:
            queryset = Notification.objects.filter(recipient=user)

            if unread_only:
                queryset = queryset.filter(is_read=False)

            return queryset.select_related(
                'related_student', 'related_objective'
            ).order_by('-created_at')[:limit]

        except Exception as e:
            logger.error(f'Error obteniendo notificaciones para usuario {user.username}: {str(e)}')
            return Notification.objects.none()