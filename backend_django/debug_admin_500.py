#!/usr/bin/env python
"""
Script para diagnosticar errores 500 en Django Admin
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
from django.contrib.admin import ModelAdmin
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def diagnosticar_admin_500():
    """Diagnosticar problemas específicos del admin que causan error 500"""
    
    print("🔍 DIAGNÓSTICO ESPECÍFICO DE ERROR 500 EN ADMIN")
    print("=" * 60)
    
    try:
        # 1. Verificar configuración básica
        print("\n1. CONFIGURACIÓN BÁSICA:")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   DATABASE: {settings.DATABASES['default']['ENGINE']}")
        
        # 2. Verificar conexión a base de datos
        print("\n2. CONEXIÓN A BASE DE DATOS:")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("   ✅ Conexión a base de datos exitosa")
        
        # 3. Verificar modelos básicos
        print("\n3. MODELOS BÁSICOS:")
        User = get_user_model()
        print(f"   Usuarios: {User.objects.count()}")
        
        # 4. Verificar admin site
        print("\n4. ADMIN SITE:")
        from django.contrib.admin.sites import site
        print(f"   Admin site registrado: {site}")
        
        # 5. Verificar registros de admin
        print("\n5. REGISTROS DE ADMIN:")
        registered_models = []
        for model, admin_class in site._registry.items():
            registered_models.append(f"{model._meta.app_label}.{model._meta.model_name}")
        print(f"   Modelos registrados: {len(registered_models)}")
        for model in registered_models:
            print(f"     - {model}")
        
        # 6. Verificar permisos de usuario
        print("\n6. PERMISOS DE USUARIO:")
        superusers = User.objects.filter(is_superuser=True)
        print(f"   Superusuarios: {superusers.count()}")
        for user in superusers:
            print(f"     - {user.username} (ID: {user.id})")
        
        # 7. Probar acceso a admin específico
        print("\n7. PRUEBA DE ACCESO A ADMIN:")
        
        # Probar User admin
        try:
            from django.contrib.auth.admin import UserAdmin
            user_admin = UserAdmin(User, site)
            print("   ✅ UserAdmin cargado correctamente")
        except Exception as e:
            print(f"   ❌ Error en UserAdmin: {e}")
        
        # Probar nuestros admins
        try:
            from core.admin import GroupAdmin, StudentAdmin, SubjectAdmin
            print("   ✅ Admins personalizados cargados correctamente")
        except Exception as e:
            print(f"   ❌ Error en admins personalizados: {e}")
        
        # 8. Verificar estructura de tablas críticas
        print("\n8. ESTRUCTURA DE TABLAS CRÍTICAS:")
        with connection.cursor() as cursor:
            # Verificar tabla auth_user
            try:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                count = cursor.fetchone()[0]
                print(f"   ✅ auth_user: {count} registros")
            except Exception as e:
                print(f"   ❌ Error en auth_user: {e}")
            
            # Verificar tabla core_group
            try:
                cursor.execute("SELECT COUNT(*) FROM core_group")
                count = cursor.fetchone()[0]
                print(f"   ✅ core_group: {count} registros")
            except Exception as e:
                print(f"   ❌ Error en core_group: {e}")
            
            # Verificar tabla core_student
            try:
                cursor.execute("SELECT COUNT(*) FROM core_student")
                count = cursor.fetchone()[0]
                print(f"   ✅ core_student: {count} registros")
            except Exception as e:
                print(f"   ❌ Error en core_student: {e}")
            
            # Verificar tabla core_subject
            try:
                cursor.execute("SELECT COUNT(*) FROM core_subject")
                count = cursor.fetchone()[0]
                print(f"   ✅ core_subject: {count} registros")
            except Exception as e:
                print(f"   ❌ Error en core_subject: {e}")
        
        # 9. Probar operaciones específicas que pueden fallar
        print("\n9. PRUEBAS DE OPERACIONES ESPECÍFICAS:")
        
        # Probar creación de usuario
        try:
            test_user = User.objects.create_user(
                username='test_admin_500',
                email='test@example.com',
                password='testpass123'
            )
            test_user.is_superuser = True
            test_user.is_staff = True
            test_user.save()
            print("   ✅ Creación de usuario superuser exitosa")
            
            # Limpiar usuario de prueba
            test_user.delete()
            print("   ✅ Eliminación de usuario de prueba exitosa")
        except Exception as e:
            print(f"   ❌ Error en operaciones de usuario: {e}")
        
        # 10. Verificar middleware
        print("\n10. MIDDLEWARE:")
        middleware_classes = getattr(settings, 'MIDDLEWARE', [])
        print(f"   Middleware configurado: {len(middleware_classes)} clases")
        for middleware in middleware_classes:
            print(f"     - {middleware}")
        
        print("\n🎉 DIAGNÓSTICO COMPLETADO")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN DIAGNÓSTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar_admin_500()
