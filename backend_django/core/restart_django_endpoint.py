import sys

@csrf_exempt
@staff_member_required
def restart_django_connection(request):
    """Endpoint para reiniciar la conexión de Django y limpiar caché"""
    
    try:
        results = {
            "status": "success",
            "acciones": {},
            "verificaciones": {},
            "errores": []
        }
        
        # 1. Limpiar caché de Django
        print("🔄 Limpiando caché de Django...")
        try:
            cache.clear()
            results["acciones"]["cache_cleared"] = "✅ Caché de Django limpiado"
        except Exception as e:
            results["acciones"]["cache_cleared"] = f"❌ Error limpiando caché: {str(e)}"
            results["errores"].append(f"Error limpiando caché: {e}")
        
        # 2. Cerrar y reabrir conexión de base de datos
        print("🔄 Reiniciando conexión de base de datos...")
        try:
            connection.close()
            # Forzar nueva conexión
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                results["acciones"]["db_connection_restarted"] = "✅ Conexión de base de datos reiniciada"
        except Exception as e:
            results["acciones"]["db_connection_restarted"] = f"❌ Error reiniciando conexión: {str(e)}"
            results["errores"].append(f"Error reiniciando conexión: {e}")
        
        # 3. Verificar que las tablas están accesibles
        print("🔍 Verificando acceso a tablas...")
        try:
            with connection.cursor() as cursor:
                
                # Verificar core_evaluation
                try:
                    cursor.execute("SELECT COUNT(*) FROM core_evaluation")
                    count = cursor.fetchone()[0]
                    results["verificaciones"]["core_evaluation_access"] = f"✅ Acceso a core_evaluation: {count} registros"
                except Exception as e:
                    results["verificaciones"]["core_evaluation_access"] = f"❌ Error accediendo core_evaluation: {str(e)}"
                    results["errores"].append(f"Error accediendo core_evaluation: {e}")
                
                # Verificar core_notification
                try:
                    cursor.execute("SELECT COUNT(*) FROM core_notification")
                    count = cursor.fetchone()[0]
                    results["verificaciones"]["core_notification_access"] = f"✅ Acceso a core_notification: {count} registros"
                except Exception as e:
                    results["verificaciones"]["core_notification_access"] = f"❌ Error accediendo core_notification: {str(e)}"
                    results["errores"].append(f"Error accediendo core_notification: {e}")
                
                # Verificar estructura de core_evaluation
                try:
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'core_evaluation' 
                        AND column_name = 'date'
                    """)
                    date_column = cursor.fetchone()
                    if date_column:
                        results["verificaciones"]["core_evaluation_date_column"] = "✅ Columna 'date' confirmada en core_evaluation"
                    else:
                        results["verificaciones"]["core_evaluation_date_column"] = "❌ Columna 'date' NO encontrada en core_evaluation"
                        results["errores"].append("Columna 'date' no encontrada en core_evaluation")
                except Exception as e:
                    results["verificaciones"]["core_evaluation_date_column"] = f"❌ Error verificando columna 'date': {str(e)}"
                    results["errores"].append(f"Error verificando columna 'date': {e}")
                
                # Verificar que core_notification existe
                try:
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_name = 'core_notification'
                    """)
                    table_exists = cursor.fetchone()
                    if table_exists:
                        results["verificaciones"]["core_notification_exists"] = "✅ Tabla core_notification confirmada"
                    else:
                        results["verificaciones"]["core_notification_exists"] = "❌ Tabla core_notification NO encontrada"
                        results["errores"].append("Tabla core_notification no encontrada")
                except Exception as e:
                    results["verificaciones"]["core_notification_exists"] = f"❌ Error verificando tabla core_notification: {str(e)}"
                    results["errores"].append(f"Error verificando tabla core_notification: {e}")
        
        except Exception as e:
            results["errores"].append(f"Error en verificación de tablas: {e}")
        
        # 4. Probar operación de eliminación simulada
        print("🧪 Probando operación de eliminación simulada...")
        try:
            with connection.cursor() as cursor:
                # Simular la consulta que Django hace al eliminar
                try:
                    cursor.execute("""
                        SELECT "core_evaluation"."id", "core_evaluation"."student_id", 
                               "core_evaluation"."subject_id", "core_evaluation"."evaluator_id", 
                               "core_evaluation"."score", "core_evaluation"."comment", 
                               "core_evaluation"."rubric_id", "core_evaluation"."created_at", 
                               "core_evaluation"."updated_at", "core_evaluation"."date"
                        FROM "core_evaluation" 
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    results["verificaciones"]["evaluation_query_simulation"] = "✅ Consulta de eliminación simulada exitosa"
                except Exception as e:
                    results["verificaciones"]["evaluation_query_simulation"] = f"❌ Error en consulta simulada: {str(e)}"
                    results["errores"].append(f"Error en consulta simulada: {e}")
                
                # Simular consulta de core_notification
                try:
                    cursor.execute("""
                        SELECT "core_notification"."id", "core_notification"."user_id", 
                               "core_notification"."title", "core_notification"."message", 
                               "core_notification"."is_read", "core_notification"."notification_type", 
                               "core_notification"."created_at", "core_notification"."updated_at"
                        FROM "core_notification" 
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    results["verificaciones"]["notification_query_simulation"] = "✅ Consulta de notificación simulada exitosa"
                except Exception as e:
                    results["verificaciones"]["notification_query_simulation"] = f"❌ Error en consulta simulada: {str(e)}"
                    results["errores"].append(f"Error en consulta simulada: {e}")
        
        except Exception as e:
            results["errores"].append(f"Error en pruebas de consulta: {e}")
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": str(sys.exc_info())
        })
