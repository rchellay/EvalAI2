from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
import psycopg2
from urllib.parse import urlparse
import os

@csrf_exempt
@staff_member_required
def ultra_fix_now(request):
    """Endpoint ultra-agresivo para corregir errores inmediatamente"""
    
    try:
        results = {
            "status": "success",
            "correcciones": {},
            "verificaciones": {},
            "errores": [],
            "metodo": "ultra_aggressive"
        }
        
        # Método 1: Usar Django connection
        print("🔧 Intentando corrección via Django connection...")
        try:
            with connection.cursor() as cursor:
                
                # 1. FORZAR columna 'date' en core_evaluation
                try:
                    cursor.execute("ALTER TABLE core_evaluation ADD COLUMN date DATE DEFAULT CURRENT_DATE")
                    results["correcciones"]["core_evaluation_date_django"] = "✅ Columna 'date' agregada via Django"
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        results["correcciones"]["core_evaluation_date_django"] = "⚠️ Columna 'date' ya existe via Django"
                    else:
                        results["correcciones"]["core_evaluation_date_django"] = f"❌ Error Django: {str(e)}"
                        results["errores"].append(f"Error Django agregando columna 'date': {e}")
                
                # 2. FORZAR tabla core_notification
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
                    results["correcciones"]["core_notification_django"] = "✅ Tabla core_notification creada via Django"
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        results["correcciones"]["core_notification_django"] = "⚠️ Tabla core_notification ya existe via Django"
                    else:
                        results["correcciones"]["core_notification_django"] = f"❌ Error Django: {str(e)}"
                        results["errores"].append(f"Error Django creando tabla core_notification: {e}")
                
        except Exception as e:
            results["errores"].append(f"Error con Django connection: {e}")
        
        # Método 2: Conexión directa a PostgreSQL (si Django falla)
        print("🔧 Intentando corrección via conexión directa PostgreSQL...")
        try:
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                parsed_url = urlparse(database_url)
                
                conn = psycopg2.connect(
                    host=parsed_url.hostname,
                    port=parsed_url.port,
                    database=parsed_url.path[1:],
                    user=parsed_url.username,
                    password=parsed_url.password
                )
                
                cursor = conn.cursor()
                
                # 1. FORZAR columna 'date' en core_evaluation
                try:
                    cursor.execute("ALTER TABLE core_evaluation ADD COLUMN date DATE DEFAULT CURRENT_DATE")
                    conn.commit()
                    results["correcciones"]["core_evaluation_date_direct"] = "✅ Columna 'date' agregada via conexión directa"
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        results["correcciones"]["core_evaluation_date_direct"] = "⚠️ Columna 'date' ya existe via conexión directa"
                    else:
                        results["correcciones"]["core_evaluation_date_direct"] = f"❌ Error directo: {str(e)}"
                        results["errores"].append(f"Error conexión directa agregando columna 'date': {e}")
                        conn.rollback()
                
                # 2. FORZAR tabla core_notification
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
                    conn.commit()
                    results["correcciones"]["core_notification_direct"] = "✅ Tabla core_notification creada via conexión directa"
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        results["correcciones"]["core_notification_direct"] = "⚠️ Tabla core_notification ya existe via conexión directa"
                    else:
                        results["correcciones"]["core_notification_direct"] = f"❌ Error directo: {str(e)}"
                        results["errores"].append(f"Error conexión directa creando tabla core_notification: {e}")
                        conn.rollback()
                
                cursor.close()
                conn.close()
                
            else:
                results["errores"].append("DATABASE_URL no encontrado para conexión directa")
                
        except Exception as e:
            results["errores"].append(f"Error con conexión directa PostgreSQL: {e}")
        
        # Verificación final
        print("🔧 Verificando estructura final...")
        try:
            with connection.cursor() as cursor:
                
                # Verificar core_evaluation
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
                        "estructura": [{"name": col[0], "type": col[1]} for col in columns],
                        "tiene_date": any(col[0] == 'date' for col in columns)
                    }
                except Exception as e:
                    results["verificaciones"]["core_evaluation"] = f"❌ Error: {str(e)}"
                    results["errores"].append(f"Error verificando core_evaluation: {e}")
                
                # Verificar core_notification
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
                    
        except Exception as e:
            results["errores"].append(f"Error en verificación final: {e}")
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": str(sys.exc_info())
        })
