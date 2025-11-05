#!/usr/bin/env python3
"""
Script directo para debuggear el problema de estudiantes
Ejecutar con: python debug_direct.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from core.models import Group, Student
from django.contrib.auth.models import User

def debug_students_issue():
    print("=== DEBUG DIRECTO ===")
    
    # 1. Verificar que existe el grupo 10
    try:
        group = Group.objects.get(id=10)
        print(f"✅ Grupo encontrado: {group.name} (ID: {group.id})")
        print(f"   Teacher: {group.teacher.username}")
        print(f"   Course: {group.course}")
    except Group.DoesNotExist:
        print("❌ ERROR: Grupo 10 no existe")
        print("Grupos disponibles:")
        for g in Group.objects.all():
            print(f"   - {g.id}: {g.name} (teacher: {g.teacher.username})")
        return
    
    # 2. Contar estudiantes en el grupo
    students_in_group = Student.objects.filter(grupo_principal=group)
    print(f"\n📊 Estudiantes en grupo {group.name}: {students_in_group.count()}")
    
    for student in students_in_group:
        print(f"   - {student.name} {student.apellidos} ({student.email}) ID: {student.id}")
    
    # 3. Crear un estudiante de prueba
    print(f"\n🔧 Creando estudiante de prueba...")
    try:
        test_student = Student.objects.create(
            name="TEST_DEBUG",
            apellidos="APELLIDO_TEST", 
            email=f"test_debug_{group.id}@example.com",
            grupo_principal=group
        )
        print(f"✅ Estudiante creado: {test_student.full_name} (ID: {test_student.id})")
        print(f"   Su grupo_principal: {test_student.grupo_principal.id if test_student.grupo_principal else 'None'}")
        
        # Verificar que ahora aparece en la consulta
        students_after = Student.objects.filter(grupo_principal=group)
        print(f"📊 Estudiantes después de crear: {students_after.count()}")
        
        # Eliminar el estudiante de prueba
        test_student.delete()
        print("🗑️ Estudiante de prueba eliminado")
        
    except Exception as e:
        print(f"❌ Error creando estudiante: {e}")
    
    # 4. Verificar todos los estudiantes en la DB
    print(f"\n📋 TODOS los estudiantes en la DB:")
    all_students = Student.objects.all()
    print(f"Total estudiantes: {all_students.count()}")
    
    for student in all_students:
        grupo_name = student.grupo_principal.name if student.grupo_principal else "Sin grupo"
        grupo_id = student.grupo_principal.id if student.grupo_principal else "None"
        print(f"   - {student.name} {student.apellidos} → Grupo: {grupo_name} (ID: {grupo_id})")

if __name__ == "__main__":
    debug_students_issue()