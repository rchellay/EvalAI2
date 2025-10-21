#!/usr/bin/env python3
"""
Script para migrar datos existentes a la nueva estructura jerárquica
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from core.models import Group, Student

def migrar_datos_existentes():
    print("🔄 MIGRANDO DATOS EXISTENTES A NUEVA ESTRUCTURA JERÁRQUICA")
    print("=" * 60)
    
    try:
        with connection.cursor() as cursor:
            # 1. Verificar estructura actual
            print("\n1. 📋 VERIFICANDO ESTRUCTURA ACTUAL:")
            
            # Verificar si existe la tabla core_group
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='core_group';
            """)
            group_table_exists = cursor.fetchone() is not None
            print(f"   ✅ Tabla core_group existe: {group_table_exists}")
            
            if group_table_exists:
                # Verificar columnas existentes
                cursor.execute("PRAGMA table_info(core_group);")
                group_columns = [row[1] for row in cursor.fetchall()]
                print(f"   📊 Columnas en core_group: {group_columns}")
            
            # Verificar si existe la tabla core_student
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='core_student';
            """)
            student_table_exists = cursor.fetchone() is not None
            print(f"   ✅ Tabla core_student existe: {student_table_exists}")
            
            if student_table_exists:
                # Verificar columnas existentes
                cursor.execute("PRAGMA table_info(core_student);")
                student_columns = [row[1] for row in cursor.fetchall()]
                print(f"   📊 Columnas en core_student: {student_columns}")
            
            # 2. Agregar columnas faltantes a core_group
            print("\n2. 🔧 AGREGANDO COLUMNAS A CORE_GROUP:")
            
            if group_table_exists:
                # Agregar columna course si no existe
                if 'course' not in group_columns:
                    cursor.execute("ALTER TABLE core_group ADD COLUMN course VARCHAR(50) DEFAULT '4t ESO';")
                    print("   ✅ Columna 'course' agregada a core_group")
                else:
                    print("   ✅ Columna 'course' ya existe en core_group")
            
            # 3. Agregar columnas faltantes a core_student
            print("\n3. 🔧 AGREGANDO COLUMNAS A CORE_STUDENT:")
            
            if student_table_exists:
                # Agregar columna apellidos si no existe
                if 'apellidos' not in student_columns:
                    cursor.execute("ALTER TABLE core_student ADD COLUMN apellidos VARCHAR(200) DEFAULT 'Sin Apellidos';")
                    print("   ✅ Columna 'apellidos' agregada a core_student")
                else:
                    print("   ✅ Columna 'apellidos' ya existe en core_student")
                
                # Agregar columna grupo_principal si no existe
                if 'grupo_principal_id' not in student_columns:
                    # Primero crear un grupo por defecto si no existe
                    cursor.execute("""
                        INSERT INTO core_group (name, course, teacher_id, created_at, updated_at)
                        SELECT 'Grupo Por Defecto', '4t ESO', 1, datetime('now'), datetime('now')
                        WHERE NOT EXISTS (SELECT 1 FROM core_group LIMIT 1);
                    """)
                    print("   ✅ Grupo por defecto creado si no existía")
                    
                    # Obtener el ID del primer grupo
                    cursor.execute("SELECT id FROM core_group ORDER BY id LIMIT 1;")
                    default_group_id = cursor.fetchone()[0]
                    
                    # Agregar columna grupo_principal
                    cursor.execute(f"""
                        ALTER TABLE core_student 
                        ADD COLUMN grupo_principal_id INTEGER DEFAULT {default_group_id};
                    """)
                    print(f"   ✅ Columna 'grupo_principal_id' agregada a core_student con valor por defecto {default_group_id}")
                else:
                    print("   ✅ Columna 'grupo_principal_id' ya existe en core_student")
            
            # 4. Crear tabla de relación subgrupos si no existe
            print("\n4. 🔧 CREANDO TABLA DE SUBGRUPOS:")
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='core_student_subgrupos';
            """)
            subgrupos_table_exists = cursor.fetchone() is not None
            
            if not subgrupos_table_exists:
                cursor.execute("""
                    CREATE TABLE core_student_subgrupos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        group_id INTEGER NOT NULL,
                        UNIQUE(student_id, group_id)
                    );
                """)
                print("   ✅ Tabla 'core_student_subgrupos' creada")
            else:
                print("   ✅ Tabla 'core_student_subgrupos' ya existe")
            
            # 5. Migrar datos existentes
            print("\n5. 📊 MIGRANDO DATOS EXISTENTES:")
            
            if student_table_exists and group_table_exists:
                # Actualizar apellidos vacíos
                cursor.execute("""
                    UPDATE core_student 
                    SET apellidos = 'Sin Apellidos' 
                    WHERE apellidos IS NULL OR apellidos = '';
                """)
                print("   ✅ Apellidos actualizados para estudiantes sin apellidos")
                
                # Actualizar grupo_principal vacíos
                cursor.execute("""
                    UPDATE core_student 
                    SET grupo_principal_id = (
                        SELECT id FROM core_group ORDER BY id LIMIT 1
                    )
                    WHERE grupo_principal_id IS NULL;
                """)
                print("   ✅ Grupo principal asignado a estudiantes sin grupo")
            
            print("\n" + "=" * 60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrar_datos_existentes()
