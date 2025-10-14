from sqlalchemy.orm import Session
from app.models import Student

SAMPLE_STUDENTS = [
    {"name": "Sehaj"},
    {"name": "Jesmeen"},
]

def seed_students(db: Session):
    if db.query(Student).count() == 0:
        for data in SAMPLE_STUDENTS:
            db.add(Student(**data))
        db.commit()

def list_students(db: Session):
    return db.query(Student).order_by(Student.id).all()
