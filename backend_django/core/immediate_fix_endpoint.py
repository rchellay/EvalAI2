from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def immediate_fix_now(request):
    """
    Corrección inmediata sin autenticación para agregar columnas faltantes
    """
    results = {
        "status": "success",
        "correcciones": {},
        "errores": [],
        "timestamp": None
    }
    
    try:
        from django.utils import timezone
        results["timestamp"] = timezone.now().isoformat()
        
        print("🔥 EJECUTANDO CORRECCIÓN INMEDIATA...")
        
        with connection.cursor() as cursor:
            # 1. CORREGIR core_objective - agregar student_id
            print("1. Corrigiendo core_objective...")
            try:
                cursor.execute("ALTER TABLE core_objective ADD COLUMN student_id INTEGER")
                results["correcciones"]["core_objective_student_id"] = "✅ Columna student_id agregada a core_objective"
                print("✅ Columna student_id agregada a core_objective")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    results["correcciones"]["core_objective_student_id"] = "⚠️ Columna student_id ya existe en core_objective"
                    print("⚠️ Columna student_id ya existe en core_objective")
                else:
                    results["correcciones"]["core_objective_student_id"] = f"❌ Error: {str(e)}"
                    results["errores"].append(f"Error agregando student_id: {e}")
                    print(f"❌ Error agregando student_id: {e}")
            
            # 2. CORREGIR core_notification - agregar recipient_id
            print("2. Corrigiendo core_notification...")
            try:
                cursor.execute("ALTER TABLE core_notification ADD COLUMN recipient_id INTEGER")
                results["correcciones"]["core_notification_recipient_id"] = "✅ Columna recipient_id agregada a core_notification"
                print("✅ Columna recipient_id agregada a core_notification")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    results["correcciones"]["core_notification_recipient_id"] = "⚠️ Columna recipient_id ya existe en core_notification"
                    print("⚠️ Columna recipient_id ya existe en core_notification")
                else:
                    results["correcciones"]["core_notification_recipient_id"] = f"❌ Error: {str(e)}"
                    results["errores"].append(f"Error agregando recipient_id: {e}")
                    print(f"❌ Error agregando recipient_id: {e}")
            
            # 3. VERIFICAR estructura de core_objective
            print("3. Verificando core_objective...")
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_objective'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                results["correcciones"]["core_objective_estructura"] = f"✅ {len(columns)} columnas: {[col[0] for col in columns]}"
                print(f"✅ core_objective tiene {len(columns)} columnas: {[col[0] for col in columns]}")
            except Exception as e:
                results["correcciones"]["core_objective_estructura"] = f"❌ Error verificando: {str(e)}"
                results["errores"].append(f"Error verificando core_objective: {e}")
                print(f"❌ Error verificando core_objective: {e}")
            
            # 4. VERIFICAR estructura de core_notification
            print("4. Verificando core_notification...")
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_notification'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                results["correcciones"]["core_notification_estructura"] = f"✅ {len(columns)} columnas: {[col[0] for col in columns]}"
                print(f"✅ core_notification tiene {len(columns)} columnas: {[col[0] for col in columns]}")
            except Exception as e:
                results["correcciones"]["core_notification_estructura"] = f"❌ Error verificando: {str(e)}"
                results["errores"].append(f"Error verificando core_notification: {e}")
                print(f"❌ Error verificando core_notification: {e}")
            
            # 5. PRUEBA de consulta que fallaba
            print("5. Probando consulta que fallaba...")
            try:
                cursor.execute("""
                    SELECT o.id, o.student_id, o.title 
                    FROM core_objective o 
                    INNER JOIN core_student s ON o.student_id = s.id 
                    LIMIT 1
                """)
                test_result = cursor.fetchone()
                results["correcciones"]["prueba_consulta"] = "✅ Consulta core_objective funciona correctamente"
                print("✅ Consulta core_objective funciona correctamente")
            except Exception as e:
                results["correcciones"]["prueba_consulta"] = f"❌ Error en consulta: {str(e)}"
                results["errores"].append(f"Error en consulta de prueba: {e}")
                print(f"❌ Error en consulta de prueba: {e}")
        
        print("🎉 CORRECCIÓN INMEDIATA COMPLETADA!")
        
    except Exception as e:
        results["status"] = "error"
        results["errores"].append(f"Error general: {str(e)}")
        print(f"❌ Error general en corrección inmediata: {e}")
    
    return JsonResponse(results, json_dumps_params={'indent': 2, 'ensure_ascii': False})
