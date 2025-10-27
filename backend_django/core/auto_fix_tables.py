import os
import django
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

def verificar_y_crear_tablas():
    """
    Función que se ejecuta al iniciar la aplicación para verificar y crear tablas faltantes
    """
    try:
        with connection.cursor() as cursor:
            # Verificar si core_attendance existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'core_attendance'
                );
            """)
            attendance_exists = cursor.fetchone()[0]
            
            if not attendance_exists:
                print("🔨 Creando tabla core_attendance...")
                cursor.execute("""
                    CREATE TABLE core_attendance (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL,
                        subject_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        status VARCHAR(10) NOT NULL,
                        comment TEXT,
                        recorded_by_id INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                print("✅ Tabla core_attendance creada")
            
            # Verificar si teacher_id existe en core_group
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'core_group' 
                    AND column_name = 'teacher_id'
                );
            """)
            teacher_id_exists = cursor.fetchone()[0]
            
            if not teacher_id_exists:
                print("🔨 Agregando columna teacher_id a core_group...")
                cursor.execute("""
                    ALTER TABLE core_group 
                    ADD COLUMN teacher_id INTEGER;
                """)
                print("✅ Columna teacher_id agregada a core_group")
            
            # Crear índices si no existen
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_student ON core_attendance(student_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_subject ON core_attendance(subject_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_date ON core_attendance(date);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_group_teacher ON core_group(teacher_id);")
                print("✅ Índices creados/verificados")
            except Exception as e:
                print(f"⚠️  Error creando índices (puede ser normal): {e}")
                
    except Exception as e:
        print(f"❌ Error verificando/creando tablas: {e}")

# Ejecutar al importar el módulo
# verficar_y_crear_tablas()  # Desactivado para evitar conflictos con migraciones
