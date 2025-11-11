"""
Script para corregir la ruta duplicada del avatar de Clara
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("🔧 CORRIGIENDO: Ruta del avatar de Clara")
print("=" * 70)

# Buscar usuario Clara
try:
    clara = User.objects.get(username='clara')
    print(f"✅ Usuario encontrado: {clara.username}")
    
    if hasattr(clara, 'profile') and clara.profile.avatar:
        profile = clara.profile
        old_path = profile.avatar.name
        print(f"\n📌 Ruta actual: {old_path}")
        
        # Si la ruta tiene "media/avatars/" al inicio, quitarlo
        if old_path.startswith('media/avatars/'):
            new_path = old_path.replace('media/avatars/', 'avatars/', 1)
            print(f"🔄 Nueva ruta: {new_path}")
            
            # Actualizar el campo
            profile.avatar.name = new_path
            profile.save()
            
            print(f"\n✅ ¡Avatar corregido!")
            print(f"   Ruta anterior: {old_path}")
            print(f"   Ruta nueva: {new_path}")
            print(f"   URL: {profile.avatar.url}")
        else:
            print(f"\n⚠️ La ruta no tiene el prefijo 'media/avatars/', no se necesita corrección")
            print(f"   Ruta actual: {old_path}")
    else:
        print(f"\n❌ Clara no tiene avatar configurado")
        
except User.DoesNotExist:
    print("❌ No se encontró el usuario 'clara'")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
