"""
Script para verificar configuración de Cloudinary
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from decouple import config

print("=" * 70)
print("🔍 VERIFICANDO: Configuración de Cloudinary")
print("=" * 70)

# Verificar variables de entorno
print("\n📋 Variables de entorno:")
use_cloudinary = config('USE_CLOUDINARY', default='False')
cloud_name = config('CLOUDINARY_CLOUD_NAME', default='')
api_key = config('CLOUDINARY_API_KEY', default='')
api_secret = config('CLOUDINARY_API_SECRET', default='')

print(f"   USE_CLOUDINARY: {use_cloudinary}")
print(f"   CLOUDINARY_CLOUD_NAME: {cloud_name[:20]}..." if cloud_name else "   CLOUDINARY_CLOUD_NAME: (vacío)")
print(f"   CLOUDINARY_API_KEY: {api_key[:10]}..." if api_key else "   CLOUDINARY_API_KEY: (vacío)")
print(f"   CLOUDINARY_API_SECRET: {'*' * 10}..." if api_secret else "   CLOUDINARY_API_SECRET: (vacío)")

# Verificar configuración en settings
if hasattr(settings, 'CLOUDINARY_STORAGE'):
    print(f"\n✅ CLOUDINARY_STORAGE configurado en settings.py")
    print(f"   Cloud Name: {settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'N/A')}")
else:
    print(f"\n❌ CLOUDINARY_STORAGE NO configurado en settings.py")

# Intentar importar cloudinary
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    print(f"\n✅ Módulo cloudinary importado correctamente")
    
    # Intentar configurar
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret
    )
    print(f"✅ Cloudinary configurado con las credenciales")
    
    # Verificar conexión haciendo un ping
    try:
        result = cloudinary.api.ping()
        print(f"✅ Conexión exitosa a Cloudinary!")
        print(f"   Status: {result.get('status', 'OK')}")
    except Exception as e:
        print(f"❌ Error conectando a Cloudinary: {e}")
        
except ImportError as e:
    print(f"\n❌ Error importando cloudinary: {e}")
    print(f"   Instala con: pip install cloudinary django-cloudinary-storage")

print("\n" + "=" * 70)
