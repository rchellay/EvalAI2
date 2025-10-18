"""
Comando Django para enviar notificaciones programadas.
Ejecutar periódicamente con: python manage.py send_notifications
"""
from django.core.management.base import BaseCommand
from core.services.notification_service import NotificationService


class Command(BaseCommand):
    help = 'Enviar notificaciones programadas y crear recordatorios automáticos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin enviar notificaciones reales',
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando envío de notificaciones...')

        try:
            # Crear recordatorios automáticos para objetivos próximos a vencer
            reminders_created = NotificationService.create_bulk_objective_reminders()
            self.stdout.write(
                self.style.SUCCESS(f'Creados {reminders_created} recordatorios de objetivos')
            )

            # Enviar notificaciones programadas
            if not options['dry_run']:
                sent_count = NotificationService.send_scheduled_notifications()
                self.stdout.write(
                    self.style.SUCCESS(f'Enviadas {sent_count} notificaciones programadas')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Modo dry-run: no se enviaron notificaciones')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error procesando notificaciones: {str(e)}')
            )
            return

        self.stdout.write(self.style.SUCCESS('Proceso de notificaciones completado'))