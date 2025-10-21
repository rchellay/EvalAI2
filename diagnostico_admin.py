#!/usr/bin/env python3
"""
Script de diagnóstico completo para el admin de Django
Identifica problemas específicos en modelos, relaciones y configuración
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_django.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from django.core.exceptions import ValidationError
from core.models import Group, Student, Subject, Attendance

def diagnosticar_admin():
    print("🔍 DIAGNÓSTICO COMPLETO DEL ADMIN DE DJANGO")
    print("=" * 60)
    
    # 1. Verificar usuarios
    print("\n1. 👥 VERIFICANDO USUARIOS:")
    try:
        users = User.objects.all()
        print(f"   ✅ Total usuarios: {users.count()}")
        
        superusers = users.filter(is_superuser=True)
        print(f"   ✅ Superusers: {superusers.count()}")
        
        for user in superusers:
            print(f"      - {user.username} (ID: {user.id})")
            
    except Exception as e:
        print(f"   ❌ Error en usuarios: {e}")
    
    # 2. Verificar modelos básicos
    print("\n2. 📊 VERIFICANDO MODELOS:")
    
    try:
        students_count = Student.objects.count()
        print(f"   ✅ Estudiantes: {students_count}")
    except Exception as e:
        print(f"   ❌ Error en estudiantes: {e}")
    
    try:
        subjects_count = Subject.objects.count()
        print(f"   ✅ Asignaturas: {subjects_count}")
    except Exception as e:
        print(f"   ❌ Error en asignaturas: {e}")
    
    try:
        groups_count = Group.objects.count()
        print(f"   ✅ Grupos: {groups_count}")
    except Exception as e:
        print(f"   ❌ Error en grupos: {e}")
    
    try:
        attendance_count = Attendance.objects.count()
        print(f"   ✅ Asistencias: {attendance_count}")
    except Exception as e:
        print(f"   ❌ Error en asistencias: {e}")
    
    # 3. Verificar relaciones problemáticas
    print("\n3. 🔗 VERIFICANDO RELACIONES:")
    
    try:
        # Grupos sin teacher
        grupos_sin_teacher = Group.objects.filter(teacher__isnull=True)
        print(f"   ⚠️  Grupos sin teacher: {grupos_sin_teacher.count()}")
        
        if grupos_sin_teacher.exists():
            for grupo in grupos_sin_teacher[:5]:  # Mostrar solo los primeros 5
                print(f"      - Grupo ID {grupo.id}: '{grupo.name}'")
                
    except Exception as e:
        print(f"   ❌ Error verificando grupos sin teacher: {e}")
    
    try:
        # Asistencias sin recorded_by
        asistencias_sin_recorded_by = Attendance.objects.filter(recorded_by__isnull=True)
        print(f"   ⚠️  Asistencias sin recorded_by: {asistencias_sin_recorded_by.count()}")
        
    except Exception as e:
        print(f"   ❌ Error verificando asistencias sin recorded_by: {e}")
    
    # 4. Probar creación de objetos
    print("\n4. 🧪 PROBANDO CREACIÓN DE OBJETOS:")
    
    try:
        # Obtener un usuario superuser para las pruebas
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            print("   ❌ No hay superusers disponibles para las pruebas")
            return
        
        print(f"   ✅ Usando superuser: {superuser.username}")
        
        # Probar creación de Group
        try:
            test_group = Group.objects.create(
                name="GRUPO_TEST_DIAGNOSTICO",
                teacher=superuser
            )
            print(f"   ✅ Grupo creado exitosamente: ID {test_group.id}")
            
            # Limpiar el grupo de prueba
            test_group.delete()
            print(f"   ✅ Grupo de prueba eliminado")
            
        except Exception as e:
            print(f"   ❌ Error creando grupo: {e}")
        
        # Probar creación de Attendance
        try:
            # Obtener un estudiante y asignatura para la prueba
            student = Student.objects.first()
            subject = Subject.objects.first()
            
            if student and subject:
                test_attendance = Attendance.objects.create(
                    student=student,
                    subject=subject,
                    date="2025-10-21",
                    status="presente",
                    recorded_by=superuser
                )
                print(f"   ✅ Asistencia creada exitosamente: ID {test_attendance.id}")
                
                # Limpiar la asistencia de prueba
                test_attendance.delete()
                print(f"   ✅ Asistencia de prueba eliminada")
            else:
                print(f"   ⚠️  No hay estudiantes o asignaturas para probar Attendance")
                
        except Exception as e:
            print(f"   ❌ Error creando asistencia: {e}")
            
    except Exception as e:
        print(f"   ❌ Error en pruebas de creación: {e}")
    
    # 5. Verificar configuración de la base de datos
    print("\n5. 🗄️  VERIFICANDO BASE DE DATOS:")
    
    try:
        with connection.cursor() as cursor:
            # Verificar tablas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('core_group', 'core_attendance', 'core_student', 'core_subject')
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"   ✅ Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"      - {table[0]}")
                
    except Exception as e:
        print(f"   ❌ Error verificando base de datos: {e}")
    
    # 6. Verificar constraints y foreign keys
    print("\n6. 🔒 VERIFICANDO CONSTRAINTS:")
    
    try:
        with connection.cursor() as cursor:
            # Verificar foreign keys de Group
            cursor.execute("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = 'core_group';
            """)
            fks = cursor.fetchall()
            
            print(f"   ✅ Foreign keys en core_group: {len(fks)}")
            for fk in fks:
                print(f"      - {fk[2]} -> {fk[3]}.{fk[4]}")
                
    except Exception as e:
        print(f"   ❌ Error verificando constraints: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    diagnosticar_admin()
