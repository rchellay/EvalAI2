"""
Middleware personalizado para manejar errores 500 en Django Admin
"""

import traceback
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AdminErrorHandlerMiddleware:
    """Middleware para manejar errores 500 específicamente en Django Admin"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Procesar excepciones específicamente en rutas de admin"""
        
        # Solo manejar errores en rutas de admin
        if not request.path.startswith('/admin/'):
            return None
        
        # Log del error
        logger.error(f"Error 500 en admin: {request.path}")
        logger.error(f"Excepción: {str(exception)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Si es una petición AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Error interno del servidor',
                'message': 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo.',
                'details': str(exception) if settings.DEBUG else None
            }, status=500)
        
        # Para peticiones normales, redirigir con mensaje de error
        try:
            messages.error(request, f'Error interno del servidor: {str(exception)}')
            # Redirigir a la página anterior o al índice del admin
            if request.META.get('HTTP_REFERER'):
                return redirect(request.META['HTTP_REFERER'])
            else:
                return redirect('/admin/')
        except:
            # Si incluso la redirección falla, devolver una respuesta básica
            return HttpResponse(
                f"<h1>Error interno del servidor</h1><p>Ha ocurrido un error inesperado.</p><p><a href='/admin/'>Volver al admin</a></p>",
                status=500
            )
