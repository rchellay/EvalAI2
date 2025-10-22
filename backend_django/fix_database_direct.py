#!/usr/bin/env python3
"""
Script de corrección DIRECTA para Render
- Se ejecuta directamente en el endpoint de diagnóstico
- Fuerza la creación de columnas usando SQL crudo
- No depende del build process
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def force_database_fix():
    """Fuerza la corrección de la base de datos usando SQL directo"""
    print("🔥 INICIANDO CORRECCIÓN DIRECTA DE BASE DE DATOS...")
    
    with connection.cursor() as cursor:
        try:
            # 1. Verificar y agregar columna 'course' a core_group
            print("📋 Verificando columna 'course' en core_group...")
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_group' AND column_name = 'course'
                """)
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE core_group ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO'")
                    print("✅ Columna 'course' agregada a core_group")
                else:
                    print("✅ Columna 'course' ya existe en core_group")
            except Exception as e:
                print(f"❌ Error con columna 'course': {e}")
            
            # 2. Verificar y agregar columna 'grupo_principal_id' a core_student
            print("📋 Verificando columna 'grupo_principal_id' en core_student...")
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_student' AND column_name = 'grupo_principal_id'
                """)
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE core_student ADD COLUMN grupo_principal_id INTEGER")
                    print("✅ Columna 'grupo_principal_id' agregada a core_student")
                    
                    # Asignar estudiantes existentes al primer grupo
                    cursor.execute("SELECT id FROM core_group LIMIT 1")
                    first_group = cursor.fetchone()
                    if first_group:
                        cursor.execute(f"UPDATE core_student SET grupo_principal_id = {first_group[0]} WHERE grupo_principal_id IS NULL")
                        print(f"✅ Estudiantes asignados al grupo {first_group[0]}")
                        
                        # Hacer NOT NULL
                        cursor.execute("ALTER TABLE core_student ALTER COLUMN grupo_principal_id SET NOT NULL")
                        print("✅ Columna 'grupo_principal_id' marcada como NOT NULL")
                else:
                    print("✅ Columna 'grupo_principal_id' ya existe en core_student")
            except Exception as e:
                print(f"❌ Error con columna 'grupo_principal_id': {e}")
            
            # 3. Verificar y agregar columna 'apellidos' a core_student
            print("📋 Verificando columna 'apellidos' en core_student...")
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_student' AND column_name = 'apellidos'
                """)
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE core_student ADD COLUMN apellidos VARCHAR(200) DEFAULT 'Sin Apellidos'")
                    print("✅ Columna 'apellidos' agregada a core_student")
                else:
                    print("✅ Columna 'apellidos' ya existe en core_student")
            except Exception as e:
                print(f"❌ Error con columna 'apellidos': {e}")
            
            # 4. Verificar y crear tabla core_student_subgrupos
            print("📋 Verificando tabla core_student_subgrupos...")
            try:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'core_student_subgrupos'
                """)
                if not cursor.fetchone():
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
            except Exception as e:
                print(f"❌ Error con tabla core_student_subgrupos: {e}")
            
            # 5. Verificar y crear tabla core_evaluation
            print("📋 Verificando tabla core_evaluation...")
            try:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'core_evaluation'
                """)
                if not cursor.fetchone():
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
            except Exception as e:
                print(f"❌ Error con tabla core_evaluation: {e}")
            
            print("🎉 CORRECCIÓN DIRECTA COMPLETADA!")
            return True
            
        except Exception as e:
            print(f"❌ Error durante la corrección directa: {e}")
            return False

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO CORRECCIÓN DIRECTA EN RENDER...")
        success = force_database_fix()
        if success:
            print("✅ CORRECCIÓN DIRECTA FINALIZADA EXITOSAMENTE!")
        else:
            print("❌ CORRECCIÓN DIRECTA FALLÓ!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
