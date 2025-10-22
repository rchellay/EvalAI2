#!/usr/bin/env python3
"""
Script para corregir problemas específicos de Render
- Corrige importaciones de OperationalError
- Agrega columnas faltantes en la base de datos
- Actualiza referencias obsoletas
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection, transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_database_columns():
    """Corrige las columnas faltantes en la base de datos"""
    print("🔧 Corrigiendo columnas faltantes en la base de datos...")
    
    with connection.cursor() as cursor:
        try:
            # 1. Agregar columna 'course' a core_group si no existe
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
            
            # 2. Agregar columna 'grupo_principal_id' a core_student si no existe
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
                    cursor.execute("""
                        ALTER TABLE core_student 
                        ALTER COLUMN grupo_principal_id SET NOT NULL
                    """)
                print("✅ Columna 'grupo_principal_id' agregada a core_student")
            else:
                print("✅ Columna 'grupo_principal_id' ya existe en core_student")
            
            # 3. Agregar columna 'apellidos' a core_student si no existe
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
            
            print("🎉 Corrección de columnas completada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error durante la corrección de columnas: {e}")
            raise

if __name__ == "__main__":
    try:
        print("🚀 Iniciando corrección de columnas en Render...")
        fix_database_columns()
        print("✅ Corrección de columnas completada!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
