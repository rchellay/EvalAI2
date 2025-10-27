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
                
                # Crear tabla core_evaluation directamente
                cursor.execute("""
                    CREATE TABLE core_evaluation (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL,
                        subject_id INTEGER NOT NULL,
                        evaluator_id INTEGER NOT NULL,
                        score DECIMAL(5,2),
                        comment TEXT,
                        rubric_id INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                print("✅ Tabla core_evaluation creada desde endpoint")
                
                # Agregar columna 'course' a core_group si no existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_group' AND column_name = 'course'
                """)
                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE core_group 
                        ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO'
                    """)
                    print("✅ Columna 'course' agregada a core_group")
                
                # Agregar columna 'grupo_principal_id' a core_student si no existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_student' AND column_name = 'grupo_principal_id'
                """)
                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE core_student 
                        ADD COLUMN grupo_principal_id INTEGER
                    """)
                    
                    # Asignar estudiantes existentes al primer grupo disponible
                    cursor.execute("SELECT id FROM core_group LIMIT 1")
                    first_group = cursor.fetchone()
                    if first_group:
                        cursor.execute("""
                            UPDATE core_student 
                            SET grupo_principal_id = %s 
                            WHERE grupo_principal_id IS NULL
                        """, [first_group[0]])
                        cursor.execute("""
                            ALTER TABLE core_student 
                            ALTER COLUMN grupo_principal_id SET NOT NULL
                        """)
                    print("✅ Columna 'grupo_principal_id' agregada a core_student")
                
                # Agregar columna 'apellidos' a core_student si no existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_student' AND column_name = 'apellidos'
                """)
                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE core_student 
                        ADD COLUMN apellidos VARCHAR(200) DEFAULT 'Sin Apellidos'
                    """)
                    print("✅ Columna 'apellidos' agregada a core_student")
                
                # Crear tabla core_student_subgrupos si no existe
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'core_student_subgrupos'
                """)
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE core_student_subgrupos (
                            id SERIAL PRIMARY KEY,
                            student_id INTEGER NOT NULL,
                            group_id INTEGER NOT NULL,
                            UNIQUE(student_id, group_id)
                        )
                    """)
                    print("✅ Tabla core_student_subgrupos creada")
                
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
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_evaluation_student ON core_evaluation(student_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_evaluation_subject ON core_evaluation(subject_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_evaluation_evaluator ON core_evaluation(evaluator_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_evaluation_created ON core_evaluation(created_at);")
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
            'pruebas': {},
            'pruebas_borrado': {}
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

        # CREAR GRUPOS DE EJEMPLO SI NO EXISTEN
        if grupos == 0:
            try:
                # Creemos grupos de ejemplo
                staff_users = User.objects.filter(is_staff=True)
                if staff_users.exists():
                    teacher = staff_users.first()
                    sample_groups = [
                        {'name': '4tA', 'course': '4t ESO'},
                        {'name': '4tB', 'course': '4t ESO'},
                        {'name': '3tA', 'course': '3r ESO'},
                        {'name': '3tB', 'course': '3r ESO'},
                        {'name': '2nA', 'course': '2n ESO'},
                        {'name': '1rA', 'course': '1r ESO'},
                    ]
                    created_count = 0
                    for group_data in sample_groups:
                        group, created = Group.objects.get_or_create(
                            name=group_data['name'],
                            course=group_data['course'],
                            teacher=teacher,
                            defaults={'course': group_data['course']}
                        )
                        if created:
                            created_count += 1
                    diagnostico['modelos']['grupos'] = f'✅ Creados {created_count} grupos de ejemplo, total {Group.objects.count()}'
                else:
                    diagnostico['modelos']['grupos'] = f'⚠️ {grupos}, pero no hay staff users para crear ejemplos'
            except Exception as e:
                diagnostico['modelos']['grupos'] = f'❌ {grupos}, error creando ejemplos: {str(e)}'
        else:
            diagnostico['modelos']['grupos'] = f'✅ {grupos}'

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
        
        # PRUEBAS ESPECÍFICAS DE BORRADO
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                print("🧪 PROBANDO BORRADO DE GRUPOS...")
                
                # Crear grupo para prueba de borrado
                test_group_delete = Group.objects.create(
                    name="GRUPO_TEST_BORRADO",
                    teacher=superuser
                )
                
                diagnostico['pruebas_borrado']['grupo_creado_para_borrar'] = f'✅ ID {test_group_delete.id}'
                
                # Intentar borrar
                try:
                    test_group_delete.delete()
                    diagnostico['pruebas_borrado']['grupo_borrado'] = '✅ Borrado exitoso'
                except Exception as delete_error:
                    diagnostico['pruebas_borrado']['grupo_borrado'] = f'❌ Error al borrar: {str(delete_error)}'
                
                # Probar borrado de Attendance
                print("🧪 PROBANDO BORRADO DE ASISTENCIAS...")
                try:
                    # Crear asistencia para prueba
                    student = Student.objects.first()
                    subject = Subject.objects.first()
                    
                    if student and subject:
                        test_attendance = Attendance.objects.create(
                            student=student,
                            subject=subject,
                            date='2023-01-01',
                            status='presente',
                            recorded_by=superuser
                        )
                        
                        diagnostico['pruebas_borrado']['asistencia_creada_para_borrar'] = f'✅ ID {test_attendance.id}'
                        
                        # Intentar borrar
                        try:
                            test_attendance.delete()
                            diagnostico['pruebas_borrado']['asistencia_borrada'] = '✅ Borrado exitoso'
                        except Exception as delete_error:
                            diagnostico['pruebas_borrado']['asistencia_borrada'] = f'❌ Error al borrar: {str(delete_error)}'
                    else:
                        diagnostico['pruebas_borrado']['asistencia_error'] = '❌ No hay estudiantes o asignaturas para la prueba'
                        
                except Exception as e:
                    diagnostico['pruebas_borrado']['asistencia_error'] = f'❌ Error creando asistencia: {str(e)}'
                    
        except Exception as e:
            diagnostico['pruebas_borrado']['error_general'] = f'❌ Error en pruebas de borrado: {str(e)}'
        
        return JsonResponse(diagnostico)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
