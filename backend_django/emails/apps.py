"""
Configuración de la app emails
"""
from django.apps import AppConfig


class EmailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emails'
    verbose_name = 'Sistema de Emails'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import emails.signals  # noqa
