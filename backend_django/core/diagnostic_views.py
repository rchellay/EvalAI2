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
        # EJECUTAR AUTO-FIX ANTES DEL DIAGNÓSTICO
        print("🔧 EJECUTANDO AUTO-FIX EN EL ENDPOINT...")
        try:
            with connection.cursor() as cursor:
                # Verificar si core_attendance existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'core_attendance'
                    );
                """)
                attendance_exists = cursor.fetchone()[0]
                
                if not attendance_exists:
                    print("🔨 Creando tabla core_attendance desde endpoint...")
                    cursor.execute("""
                        CREATE TABLE core_attendance (
                            id SERIAL PRIMARY KEY,
                            student_id INTEGER NOT NULL,
                            subject_id INTEGER NOT NULL,
                            date DATE NOT NULL,
                            status VARCHAR(10) NOT NULL,
                            comment TEXT,
                            recorded_by_id INTEGER,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    print("✅ Tabla core_attendance creada desde endpoint")
                
                # Verificar si teacher_id existe en core_group
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'core_group' 
                        AND column_name = 'teacher_id'
                    );
                """)
                teacher_id_exists = cursor.fetchone()[0]
                
                if not teacher_id_exists:
                    print("🔨 Agregando columna teacher_id a core_group desde endpoint...")
                    cursor.execute("""
                        ALTER TABLE core_group 
                        ADD COLUMN teacher_id INTEGER;
                    """)
                    print("✅ Columna teacher_id agregada desde endpoint")
                
                # Crear índices
                try:
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_student ON core_attendance(student_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_subject ON core_attendance(subject_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_date ON core_attendance(date);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_group_teacher ON core_group(teacher_id);")
                    print("✅ Índices creados desde endpoint")
                except Exception as e:
                    print(f"⚠️  Error creando índices: {e}")
                    
        except Exception as e:
            print(f"❌ Error en auto-fix desde endpoint: {e}")
        
        diagnostico = {
            'status': 'success',
            'auto_fix_ejecutado': True,
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