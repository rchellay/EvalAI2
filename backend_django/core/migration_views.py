"""
Endpoint para ejecutar migraciones remotamente (solo superuser)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.contrib.auth.decorators import user_passes_test
import io
import sys


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def run_migrations_view(request):
    """
    Ejecuta migraciones pendientes en producción
    POST /api/admin/run-migrations/
    
    Requiere: Usuario autenticado como superuser
    """
    try:
        # Capturar output
        output = io.StringIO()
        sys.stdout = output
        sys.stderr = output
        
        # Ejecutar migraciones
        call_command('migrate', '--no-input', stdout=output, stderr=output)
        
        # Restaurar stdout/stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        result = output.getvalue()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Migraciones ejecutadas exitosamente',
            'output': result
        })
        
    except Exception as e:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        return JsonResponse({
            'status': 'error',
            'message': f'Error ejecutando migraciones: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@user_passes_test(is_superuser)
def check_migrations_view(request):
    """
    Verifica si hay migraciones pendientes
    GET /api/admin/check-migrations/
    """
    try:
        output = io.StringIO()
        sys.stdout = output
        
        call_command('showmigrations', '--plan', stdout=output)
        
        sys.stdout = sys.__stdout__
        result = output.getvalue()
        
        # Detectar migraciones pendientes
        pending = '[ ]' in result
        
        return JsonResponse({
            'status': 'success',
            'pending_migrations': pending,
            'output': result
        })
        
    except Exception as e:
        sys.stdout = sys.__stdout__
        
        return JsonResponse({
            'status': 'error',
            'message': f'Error verificando migraciones: {str(e)}'
        }, status=500)
