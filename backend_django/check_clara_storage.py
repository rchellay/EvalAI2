"""
Script para ver toda la info del avatar de Clara
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("🔍 INFO COMPLETA: Avatar de Clara")
print("=" * 70)

try:
    clara = User.objects.get(username='clara')
    
    if hasattr(clara, 'profile') and clara.profile.avatar:
        profile = clara.profile
        
        print(f"👤 Usuario: {clara.username}")
        print(f"\n📄 Campo avatar:")
        print(f"   .name: {profile.avatar.name}")
        print(f"   .url: {profile.avatar.url}")
        
        # Verificar el storage backend
        print(f"\n💾 Storage:")
        print(f"   Type: {type(profile.avatar.storage).__name__}")
        print(f"   Class: {profile.avatar.storage.__class__.__module__}.{profile.avatar.storage.__class__.__name__}")
        
        # Si es Cloudinary
        if 'cloudinary' in str(type(profile.avatar.storage)).lower():
            print(f"   ☁️ Usando Cloudinary Storage")
            # Intentar obtener la URL pública de Cloudinary
            try:
                from cloudinary import CloudinaryImage
                public_id = profile.avatar.name
                print(f"   Public ID: {public_id}")
                # Generar URL de Cloudinary
                img = CloudinaryImage(public_id)
                cloudinary_url = img.build_url()
                print(f"   ✅ URL de Cloudinary: {cloudinary_url}")
            except Exception as e:
                print(f"   ⚠️ Error obteniendo URL de Cloudinary: {e}")
        else:
            print(f"   📁 Usando FileSystem Storage local")
            
            # Verificar si existe el archivo
            if profile.avatar.storage.exists(profile.avatar.name):
                print(f"   ✅ Archivo existe en storage")
                print(f"   Path: {profile.avatar.path if hasattr(profile.avatar, 'path') else 'N/A'}")
            else:
                print(f"   ❌ Archivo NO existe en storage")
                print(f"   Expected path: {profile.avatar.path if hasattr(profile.avatar, 'path') else 'N/A'}")
                
    else:
        print(f"❌ Clara no tiene avatar configurado")
        
except User.DoesNotExist:
    print("❌ No se encontró el usuario 'clara'")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
