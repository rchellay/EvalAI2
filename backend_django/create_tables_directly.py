#!/usr/bin/env python3
"""
Script para crear tablas directamente en Render
Este script se ejecutará durante el build process
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.core.exceptions import OperationalError

def crear_tablas_directamente():
    print("🔨 CREANDO TABLAS DIRECTAMENTE EN RENDER...")
    
    try:
        # Verificar conexión
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            print("✅ Conexión a base de datos exitosa")
        
        # Crear tabla core_attendance directamente
        print("🔨 Creando tabla core_attendance...")
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_attendance (
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
        
        # Agregar columna teacher_id a core_group si no existe
        print("🔨 Agregando columna teacher_id a core_group...")
        with connection.cursor() as cursor:
            # Verificar si la columna existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'core_group' 
                    AND column_name = 'teacher_id'
                );
            """)
            teacher_id_exists = cursor.fetchone()[0]
            
            if not teacher_id_exists:
                cursor.execute("""
                    ALTER TABLE core_group 
                    ADD COLUMN teacher_id INTEGER;
                """)
                print("✅ Columna teacher_id agregada a core_group")
            else:
                print("✅ Columna teacher_id ya existe en core_group")
        
        # Crear índices
        print("🔨 Creando índices...")
        with connection.cursor() as cursor:
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_student ON core_attendance(student_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_subject ON core_attendance(subject_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_attendance_date ON core_attendance(date);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_group_teacher ON core_group(teacher_id);")
                print("✅ Índices creados")
            except Exception as e:
                print(f"⚠️  Error creando índices (puede ser normal): {e}")
        
        # Aplicar migraciones para sincronizar el estado
        print("🔄 Aplicando migraciones para sincronizar estado...")
        execute_from_command_line(['manage.py', 'migrate', '--fake', '--noinput'])
        
        # Verificar estado final
        print("✅ Verificación final:")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'core_attendance'
                );
            """)
            attendance_final = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'core_group' 
                    AND column_name = 'teacher_id'
                );
            """)
            teacher_id_final = cursor.fetchone()[0]
            
            print(f"   📋 core_attendance: {'✅ OK' if attendance_final else '❌ FALTA'}")
            print(f"   📋 teacher_id en core_group: {'✅ OK' if teacher_id_final else '❌ FALTA'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        import traceback
        print(f"Detalles: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    crear_tablas_directamente()
