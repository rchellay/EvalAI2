#!/usr/bin/env python3
"""
Script para verificar y corregir la base de datos en Render
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

def verificar_y_corregir_bd():
    print("🔍 VERIFICANDO Y CORRIGIENDO BASE DE DATOS...")
    
    try:
        # Verificar conexión
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            print("✅ Conexión a base de datos exitosa")
        
        # Verificar si las tablas existen
        with connection.cursor() as cursor:
            # Verificar tabla core_attendance
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'core_attendance'
                );
            """)
            attendance_exists = cursor.fetchone()[0]
            print(f"📋 Tabla core_attendance: {'✅ Existe' if attendance_exists else '❌ No existe'}")
            
            # Verificar columna teacher_id en core_group
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'core_group' 
                    AND column_name = 'teacher_id'
                );
            """)
            teacher_id_exists = cursor.fetchone()[0]
            print(f"📋 Columna teacher_id en core_group: {'✅ Existe' if teacher_id_exists else '❌ No existe'}")
        
        # Si faltan tablas/columnas, aplicar migraciones específicas
        if not attendance_exists or not teacher_id_exists:
            print("🔄 Aplicando migraciones específicas...")
            
            # Aplicar migración de attendance
            if not attendance_exists:
                print("📋 Aplicando migración 0007_attendance...")
                execute_from_command_line(['manage.py', 'migrate', 'core', '0007', '--noinput'])
            
            # Aplicar migración de group_teacher
            if not teacher_id_exists:
                print("📋 Aplicando migración 0008_group_teacher...")
                execute_from_command_line(['manage.py', 'migrate', 'core', '0008', '--noinput'])
            
            # Aplicar migración de alter_group_teacher
            print("📋 Aplicando migración 0009_alter_group_teacher...")
            execute_from_command_line(['manage.py', 'migrate', 'core', '0009', '--noinput'])
        
        # Aplicar todas las migraciones pendientes
        print("🔄 Aplicando todas las migraciones pendientes...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
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
        print(f"❌ Error verificando/corrigiendo BD: {e}")
        import traceback
        print(f"Detalles: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    verificar_y_corregir_bd()
