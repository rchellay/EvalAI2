"""
Script para diagnosticar el avatar del usuario Clara
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.serializers import UserSerializer
from rest_framework.test import APIRequestFactory

print("=" * 70)
print("🔍 DIAGNÓSTICO: Avatar del usuario Clara")
print("=" * 70)

# Buscar usuario Clara
claras = User.objects.filter(username__icontains='clara') | User.objects.filter(first_name__icontains='clara')

if not claras.exists():
    print("❌ No se encontró ningún usuario con nombre 'Clara'")
    print("\n📋 Primeros 10 usuarios en la base de datos:")
    for user in User.objects.all()[:10]:
        print(f"  - ID: {user.id} | Username: {user.username} | Email: {user.email} | Nombre: {user.get_full_name()}")
else:
    print(f"✅ Se encontraron {claras.count()} usuario(s) con nombre 'Clara'\n")
    
    for clara in claras:
        print("-" * 70)
        print(f"📌 Usuario ID: {clara.id}")
        print(f"   Username: {clara.username}")
        print(f"   Email: {clara.email}")
        print(f"   Nombre: {clara.get_full_name()}")
        
        # Verificar perfil
        if hasattr(clara, 'profile'):
            profile = clara.profile
            print(f"\n👤 Perfil encontrado:")
            print(f"   Display name: {profile.display_name}")
            print(f"   Gender: {profile.gender}")
            print(f"   Avatar field: {profile.avatar}")
            print(f"   Avatar name: {profile.avatar.name if profile.avatar else 'Sin avatar'}")
            
            if profile.avatar:
                print(f"   Avatar URL: {profile.avatar.url}")
                print(f"   Avatar path: {profile.avatar.path if hasattr(profile.avatar, 'path') else 'N/A'}")
                
                # Verificar si el archivo existe
                try:
                    if profile.avatar.storage.exists(profile.avatar.name):
                        print(f"   ✅ Archivo de avatar EXISTE en storage")
                    else:
                        print(f"   ❌ Archivo de avatar NO EXISTE en storage")
                except Exception as e:
                    print(f"   ⚠️ Error verificando archivo: {e}")
            else:
                print(f"   ⚠️ No tiene avatar configurado")
        else:
            print(f"\n❌ El usuario NO tiene perfil creado")
        
        # Ver datos serializados
        print(f"\n📊 Datos serializados (como los ve el frontend):")
        factory = APIRequestFactory()
        request = factory.get('/')
        serializer = UserSerializer(clara, context={'request': request})
        data = serializer.data
        
        print(f"   username: {data.get('username')}")
        print(f"   display_name: {data.get('display_name')}")
        print(f"   avatar_url: {data.get('avatar_url')}")
        print(f"   gender: {data.get('gender')}")

print("\n" + "=" * 70)
