from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def fix_database_now(request):
    """
    Endpoint que ejecuta la corrección de base de datos inmediatamente
    Se puede llamar desde el frontend para forzar la corrección
    """
    print("🔥 EJECUTANDO CORRECCIÓN INMEDIATA DE BASE DE DATOS...")
    
    result = {
        'status': 'success',
        'message': 'Corrección ejecutada',
        'fixes_applied': []
    }
    
    try:
        with connection.cursor() as cursor:
            # 1. Forzar creación de columna 'course' en core_group
            try:
                cursor.execute("ALTER TABLE core_group ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO'")
                result['fixes_applied'].append("Columna 'course' agregada a core_group")
                print("✅ Columna 'course' agregada a core_group")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    result['fixes_applied'].append("Columna 'course' ya existe en core_group")
                    print("⚠️  Columna 'course' ya existe en core_group")
                else:
                    result['fixes_applied'].append(f"Error con columna 'course': {e}")
                    print(f"❌ Error con columna 'course': {e}")
            
            # 2. Forzar creación de columna 'grupo_principal_id' en core_student
            try:
                cursor.execute("ALTER TABLE core_student ADD COLUMN grupo_principal_id INTEGER")
                result['fixes_applied'].append("Columna 'grupo_principal_id' agregada a core_student")
                print("✅ Columna 'grupo_principal_id' agregada a core_student")
                
                # Asignar estudiantes existentes al primer grupo
                cursor.execute("SELECT id FROM core_group LIMIT 1")
                first_group = cursor.fetchone()
                if first_group:
                    cursor.execute(f"UPDATE core_student SET grupo_principal_id = {first_group[0]} WHERE grupo_principal_id IS NULL")
                    cursor.execute("ALTER TABLE core_student ALTER COLUMN grupo_principal_id SET NOT NULL")
                    result['fixes_applied'].append(f"Estudiantes asignados al grupo {first_group[0]}")
                    print(f"✅ Estudiantes asignados al grupo {first_group[0]}")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    result['fixes_applied'].append("Columna 'grupo_principal_id' ya existe en core_student")
                    print("⚠️  Columna 'grupo_principal_id' ya existe en core_student")
                else:
                    result['fixes_applied'].append(f"Error con columna 'grupo_principal_id': {e}")
                    print(f"❌ Error con columna 'grupo_principal_id': {e}")
            
            # 3. Forzar creación de columna 'apellidos' en core_student
            try:
                cursor.execute("ALTER TABLE core_student ADD COLUMN apellidos VARCHAR(200) DEFAULT 'Sin Apellidos'")
                result['fixes_applied'].append("Columna 'apellidos' agregada a core_student")
                print("✅ Columna 'apellidos' agregada a core_student")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    result['fixes_applied'].append("Columna 'apellidos' ya existe en core_student")
                    print("⚠️  Columna 'apellidos' ya existe en core_student")
                else:
                    result['fixes_applied'].append(f"Error con columna 'apellidos': {e}")
                    print(f"❌ Error con columna 'apellidos': {e}")
            
            # 4. Forzar creación de tabla core_student_subgrupos
            try:
                cursor.execute("""
                    CREATE TABLE core_student_subgrupos (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL,
                        group_id INTEGER NOT NULL,
                        UNIQUE(student_id, group_id)
                    )
                """)
                result['fixes_applied'].append("Tabla core_student_subgrupos creada")
                print("✅ Tabla core_student_subgrupos creada")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    result['fixes_applied'].append("Tabla core_student_subgrupos ya existe")
                    print("⚠️  Tabla core_student_subgrupos ya existe")
                else:
                    result['fixes_applied'].append(f"Error con tabla core_student_subgrupos: {e}")
                    print(f"❌ Error con tabla core_student_subgrupos: {e}")
            
            # 5. Forzar creación de tabla core_evaluation
            try:
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
                    )
                """)
                result['fixes_applied'].append("Tabla core_evaluation creada")
                print("✅ Tabla core_evaluation creada")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    result['fixes_applied'].append("Tabla core_evaluation ya existe")
                    print("⚠️  Tabla core_evaluation ya existe")
                else:
                    result['fixes_applied'].append(f"Error con tabla core_evaluation: {e}")
                    print(f"❌ Error con tabla core_evaluation: {e}")
        
        print("🎉 CORRECCIÓN INMEDIATA COMPLETADA!")
        result['message'] = 'Corrección completada exitosamente'
        
    except Exception as e:
        print(f"❌ Error durante la corrección inmediata: {e}")
        result['status'] = 'error'
        result['message'] = f'Error durante la corrección: {e}'
    
    return JsonResponse(result)
