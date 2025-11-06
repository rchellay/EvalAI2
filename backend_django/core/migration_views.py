"""
Endpoint para ejecutar migraciones remotamente (solo superuser)
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.management import call_command
import io
import sys


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_migrations_view(request):
    """
    Ejecuta migraciones pendientes en producción
    POST /api/admin/run-migrations/
    
    Requiere: Usuario autenticado como superuser
    """
    # Verificar que sea superuser
    if not request.user.is_superuser:
        return Response(
            {'error': 'Solo superusers pueden ejecutar migraciones'},
            status=status.HTTP_403_FORBIDDEN
        )
    
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
        
        return Response({
            'status': 'success',
            'message': 'Migraciones ejecutadas exitosamente',
            'output': result
        })
        
    except Exception as e:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        return Response({
            'status': 'error',
            'message': f'Error ejecutando migraciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_migrations_view(request):
    """
    Verifica si hay migraciones pendientes
    GET /api/admin/check-migrations/
    """
    # Verificar que sea superuser
    if not request.user.is_superuser:
        return Response(
            {'error': 'Solo superusers pueden verificar migraciones'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        output = io.StringIO()
        sys.stdout = output
        
        call_command('showmigrations', '--plan', stdout=output)
        
        sys.stdout = sys.__stdout__
        result = output.getvalue()
        
        # Detectar migraciones pendientes
        pending = '[ ]' in result
        
        return Response({
            'status': 'success',
            'pending_migrations': pending,
            'output': result
        })
        
    except Exception as e:
        sys.stdout = sys.__stdout__
        
        return Response({
            'status': 'error',
            'message': f'Error verificando migraciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
