#!/usr/bin/env python3
"""
Script de corrección EXTREMA para Render
- Se ejecuta directamente en el código de Django
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

def extreme_database_fix():
    """Corrección extrema de la base de datos"""
    print("🔥 INICIANDO CORRECCIÓN EXTREMA DE BASE DE DATOS...")
    
    with connection.cursor() as cursor:
        try:
            # 1. Forzar creación de columna 'course' en core_group
            print("📋 Forzando creación de columna 'course' en core_group...")
            try:
                cursor.execute("ALTER TABLE core_group ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO'")
                print("✅ Columna 'course' agregada a core_group")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("⚠️  Columna 'course' ya existe en core_group")
                else:
                    print(f"❌ Error con columna 'course': {e}")
            
            # 2. Forzar creación de columna 'grupo_principal_id' en core_student
            print("📋 Forzando creación de columna 'grupo_principal_id' en core_student...")
            try:
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
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("⚠️  Columna 'grupo_principal_id' ya existe en core_student")
                else:
                    print(f"❌ Error con columna 'grupo_principal_id': {e}")
            
            # 3. Forzar creación de columna 'apellidos' en core_student
            print("📋 Forzando creación de columna 'apellidos' en core_student...")
            try:
                cursor.execute("ALTER TABLE core_student ADD COLUMN apellidos VARCHAR(200) DEFAULT 'Sin Apellidos'")
                print("✅ Columna 'apellidos' agregada a core_student")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("⚠️  Columna 'apellidos' ya existe en core_student")
                else:
                    print(f"❌ Error con columna 'apellidos': {e}")
            
            # 4. Forzar creación de tabla core_student_subgrupos
            print("📋 Forzando creación de tabla core_student_subgrupos...")
            try:
                cursor.execute("""
                    CREATE TABLE core_student_subgrupos (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL,
                        group_id INTEGER NOT NULL,
                        UNIQUE(student_id, group_id)
                    )
                """)
                print("✅ Tabla core_student_subgrupos creada")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("⚠️  Tabla core_student_subgrupos ya existe")
                else:
                    print(f"❌ Error con tabla core_student_subgrupos: {e}")
            
            # 5. Forzar creación de tabla core_evaluation
            print("📋 Forzando creación de tabla core_evaluation...")
            try:
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
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("⚠️  Tabla core_evaluation ya existe")
                else:
                    print(f"❌ Error con tabla core_evaluation: {e}")
            
            print("🎉 CORRECCIÓN EXTREMA COMPLETADA!")
            return True
            
        except Exception as e:
            print(f"❌ Error durante la corrección extrema: {e}")
            return False

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO CORRECCIÓN EXTREMA EN RENDER...")
        success = extreme_database_fix()
        if success:
            print("✅ CORRECCIÓN EXTREMA FINALIZADA EXITOSAMENTE!")
        else:
            print("❌ CORRECCIÓN EXTREMA FALLÓ!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
