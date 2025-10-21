#!/usr/bin/env python3
"""
Script para eliminar la columna course de core_student
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def eliminar_columna_course():
    print("🗑️ ELIMINANDO COLUMNA COURSE DE CORE_STUDENT")
    print("=" * 50)
    
    try:
        with connection.cursor() as cursor:
            # Deshabilitar foreign keys temporalmente
            cursor.execute("PRAGMA foreign_keys=OFF;")
            
            # Verificar si la columna course existe
            cursor.execute("PRAGMA table_info(core_student);")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'course' in columns:
                print("   ✅ Columna 'course' encontrada en core_student")
                
                # Limpiar tabla temporal si existe
                cursor.execute("DROP TABLE IF EXISTS core_student_new;")
                
                # En SQLite no se puede eliminar columnas directamente
                # Necesitamos recrear la tabla sin la columna course
                print("   🔄 Recreando tabla sin columna 'course'...")
                
                # 1. Crear tabla temporal con la nueva estructura
                cursor.execute("""
                    CREATE TABLE core_student_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(200) NOT NULL,
                        apellidos VARCHAR(200) NOT NULL,
                        email VARCHAR(254) NOT NULL UNIQUE,
                        photo VARCHAR(100),
                        attendance_percentage REAL NOT NULL DEFAULT 0.0,
                        grupo_principal_id INTEGER NOT NULL,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL
                    );
                """)
                print("   ✅ Tabla temporal creada")
                
                # 2. Copiar datos sin la columna course
                cursor.execute("""
                    INSERT INTO core_student_new (
                        id, name, apellidos, email, photo, attendance_percentage,
                        grupo_principal_id, created_at, updated_at
                    )
                    SELECT 
                        id, name, apellidos, email, photo, attendance_percentage,
                        grupo_principal_id, created_at, updated_at
                    FROM core_student;
                """)
                print("   ✅ Datos copiados a tabla temporal")
                
                # 3. Eliminar tabla original
                cursor.execute("DROP TABLE core_student;")
                print("   ✅ Tabla original eliminada")
                
                # 4. Renombrar tabla temporal
                cursor.execute("ALTER TABLE core_student_new RENAME TO core_student;")
                print("   ✅ Tabla temporal renombrada")
                
                # 5. Recrear índices
                cursor.execute("CREATE UNIQUE INDEX core_student_email_unique ON core_student (email);")
                cursor.execute("CREATE INDEX core_student_grupo_principal_id ON core_student (grupo_principal_id);")
                print("   ✅ Índices recreados")
                
                print("\n✅ COLUMNA COURSE ELIMINADA EXITOSAMENTE")
            else:
                print("   ✅ Columna 'course' no existe en core_student")
            
            # Rehabilitar foreign keys
            cursor.execute("PRAGMA foreign_keys=ON;")
            
            # Verificar estructura final
            cursor.execute("PRAGMA table_info(core_student);")
            final_columns = [row[1] for row in cursor.fetchall()]
            print(f"\n📋 Estructura final de core_student: {final_columns}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    eliminar_columna_course()
