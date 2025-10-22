from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection

@csrf_exempt
@staff_member_required
def create_objective_table(request):
    """Endpoint específico para crear solo la tabla core_objective"""
    
    try:
        results = {
            "status": "success",
            "acciones": {},
            "verificaciones": {},
            "errores": []
        }
        
        with connection.cursor() as cursor:
            
            # Crear tabla core_objective
            print("🔧 Creando tabla core_objective...")
            try:
                cursor.execute("""
                    CREATE TABLE core_objective (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        subject_id INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                results["acciones"]["core_objective_created"] = "✅ Tabla core_objective creada exitosamente"
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    results["acciones"]["core_objective_created"] = "⚠️ Tabla core_objective ya existe"
                else:
                    results["acciones"]["core_objective_created"] = f"❌ Error: {str(e)}"
                    results["errores"].append(f"Error creando tabla core_objective: {e}")
            
            # Verificar que la tabla existe
            try:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'core_objective'
                """)
                table_exists = cursor.fetchone()
                if table_exists:
                    results["verificaciones"]["core_objective_exists"] = "✅ Tabla core_objective confirmada"
                else:
                    results["verificaciones"]["core_objective_exists"] = "❌ Tabla core_objective NO encontrada"
                    results["errores"].append("Tabla core_objective no encontrada después de creación")
            except Exception as e:
                results["verificaciones"]["core_objective_exists"] = f"❌ Error verificando: {str(e)}"
                results["errores"].append(f"Error verificando tabla core_objective: {e}")
            
            # Verificar estructura de la tabla
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_objective' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                results["verificaciones"]["core_objective_structure"] = {
                    "columnas": len(columns),
                    "estructura": [{"name": col[0], "type": col[1]} for col in columns]
                }
            except Exception as e:
                results["verificaciones"]["core_objective_structure"] = f"❌ Error: {str(e)}"
                results["errores"].append(f"Error verificando estructura: {e}")
            
            # Probar consulta simulada que Django hace
            try:
                cursor.execute("""
                    SELECT "core_objective"."id", "core_objective"."title", 
                           "core_objective"."description", "core_objective"."subject_id", 
                           "core_objective"."created_at", "core_objective"."updated_at"
                    FROM "core_objective" 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                results["verificaciones"]["objective_query_simulation"] = "✅ Consulta simulada de Django exitosa"
            except Exception as e:
                results["verificaciones"]["objective_query_simulation"] = f"❌ Error en consulta simulada: {str(e)}"
                results["errores"].append(f"Error en consulta simulada: {e}")
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": str(sys.exc_info())
        })
