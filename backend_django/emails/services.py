"""
Servicios de envío de emails para EvalAI
Gestiona el envío de correos con plantillas HTML y texto plano
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

logger = logging.getLogger(__name__)


def send_welcome_email(user):
    """
    Envía email de bienvenida a un nuevo usuario
    
    Args:
        user: Instancia del modelo User
        
    Returns:
        bool: True si el email se envió exitosamente, False en caso contrario
    """
    try:
        # Contexto para las plantillas
        context = {
            'username': user.get_full_name() or user.username,
            'app_version': settings.APP_VERSION,
        }
        
        # Renderizar plantillas
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = render_to_string('emails/welcome_email.txt', context)
        
        # Crear email
        subject = '¡Bienvenido a EvalAI!'
        from_email = f'{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>'
        to_email = user.email
        
        # Crear mensaje con versión HTML y texto plano
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Enviar
        msg.send()
        
        logger.info(f"✅ Email de bienvenida enviado a {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de bienvenida a {user.email}: {str(e)}", exc_info=True)
        return False


def send_password_setup_email(user, reset_link=None):
    """
    Envía email con enlace para establecer/resetear contraseña
    
    Args:
        user: Instancia del modelo User
        reset_link: URL completa para resetear contraseña (opcional)
        
    Returns:
        bool: True si el email se envió exitosamente, False en caso contrario
    """
    try:
        # Generar token y link si no se proporciona
        if not reset_link:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Contexto para las plantillas
        context = {
            'username': user.get_full_name() or user.username,
            'reset_link': reset_link,
            'app_version': settings.APP_VERSION,
        }
        
        # Renderizar plantillas
        html_content = render_to_string('emails/reset_password.html', context)
        text_content = render_to_string('emails/reset_password.txt', context)
        
        # Crear email
        subject = 'Configura tu contraseña en EvalAI'
        from_email = f'{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>'
        to_email = user.email
        
        # Crear mensaje con versión HTML y texto plano
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Enviar
        msg.send()
        
        logger.info(f"✅ Email de configuración de contraseña enviado a {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de contraseña a {user.email}: {str(e)}", exc_info=True)
        return False


def send_custom_email(to_email, subject, html_template, text_template, context):
    """
    Función genérica para enviar emails personalizados
    
    Args:
        to_email: Email del destinatario
        subject: Asunto del correo
        html_template: Ruta de la plantilla HTML
        text_template: Ruta de la plantilla de texto
        context: Diccionario con variables para las plantillas
        
    Returns:
        bool: True si el email se envió exitosamente, False en caso contrario
    """
    try:
        # Añadir versión de la app al contexto
        context['app_version'] = settings.APP_VERSION
        
        # Renderizar plantillas
        html_content = render_to_string(html_template, context)
        text_content = render_to_string(text_template, context)
        
        # Crear email
        from_email = f'{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>'
        
        # Crear mensaje con versión HTML y texto plano
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Enviar
        msg.send()
        
        logger.info(f"✅ Email personalizado '{subject}' enviado a {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email a {to_email}: {str(e)}", exc_info=True)
        return False
