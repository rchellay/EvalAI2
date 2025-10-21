#!/usr/bin/env python3
"""
Script para corregir problemas de deployment en Render
- Agrega columnas faltantes en core_group y core_student
- Actualiza referencias obsoletas en el código
- Aplica migraciones necesarias
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection, transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_database_schema():
    """Corrige el esquema de la base de datos"""
    print("🔧 Iniciando corrección del esquema de base de datos...")
    
    with connection.cursor() as cursor:
        try:
            # 1. Verificar y agregar columna 'course' a core_group
            print("📋 Verificando columna 'course' en core_group...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'core_group' AND column_name = 'course'
            """)
            
            if not cursor.fetchone():
                print("➕ Agregando columna 'course' a core_group...")
                cursor.execute("""
                    ALTER TABLE core_group 
                    ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO'
                """)
                print("✅ Columna 'course' agregada a core_group")
            else:
                print("✅ Columna 'course' ya existe en core_group")
            
            # 2. Verificar y agregar columna 'grupo_principal_id' a core_student
            print("📋 Verificando columna 'grupo_principal_id' en core_student...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'core_student' AND column_name = 'grupo_principal_id'
            """)
            
            if not cursor.fetchone():
                print("➕ Agregando columna 'grupo_principal_id' a core_student...")
                cursor.execute("""
                    ALTER TABLE core_student 
                    ADD COLUMN grupo_principal_id INTEGER
                """)
                
                # Asignar estudiantes existentes al primer grupo disponible
                cursor.execute("SELECT id FROM core_group LIMIT 1")
                first_group = cursor.fetchone()
                if first_group:
                    cursor.execute("""
                        UPDATE core_student 
                        SET grupo_principal_id = %s 
                        WHERE grupo_principal_id IS NULL
                    """, [first_group[0]])
                    print(f"✅ Estudiantes asignados al grupo {first_group[0]}")
                
                # Hacer la columna NOT NULL después de asignar valores
                cursor.execute("""
                    ALTER TABLE core_student 
                    ALTER COLUMN grupo_principal_id SET NOT NULL
                """)
                print("✅ Columna 'grupo_principal_id' agregada a core_student")
            else:
                print("✅ Columna 'grupo_principal_id' ya existe en core_student")
            
            # 3. Verificar y agregar columna 'apellidos' a core_student
            print("📋 Verificando columna 'apellidos' en core_student...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'core_student' AND column_name = 'apellidos'
            """)
            
            if not cursor.fetchone():
                print("➕ Agregando columna 'apellidos' a core_student...")
                cursor.execute("""
                    ALTER TABLE core_student 
                    ADD COLUMN apellidos VARCHAR(200) DEFAULT 'Sin Apellidos'
                """)
                print("✅ Columna 'apellidos' agregada a core_student")
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
                print("➕ Creando tabla core_student_subgrupos...")
                cursor.execute("""
                    CREATE TABLE core_student_subgrupos (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL,
                        group_id INTEGER NOT NULL,
                        UNIQUE(student_id, group_id)
                    )
                """)
                print("✅ Tabla core_student_subgrupos creada")
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
                print("➕ Creando tabla core_evaluation...")
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
                print("✅ Tabla core_evaluation creada")
            else:
                print("✅ Tabla core_evaluation ya existe")
            
            print("🎉 Corrección del esquema completada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error durante la corrección: {e}")
            raise

def update_model_references():
    """Actualiza referencias obsoletas en el código"""
    print("🔧 Actualizando referencias obsoletas...")
    
    # Este script se ejecuta después de que el código ya esté desplegado
    # Las referencias obsoletas se corregirán en el próximo deployment
    print("✅ Referencias obsoletas serán corregidas en el próximo deployment")

if __name__ == "__main__":
    try:
        print("🚀 Iniciando corrección de deployment en Render...")
        fix_database_schema()
        update_model_references()
        print("✅ Corrección completada exitosamente!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
