from app.core.database import SessionLocal
from app.models.subject import Subject
from app.models.group import Group

db = SessionLocal()

print("\n=== VERIFICACIÓN DE ASIGNATURAS ===")
subjects = db.query(Subject).all()
print(f"Total asignaturas: {len(subjects)}")
for subject in subjects:
    print(f"  - ID: {subject.id}, Nombre: {subject.name}, Color: {subject.color}")
    if subject.schedules:
        print(f"    Horarios: {len(subject.schedules)}")
        for schedule in subject.schedules:
            print(f"      {schedule.day_of_week}: {schedule.start_time} - {schedule.end_time}")

print("\n=== VERIFICACIÓN DE GRUPOS ===")
groups = db.query(Group).all()
print(f"Total grupos: {len(groups)}")
for group in groups:
    print(f"  - ID: {group.id}, Nombre: {group.name}")
    print(f"    Estudiantes: {len(group.students) if group.students else 0}")
    print(f"    Asignaturas: {len(group.subjects) if group.subjects else 0}")

db.close()
