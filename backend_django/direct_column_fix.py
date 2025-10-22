#!/usr/bin/env python3
"""
Script de corrección directa para Render
Agrega columnas faltantes: student_id a core_objective y recipient_id a core_notification
"""

import os
import psycopg2
from urllib.parse import urlparse

def fix_missing_columns():
    """Corrección directa de columnas faltantes"""
    
    print("🔥 INICIANDO CORRECCIÓN DIRECTA DE COLUMNAS FALTANTES...")
    
    # Obtener DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL no encontrada")
        return False
    
    try:
        # Parsear DATABASE_URL
        parsed = urlparse(database_url)
        
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remover el '/' inicial
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        print("✅ Conectado a PostgreSQL")
        
        # 1. CORREGIR core_objective - agregar student_id
        print("\n1. CORRIGIENDO core_objective...")
        try:
            cursor.execute("ALTER TABLE core_objective ADD COLUMN student_id INTEGER")
            conn.commit()
            print("   ✅ Columna student_id agregada a core_objective")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️ Columna student_id ya existe en core_objective")
            else:
                print(f"   ❌ Error agregando student_id: {e}")
                conn.rollback()
        
        # 2. CORREGIR core_notification - agregar recipient_id
        print("\n2. CORRIGIENDO core_notification...")
        try:
            cursor.execute("ALTER TABLE core_notification ADD COLUMN recipient_id INTEGER")
            conn.commit()
            print("   ✅ Columna recipient_id agregada a core_notification")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️ Columna recipient_id ya existe en core_notification")
            else:
                print(f"   ❌ Error agregando recipient_id: {e}")
                conn.rollback()
        
        # 3. VERIFICAR estructura de core_objective
        print("\n3. VERIFICANDO core_objective...")
        try:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'core_objective'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"   ✅ core_objective tiene {len(columns)} columnas:")
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
        except Exception as e:
            print(f"   ❌ Error verificando core_objective: {e}")
        
        # 4. VERIFICAR estructura de core_notification
        print("\n4. VERIFICANDO core_notification...")
        try:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'core_notification'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"   ✅ core_notification tiene {len(columns)} columnas:")
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
        except Exception as e:
            print(f"   ❌ Error verificando core_notification: {e}")
        
        # 5. PRUEBA de consulta que fallaba
        print("\n5. PROBANDO CONSULTA QUE FALLABA...")
        try:
            cursor.execute("""
                SELECT o.id, o.student_id, o.title 
                FROM core_objective o 
                INNER JOIN core_student s ON o.student_id = s.id 
                LIMIT 1
            """)
            test_result = cursor.fetchone()
            print("   ✅ Consulta core_objective funciona correctamente")
        except Exception as e:
            print(f"   ❌ Error en consulta de prueba: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 CORRECCIÓN DIRECTA COMPLETADA!")
        return True
        
    except Exception as e:
        print(f"❌ Error general en corrección directa: {e}")
        return False

if __name__ == "__main__":
    success = fix_missing_columns()
    if success:
        print("✅ Corrección exitosa")
        exit(0)
    else:
        print("❌ Corrección falló")
        exit(1)
