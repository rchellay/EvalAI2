"""
Script para depurar el problema del endpoint de grupos
"""
import sys
sys.path.append('backend')

from app.core.database import SessionLocal
from app.models.group import Group
from app.models.user import User

db = SessionLocal()

try:
    print("="*60)
    print("DEPURACIÓN DEL PROBLEMA DE GRUPOS")
    print("="*60)
    
    # Obtener grupo 11
    group_id = 11
    print(f"\n1. Consultando grupo {group_id}...")
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        print(f"❌ Grupo {group_id} no encontrado")
        exit(1)
    
    print(f"✅ Grupo encontrado: {group.name}")
    print(f"   ID: {group.id}")
    print(f"   Teacher ID: {group.teacher_id}")
    print(f"   Color: {group.color}")
    
    # Intentar acceder a students
    print(f"\n2. Accediendo a estudiantes...")
    try:
        students = group.students
        print(f"✅ {len(students)} estudiantes encontrados")
        if students:
            print(f"   Primer estudiante: {students[0].username} (ID: {students[0].id})")
            print(f"   Email: {students[0].email}")
    except Exception as e:
        print(f"❌ Error al acceder a estudiantes: {e}")
        import traceback
        traceback.print_exc()
    
    # Intentar acceder a subjects
    print(f"\n3. Accediendo a asignaturas...")
    try:
        subjects = group.subjects
        print(f"✅ {len(subjects)} asignaturas encontradas")
        if subjects:
            for subject in subjects[:3]:
                print(f"   - {subject.name} (ID: {subject.id})")
    except Exception as e:
        print(f"❌ Error al acceder a asignaturas: {e}")
        import traceback
        traceback.print_exc()
    
    # Simular lo que hace el endpoint
    print(f"\n4. Simulando construcción de respuesta...")
    try:
        students_list = [
            {
                "id": student.id,
                "username": student.username,
                "email": student.email
            }
            for student in group.students
        ]
        print(f"✅ Lista de estudiantes creada: {len(students_list)} elementos")
        
        subjects_list = [
            {
                "id": subject.id,
                "name": subject.name,
                "color": subject.color,
                "schedule_count": len(subject.schedules)
            }
            for subject in group.subjects
        ]
        print(f"✅ Lista de asignaturas creada: {len(subjects_list)} elementos")
        
    except Exception as e:
        print(f"❌ Error en construcción de respuesta: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Depuración completada")
    
except Exception as e:
    print(f"\n❌ Error general: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
