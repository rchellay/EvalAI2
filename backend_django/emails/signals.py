"""
Signals para envío automático de emails
Se disparan cuando ocurren eventos específicos en el sistema
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

from .services import send_welcome_email, send_password_setup_email

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de crear un nuevo usuario
    Envía emails de bienvenida y configuración de contraseña
    
    Args:
        sender: Modelo que envía la señal (User)
        instance: Instancia del usuario creado
        created: True si el usuario es nuevo, False si se actualizó
        **kwargs: Argumentos adicionales
    """
    # Solo actuar si es un usuario nuevo
    if not created:
        return
    
    # Verificar que el usuario tenga email
    if not instance.email:
        logger.warning(f"⚠️ Usuario {instance.username} creado sin email, no se enviarán correos")
        return
    
    logger.info(f"📧 Nuevo usuario creado: {instance.username} ({instance.email})")
    
    try:
        # 1. Enviar email de bienvenida
        welcome_sent = send_welcome_email(instance)
        if welcome_sent:
            logger.info(f"✅ Email de bienvenida enviado a {instance.email}")
        else:
            logger.error(f"❌ Fallo al enviar email de bienvenida a {instance.email}")
        
        # 2. Enviar email para configurar contraseña
        # Solo si el usuario no tiene contraseña establecida (no usable)
        if not instance.has_usable_password():
            password_sent = send_password_setup_email(instance)
            if password_sent:
                logger.info(f"✅ Email de configuración de contraseña enviado a {instance.email}")
            else:
                logger.error(f"❌ Fallo al enviar email de contraseña a {instance.email}")
        else:
            logger.info(f"ℹ️ Usuario {instance.email} ya tiene contraseña, no se envía email de configuración")
            
    except Exception as e:
        logger.error(f"❌ Error en signal de creación de usuario para {instance.email}: {str(e)}", exc_info=True)


# Signal opcional: detectar cuando un usuario solicita reset de contraseña
# Este signal puede conectarse al sistema de reset de contraseña de Django/DRF
# Para uso futuro si se implementa endpoint personalizado de reset

def send_password_reset_email(user):
    """
    Función auxiliar para enviar email de reset de contraseña
    Puede ser llamada desde views o endpoints personalizados
    
    Args:
        user: Instancia del modelo User
    """
    try:
        success = send_password_setup_email(user)
        if success:
            logger.info(f"✅ Email de reset de contraseña enviado a {user.email}")
        return success
    except Exception as e:
        logger.error(f"❌ Error enviando email de reset a {user.email}: {str(e)}", exc_info=True)
        return False
