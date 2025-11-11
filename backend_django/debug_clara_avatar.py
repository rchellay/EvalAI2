"""
Script para diagnosticar el avatar de Clara
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student
from core.serializers import StudentSerializer

print("=" * 70)
print("🔍 DIAGNÓSTICO: Avatar de Clara")
print("=" * 70)

# Buscar estudiante Clara
claras = Student.objects.filter(name__icontains='clara')

if not claras.exists():
    print("❌ No se encontró ningún estudiante con nombre 'Clara'")
    print("\n📋 Todos los estudiantes en la base de datos:")
    for student in Student.objects.all()[:10]:
        print(f"  - ID: {student.id} | Nombre: {student.name} | Email: {student.email}")
else:
    print(f"✅ Se encontraron {claras.count()} estudiante(s) con nombre 'Clara'\n")
    
    for clara in claras:
        print("-" * 70)
        print(f"📌 Estudiante ID: {clara.id}")
        print(f"   Nombre completo: {clara.full_name}")
        print(f"   Email: {clara.email}")
        print(f"   Photo field: {clara.photo}")
        print(f"   Avatar Type: {clara.avatar_type}")
        print(f"   Avatar Value length: {len(clara.avatar_value) if clara.avatar_value else 0} caracteres")
        
        if clara.avatar_value:
            preview = clara.avatar_value[:100] + "..." if len(clara.avatar_value) > 100 else clara.avatar_value
            print(f"   Avatar Value preview: {preview}")
        else:
            print(f"   Avatar Value: (vacío)")
        
        print("\n📊 Datos serializados (como los ve el frontend):")
        serializer = StudentSerializer(clara)
        data = serializer.data
        print(f"   avatar_type: {data.get('avatar_type')}")
        print(f"   avatar_value: {data.get('avatar_value')[:100] if data.get('avatar_value') else '(vacío)'}")
        
        # Verificar si avatar_value es una URL o base64
        if clara.avatar_value:
            if clara.avatar_value.startswith('http'):
                print(f"\n   ✅ Avatar Value es una URL: {clara.avatar_value}")
            elif clara.avatar_value.startswith('data:image'):
                print(f"\n   ✅ Avatar Value es base64 (data:image...)")
            else:
                print(f"\n   ⚠️ Avatar Value no parece ser URL ni base64")

print("\n" + "=" * 70)
