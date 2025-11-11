"""
Script para limpiar el avatar roto de Clara (opción temporal)
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("🧹 LIMPIANDO: Avatar roto de Clara")
print("=" * 70)

try:
    clara = User.objects.get(username='clara')
    
    if hasattr(clara, 'profile') and clara.profile.avatar:
        profile = clara.profile
        old_avatar = profile.avatar.name
        
        # Limpiar el campo avatar
        profile.avatar = None
        profile.save()
        
        print(f"✅ Avatar limpiado")
        print(f"   Avatar anterior: {old_avatar}")
        print(f"   Avatar actual: {profile.avatar}")
        print(f"\n💡 Ahora Clara verá su inicial 'C' hasta que subas un nuevo avatar")
        
    else:
        print(f"⚠️ Clara ya no tiene avatar configurado")
        
except User.DoesNotExist:
    print("❌ No se encontró el usuario 'clara'")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
