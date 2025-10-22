#!/usr/bin/env python
"""
Script para diagnosticar errores 500 específicamente en Render deployment
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def diagnosticar_render_500():
    """Diagnosticar problemas específicos en Render que causan error 500"""
    
    print("🔍 DIAGNÓSTICO ESPECÍFICO DE ERROR 500 EN RENDER")
    print("=" * 60)
    
    try:
        # 1. Verificar configuración de Render
        print("\n1. CONFIGURACIÓN DE RENDER:")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   DATABASE_URL: {'✅ Definido' if os.environ.get('DATABASE_URL') else '❌ No definido'}")
        print(f"   SECRET_KEY: {'✅ Definido' if settings.SECRET_KEY else '❌ No definido'}")
        
        # 2. Verificar conexión a PostgreSQL en Render
        print("\n2. CONEXIÓN A POSTGRESQL EN RENDER:")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                print(f"   ✅ PostgreSQL conectado: {version[:50]}...")
        except Exception as e:
            print(f"   ❌ Error de conexión PostgreSQL: {e}")
            return
        
        # 3. Verificar estructura de tablas en PostgreSQL
        print("\n3. ESTRUCTURA DE TABLAS EN POSTGRESQL:")
        with connection.cursor() as cursor:
            # Verificar si las tablas existen
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'core_%'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"   Tablas core encontradas: {len(tables)}")
            for table in tables:
                print(f"     - {table[0]}")
            
            # Verificar estructura específica de core_group
            try:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_group' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print(f"\n   Estructura de core_group:")
                for col in columns:
                    print(f"     - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            except Exception as e:
                print(f"   ❌ Error verificando core_group: {e}")
            
            # Verificar estructura específica de core_student
            try:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_student' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print(f"\n   Estructura de core_student:")
                for col in columns:
                    print(f"     - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            except Exception as e:
                print(f"   ❌ Error verificando core_student: {e}")
        
        # 4. Verificar datos críticos
        print("\n4. DATOS CRÍTICOS:")
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                print(f"   ✅ Usuarios: {user_count}")
                
                cursor.execute("SELECT COUNT(*) FROM core_group")
                group_count = cursor.fetchone()[0]
                print(f"   ✅ Grupos: {group_count}")
                
                cursor.execute("SELECT COUNT(*) FROM core_student")
                student_count = cursor.fetchone()[0]
                print(f"   ✅ Estudiantes: {student_count}")
                
                cursor.execute("SELECT COUNT(*) FROM core_subject")
                subject_count = cursor.fetchone()[0]
                print(f"   ✅ Asignaturas: {subject_count}")
            except Exception as e:
                print(f"   ❌ Error verificando datos: {e}")
        
        # 5. Probar operaciones específicas que pueden fallar en Render
        print("\n5. PRUEBAS DE OPERACIONES EN RENDER:")
        
        # Probar acceso a admin
        try:
            from django.contrib.admin.sites import site
            print(f"   ✅ Admin site: {site}")
            
            # Probar registro de modelos
            registered_count = len(site._registry)
            print(f"   ✅ Modelos registrados: {registered_count}")
            
        except Exception as e:
            print(f"   ❌ Error en admin site: {e}")
        
        # 6. Verificar problemas específicos de PostgreSQL
        print("\n6. PROBLEMAS ESPECÍFICOS DE POSTGRESQL:")
        with connection.cursor() as cursor:
            # Verificar si hay problemas de permisos
            try:
                cursor.execute("SELECT current_user, current_database()")
                user_db = cursor.fetchone()
                print(f"   Usuario actual: {user_db[0]}")
                print(f"   Base de datos actual: {user_db[1]}")
            except Exception as e:
                print(f"   ❌ Error verificando permisos: {e}")
            
            # Verificar si hay problemas de esquema
            try:
                cursor.execute("SELECT current_schema()")
                schema = cursor.fetchone()[0]
                print(f"   Esquema actual: {schema}")
            except Exception as e:
                print(f"   ❌ Error verificando esquema: {e}")
        
        # 7. Probar operaciones CRUD específicas
        print("\n7. PRUEBAS CRUD ESPECÍFICAS:")
        
        # Probar creación de grupo
        try:
            from core.models import Group
            test_group = Group.objects.create(
                name='Test Group Render',
                course='Test Course',
                teacher_id=1  # Usar ID del admin
            )
            print(f"   ✅ Creación de grupo exitosa: ID {test_group.id}")
            
            # Probar eliminación de grupo
            test_group.delete()
            print(f"   ✅ Eliminación de grupo exitosa")
            
        except Exception as e:
            print(f"   ❌ Error en operaciones de grupo: {e}")
            import traceback
            traceback.print_exc()
        
        # Probar creación de estudiante
        try:
            from core.models import Student
            # Obtener un grupo existente
            existing_group = Group.objects.first()
            if existing_group:
                test_student = Student.objects.create(
                    name='Test Student Render',
                    apellidos='Test Apellidos',
                    email='test@render.com',
                    grupo_principal=existing_group
                )
                print(f"   ✅ Creación de estudiante exitosa: ID {test_student.id}")
                
                # Probar eliminación de estudiante
                test_student.delete()
                print(f"   ✅ Eliminación de estudiante exitosa")
            else:
                print("   ⚠️  No hay grupos disponibles para probar estudiante")
                
        except Exception as e:
            print(f"   ❌ Error en operaciones de estudiante: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎉 DIAGNÓSTICO DE RENDER COMPLETADO")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN DIAGNÓSTICO DE RENDER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar_render_500()
