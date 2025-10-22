#!/usr/bin/env python
"""
Script ultra-agresivo para corregir errores de base de datos en Render
Este script se ejecuta durante el build y fuerza las correcciones
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def ultra_aggressive_fix():
    """Corrección ultra-agresiva de errores de base de datos"""
    
    print("🔥 CORRECCIÓN ULTRA-AGRESIVA DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Obtener DATABASE_URL del entorno
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL no encontrado en variables de entorno")
            return False
        
        # Parsear la URL de la base de datos
        parsed_url = urlparse(database_url)
        
        # Conectar directamente a PostgreSQL
        conn = psycopg2.connect(
            host=parsed_url.hostname,
            port=parsed_url.port,
            database=parsed_url.path[1:],  # Remover el '/' inicial
            user=parsed_url.username,
            password=parsed_url.password
        )
        
        cursor = conn.cursor()
        print("✅ Conectado directamente a PostgreSQL")
        
        # 1. FORZAR creación de columna 'date' en core_evaluation
        print("\n1. FORZANDO COLUMNA 'date' EN core_evaluation:")
        try:
            cursor.execute("ALTER TABLE core_evaluation ADD COLUMN date DATE DEFAULT CURRENT_DATE")
            conn.commit()
            print("   ✅ Columna 'date' agregada a core_evaluation")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️  Columna 'date' ya existe en core_evaluation")
            else:
                print(f"   ❌ Error agregando columna 'date': {e}")
                conn.rollback()
        
        # 2. FORZAR creación de tabla core_notification
        print("\n2. FORZANDO TABLA core_notification:")
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
            print("   ✅ Tabla core_notification creada")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️  Tabla core_notification ya existe")
            else:
                print(f"   ❌ Error creando tabla core_notification: {e}")
                conn.rollback()
        
        # 3. FORZAR creación de tabla core_objective
        print("\n3. FORZANDO TABLA core_objective:")
        try:
            cursor.execute("""
                CREATE TABLE core_objective (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    student_id INTEGER,
                    subject_id INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            conn.commit()
            print("   ✅ Tabla core_objective creada")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️  Tabla core_objective ya existe")
                # Agregar columna student_id si falta
                try:
                    cursor.execute("ALTER TABLE core_objective ADD COLUMN student_id INTEGER")
                    conn.commit()
                    print("   ✅ Columna student_id agregada a core_objective")
                except Exception as add_error:
                    if "already exists" in str(add_error).lower() or "duplicate" in str(add_error).lower():
                        print("   ⚠️  Columna student_id ya existe en core_objective")
                    else:
                        print(f"   ❌ Error agregando student_id: {add_error}")
                        conn.rollback()
            else:
                print(f"   ❌ Error creando tabla core_objective: {e}")
                conn.rollback()
        
        # 3. VERIFICAR estructura final
        print("\n3. VERIFICANDO ESTRUCTURA FINAL:")
        
        # Verificar core_evaluation
        try:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'core_evaluation' 
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"   ✅ core_evaluation: {len(columns)} columnas")
            has_date = False
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
                if col[0] == 'date':
                    has_date = True
            
            if not has_date:
                print("   ❌ CRÍTICO: Columna 'date' no encontrada en core_evaluation")
                return False
            else:
                print("   ✅ Columna 'date' confirmada en core_evaluation")
                
        except Exception as e:
            print(f"   ❌ Error verificando core_evaluation: {e}")
            return False
        
        # Verificar core_notification
        try:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'core_notification' 
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"   ✅ core_notification: {len(columns)} columnas")
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
                
        except Exception as e:
            print(f"   ❌ Error verificando core_notification: {e}")
            return False
        
        cursor.close()
        conn.close()
        
        print("\n🎉 CORRECCIÓN ULTRA-AGRESIVA COMPLETADA!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN CORRECCIÓN ULTRA-AGRESIVA: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ultra_aggressive_fix()
    if success:
        print("\n✅ CORRECCIÓN EXITOSA - BASE DE DATOS CORREGIDA")
        sys.exit(0)
    else:
        print("\n❌ CORRECCIÓN FALLIDA - REVISAR LOGS")
        sys.exit(1)
