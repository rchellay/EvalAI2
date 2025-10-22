#!/usr/bin/env python3
"""
Script de corrección directa para Render - Versión mejorada
- Ejecuta correcciones SQL directamente
- Maneja errores de manera robusta
- Asegura que las columnas se agreguen correctamente
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection, transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def execute_sql_safely(cursor, sql, description):
    """Ejecuta SQL de manera segura con manejo de errores"""
    try:
        cursor.execute(sql)
        print(f"✅ {description}")
        return True
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"⚠️  {description} (ya existe)")
            return True
        else:
            print(f"❌ Error en {description}: {e}")
            return False

def fix_database_completely():
    """Corrección completa y robusta de la base de datos"""
    print("🔧 Iniciando corrección completa de la base de datos...")
    
    with connection.cursor() as cursor:
        try:
            # 1. Agregar columna 'course' a core_group
            print("📋 Verificando columna 'course' en core_group...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'core_group' AND column_name = 'course'
            """)
            
            if not cursor.fetchone():
                success = execute_sql_safely(cursor, """
                    ALTER TABLE core_group 
                    ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO'
                """, "Columna 'course' agregada a core_group")
                
                if not success:
                    # Intentar con IF NOT EXISTS (PostgreSQL)
                    execute_sql_safely(cursor, """
                        DO $$ 
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_name = 'core_group' AND column_name = 'course'
                            ) THEN
                                ALTER TABLE core_group ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO';
                            END IF;
                        END $$;
                    """, "Columna 'course' agregada con DO block")
            else:
                print("✅ Columna 'course' ya existe en core_group")
            
            # 2. Agregar columna 'grupo_principal_id' a core_student
            print("📋 Verificando columna 'grupo_principal_id' en core_student...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'core_student' AND column_name = 'grupo_principal_id'
            """)
            
            if not cursor.fetchone():
                # Primero agregar la columna como nullable
                execute_sql_safely(cursor, """
                    ALTER TABLE core_student 
                    ADD COLUMN grupo_principal_id INTEGER
                """, "Columna 'grupo_principal_id' agregada a core_student")
                
                # Asignar estudiantes existentes al primer grupo disponible
                cursor.execute("SELECT id FROM core_group LIMIT 1")
                first_group = cursor.fetchone()
                if first_group:
                    execute_sql_safely(cursor, f"""
                        UPDATE core_student 
                        SET grupo_principal_id = {first_group[0]} 
                        WHERE grupo_principal_id IS NULL
                    """, f"Estudiantes asignados al grupo {first_group[0]}")
                    
                    # Hacer la columna NOT NULL
                    execute_sql_safely(cursor, """
                        ALTER TABLE core_student 
                        ALTER COLUMN grupo_principal_id SET NOT NULL
                    """, "Columna 'grupo_principal_id' marcada como NOT NULL")
            else:
                print("✅ Columna 'grupo_principal_id' ya existe en core_student")
            
            # 3. Agregar columna 'apellidos' a core_student
            print("📋 Verificando columna 'apellidos' en core_student...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'core_student' AND column_name = 'apellidos'
            """)
            
            if not cursor.fetchone():
                execute_sql_safely(cursor, """
                    ALTER TABLE core_student 
                    ADD COLUMN apellidos VARCHAR(200) DEFAULT 'Sin Apellidos'
                """, "Columna 'apellidos' agregada a core_student")
            else:
                print("✅ Columna 'apellidos' ya existe en core_student")
            
            # 4. Crear tabla core_student_subgrupos si no existe
            print("📋 Verificando tabla core_student_subgrupos...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'core_student_subgrupos'
            """)
            
            if not cursor.fetchone():
                execute_sql_safely(cursor, """
                    CREATE TABLE core_student_subgrupos (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL,
                        group_id INTEGER NOT NULL,
                        UNIQUE(student_id, group_id)
                    )
                """, "Tabla core_student_subgrupos creada")
            else:
                print("✅ Tabla core_student_subgrupos ya existe")
            
            # 5. Crear tabla core_evaluation si no existe
            print("📋 Verificando tabla core_evaluation...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'core_evaluation'
            """)
            
            if not cursor.fetchone():
                execute_sql_safely(cursor, """
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
                """, "Tabla core_evaluation creada")
            else:
                print("✅ Tabla core_evaluation ya existe")
            
            print("🎉 Corrección completa de la base de datos finalizada!")
            
        except Exception as e:
            print(f"❌ Error durante la corrección completa: {e}")
            raise

if __name__ == "__main__":
    try:
        print("🚀 Iniciando corrección completa de base de datos en Render...")
        fix_database_completely()
        print("✅ Corrección completa finalizada!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
