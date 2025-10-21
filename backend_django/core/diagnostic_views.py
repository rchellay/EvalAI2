from django.http import JsonResponse
from django.contrib.auth.models import User
from core.models import Group, Student, Subject, Attendance
from django.db import connection
import os

def diagnosticar_deployment(request):
    """
    Endpoint para diagnosticar problemas específicos del deployment
    """
    try:
        diagnostico = {
            'status': 'success',
            'configuracion': {
                'debug': os.environ.get('DEBUG', 'No definido'),
                'secret_key': '✅ Definido' if os.environ.get('SECRET_KEY') else '❌ No definido',
                'database_url': '✅ Definido' if os.environ.get('DATABASE_URL') else '❌ No definido',
                'allowed_hosts': os.environ.get('ALLOWED_HOSTS', 'No definido'),
            },
            'base_datos': {},
            'modelos': {},
            'admin': {},
            'pruebas': {}
        }
        
        # Verificar conexión a la base de datos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                diagnostico['base_datos']['conexion'] = '✅ Conectado'
        except Exception as e:
            diagnostico['base_datos']['conexion'] = f'❌ Error: {str(e)}'
        
        # Verificar usuarios
        try:
            users_count = User.objects.count()
            superusers_count = User.objects.filter(is_superuser=True).count()
            diagnostico['modelos']['usuarios'] = f'✅ {users_count} usuarios, {superusers_count} superusers'
        except Exception as e:
            diagnostico['modelos']['usuarios'] = f'❌ Error: {str(e)}'
        
        # Verificar modelos
        try:
            estudiantes = Student.objects.count()
            asignaturas = Subject.objects.count()
            grupos = Group.objects.count()
            asistencias = Attendance.objects.count()
            
            diagnostico['modelos']['estudiantes'] = f'✅ {estudiantes}'
            diagnostico['modelos']['asignaturas'] = f'✅ {asignaturas}'
            diagnostico['modelos']['grupos'] = f'✅ {grupos}'
            diagnostico['modelos']['asistencias'] = f'✅ {asistencias}'
        except Exception as e:
            diagnostico['modelos']['error'] = f'❌ Error: {str(e)}'
        
        # Verificar admin
        try:
            from django.contrib import admin
            from core.admin import GroupAdmin, AttendanceAdmin
            
            diagnostico['admin']['group_admin'] = '✅ Registrado' if admin.site.is_registered(Group) else '❌ No registrado'
            diagnostico['admin']['attendance_admin'] = '✅ Registrado' if admin.site.is_registered(Attendance) else '❌ No registrado'
        except Exception as e:
            diagnostico['admin']['error'] = f'❌ Error: {str(e)}'
        
        # Prueba de creación
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                # Crear grupo de prueba
                test_group = Group.objects.create(
                    name="GRUPO_TEST_DEPLOYMENT_API",
                    teacher=superuser
                )
                
                diagnostico['pruebas']['grupo_creado'] = f'✅ ID {test_group.id}'
                
                # Limpiar
                test_group.delete()
                diagnostico['pruebas']['grupo_eliminado'] = '✅ Limpiado'
            else:
                diagnostico['pruebas']['error'] = '❌ No hay superusers'
        except Exception as e:
            diagnostico['pruebas']['error'] = f'❌ Error: {str(e)}'
        
        return JsonResponse(diagnostico)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
