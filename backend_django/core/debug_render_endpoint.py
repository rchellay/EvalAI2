from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.contrib.auth import get_user_model

@csrf_exempt
@staff_member_required
def debug_render_500(request):
    """Endpoint para diagnosticar errores 500 específicamente en Render"""
    
    try:
        results = {
            "status": "success",
            "configuracion": {},
            "base_datos": {},
            "estructura_tablas": {},
            "datos_criticos": {},
            "operaciones_crud": {},
            "problemas_encontrados": []
        }
        
        # 1. Configuración de Render
        results["configuracion"] = {
            "debug": str(settings.DEBUG),
            "allowed_hosts": settings.ALLOWED_HOSTS,
            "database_url": "✅ Definido" if os.environ.get('DATABASE_URL') else "❌ No definido",
            "secret_key": "✅ Definido" if settings.SECRET_KEY else "❌ No definido"
        }
        
        # 2. Conexión a PostgreSQL
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                results["base_datos"]["conexion"] = f"✅ PostgreSQL conectado: {version[:50]}..."
        except Exception as e:
            results["base_datos"]["conexion"] = f"❌ Error: {str(e)}"
            results["problemas_encontrados"].append(f"Error de conexión PostgreSQL: {e}")
        
        # 3. Estructura de tablas
        try:
            with connection.cursor() as cursor:
                # Verificar tablas core
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'core_%'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                results["estructura_tablas"]["tablas_core"] = [table[0] for table in tables]
                
                # Verificar estructura de core_group
                try:
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = 'core_group' 
                        ORDER BY ordinal_position
                    """)
                    columns = cursor.fetchall()
                    results["estructura_tablas"]["core_group"] = [
                        {"name": col[0], "type": col[1], "nullable": col[2] == 'YES'} 
                        for col in columns
                    ]
                except Exception as e:
                    results["estructura_tablas"]["core_group"] = f"❌ Error: {str(e)}"
                    results["problemas_encontrados"].append(f"Error en core_group: {e}")
                
                # Verificar estructura de core_student
                try:
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = 'core_student' 
                        ORDER BY ordinal_position
                    """)
                    columns = cursor.fetchall()
                    results["estructura_tablas"]["core_student"] = [
                        {"name": col[0], "type": col[1], "nullable": col[2] == 'YES'} 
                        for col in columns
                    ]
                except Exception as e:
                    results["estructura_tablas"]["core_student"] = f"❌ Error: {str(e)}"
                    results["problemas_encontrados"].append(f"Error en core_student: {e}")
                    
        except Exception as e:
            results["estructura_tablas"]["error"] = f"❌ Error: {str(e)}"
            results["problemas_encontrados"].append(f"Error verificando estructura: {e}")
        
        # 4. Datos críticos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                results["datos_criticos"]["usuarios"] = f"✅ {user_count}"
                
                cursor.execute("SELECT COUNT(*) FROM core_group")
                group_count = cursor.fetchone()[0]
                results["datos_criticos"]["grupos"] = f"✅ {group_count}"
                
                cursor.execute("SELECT COUNT(*) FROM core_student")
                student_count = cursor.fetchone()[0]
                results["datos_criticos"]["estudiantes"] = f"✅ {student_count}"
                
                cursor.execute("SELECT COUNT(*) FROM core_subject")
                subject_count = cursor.fetchone()[0]
                results["datos_criticos"]["asignaturas"] = f"✅ {subject_count}"
                
        except Exception as e:
            results["datos_criticos"]["error"] = f"❌ Error: {str(e)}"
            results["problemas_encontrados"].append(f"Error verificando datos: {e}")
        
        # 5. Pruebas CRUD específicas
        try:
            from core.models import Group, Student
            
            # Probar creación de grupo
            test_group = Group.objects.create(
                name='Test Group Render Debug',
                course='Test Course',
                teacher_id=1
            )
            results["operaciones_crud"]["grupo_creado"] = f"✅ ID {test_group.id}"
            
            # Probar eliminación de grupo
            test_group.delete()
            results["operaciones_crud"]["grupo_eliminado"] = "✅ Eliminado correctamente"
            
            # Probar creación de estudiante
            existing_group = Group.objects.first()
            if existing_group:
                test_student = Student.objects.create(
                    name='Test Student Render Debug',
                    apellidos='Test Apellidos',
                    email='test@render.debug.com',
                    grupo_principal=existing_group
                )
                results["operaciones_crud"]["estudiante_creado"] = f"✅ ID {test_student.id}"
                
                # Probar eliminación de estudiante
                test_student.delete()
                results["operaciones_crud"]["estudiante_eliminado"] = "✅ Eliminado correctamente"
            else:
                results["operaciones_crud"]["estudiante_error"] = "❌ No hay grupos disponibles"
                
        except Exception as e:
            results["operaciones_crud"]["error"] = f"❌ Error: {str(e)}"
            results["problemas_encontrados"].append(f"Error en operaciones CRUD: {e}")
            import traceback
            results["operaciones_crud"]["traceback"] = traceback.format_exc()
        
        # 6. Verificar admin site
        try:
            from django.contrib.admin.sites import site
            registered_count = len(site._registry)
            results["admin_site"] = {
                "registrado": "✅ Admin site funcionando",
                "modelos_registrados": registered_count
            }
        except Exception as e:
            results["admin_site"] = f"❌ Error: {str(e)}"
            results["problemas_encontrados"].append(f"Error en admin site: {e}")
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": str(sys.exc_info())
        })
