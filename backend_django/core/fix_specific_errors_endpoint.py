from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection

@csrf_exempt
@staff_member_required
def fix_specific_errors(request):
    """Endpoint para corregir los errores específicos identificados"""
    
    try:
        results = {
            "status": "success",
            "correcciones": {},
            "verificaciones": {},
            "errores": []
        }
        
        with connection.cursor() as cursor:
            
            # 1. Corregir columna 'date' faltante en core_evaluation
            try:
                cursor.execute("ALTER TABLE core_evaluation ADD COLUMN date DATE DEFAULT CURRENT_DATE")
                results["correcciones"]["core_evaluation_date"] = "✅ Columna 'date' agregada"
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    results["correcciones"]["core_evaluation_date"] = "⚠️ Columna 'date' ya existe"
                else:
                    results["correcciones"]["core_evaluation_date"] = f"❌ Error: {str(e)}"
                    results["errores"].append(f"Error agregando columna 'date': {e}")
            
            # 2. Crear tabla core_notification faltante
            try:
                cursor.execute("""
                    CREATE TABLE core_notification (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        message TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        notification_type VARCHAR(50) DEFAULT 'info',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                results["correcciones"]["core_notification"] = "✅ Tabla core_notification creada"
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    results["correcciones"]["core_notification"] = "⚠️ Tabla core_notification ya existe"
                else:
                    results["correcciones"]["core_notification"] = f"❌ Error: {str(e)}"
                    results["errores"].append(f"Error creando tabla core_notification: {e}")
            
            # 3. Verificar estructura final
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_evaluation' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                results["verificaciones"]["core_evaluation"] = {
                    "columnas": len(columns),
                    "estructura": [{"name": col[0], "type": col[1]} for col in columns]
                }
            except Exception as e:
                results["verificaciones"]["core_evaluation"] = f"❌ Error: {str(e)}"
                results["errores"].append(f"Error verificando core_evaluation: {e}")
            
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_notification' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                results["verificaciones"]["core_notification"] = {
                    "columnas": len(columns),
                    "estructura": [{"name": col[0], "type": col[1]} for col in columns]
                }
            except Exception as e:
                results["verificaciones"]["core_notification"] = f"❌ Error: {str(e)}"
                results["errores"].append(f"Error verificando core_notification: {e}")
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": str(sys.exc_info())
        })
