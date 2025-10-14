import os, sys, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Student, Subject, Group
from datetime import time

print("Creando datos de prueba...")

admin = User.objects.filter(username="admin").first()
if not admin:
    admin = User.objects.create_superuser("admin", "admin@example.com", "admin123")
    print("Admin creado")

# Asignaturas
subjects_data = [
    {"name": "Matematicas", "days": ["monday", "wednesday", "friday"], "start_time": time(9, 0), "end_time": time(10, 30), "color": "#3B82F6"},
    {"name": "Lengua Española", "days": ["tuesday", "thursday"], "start_time": time(10, 45), "end_time": time(12, 15), "color": "#EF4444"},
    {"name": "Ciencias Naturales", "days": ["monday", "friday"], "start_time": time(12, 30), "end_time": time(14, 0), "color": "#10B981"},
    {"name": "Historia", "days": ["tuesday"], "start_time": time(9, 0), "end_time": time(10, 30), "color": "#F59E0B"},
    {"name": "Educacion Fisica", "days": ["wednesday"], "start_time": time(14, 15), "end_time": time(15, 45), "color": "#8B5CF6"},
]

created_subjects = []
for data in subjects_data:
    subj, created = Subject.objects.get_or_create(name=data["name"], defaults={**data, "teacher": admin})
    created_subjects.append(subj)
    print(f"Asignatura: {subj.name}")

# Grupos
groups_data = ["1º A", "1º B", "2º A"]
created_groups = []
for group_name in groups_data:
    grp, created = Group.objects.get_or_create(name=group_name)
    # Asignar asignaturas al grupo
    if created:
        grp.subjects.set(created_subjects[:3])
    created_groups.append(grp)
    print(f"Grupo: {grp.name}")

# Estudiantes
students_data = [
    {"name": "Juan García López", "email": "juan.garcia@example.com", "course": "1º ESO"},
    {"name": "María Rodríguez Pérez", "email": "maria.rodriguez@example.com", "course": "1º ESO"},
    {"name": "Carlos Martínez Sánchez", "email": "carlos.martinez@example.com", "course": "1º ESO"},
    {"name": "Ana López Fernández", "email": "ana.lopez@example.com", "course": "1º ESO"},
    {"name": "Pedro González Ruiz", "email": "pedro.gonzalez@example.com", "course": "2º ESO"},
    {"name": "Laura Hernández Torres", "email": "laura.hernandez@example.com", "course": "2º ESO"},
    {"name": "Diego Jiménez Moreno", "email": "diego.jimenez@example.com", "course": "2º ESO"},
]

for i, data in enumerate(students_data):
    group = created_groups[i % len(created_groups)]
    std, created = Student.objects.get_or_create(email=data["email"], defaults=data)
    # Asociar estudiante con grupo
    group.students.add(std)
    print(f"Estudiante: {std.name} (Grupo: {group.name})")

print("Datos creados exitosamente!")
print(f"Total Asignaturas: {Subject.objects.count()}")
print(f"Total Grupos: {Group.objects.count()}")
print(f"Total Estudiantes: {Student.objects.count()}")