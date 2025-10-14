# app/models/group.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# Tabla de asociación entre grupos y estudiantes
group_students = Table(
    'group_students',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
    Column('student_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

class Group(Base):
    """Modelo de Grupo de estudiantes"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Ej: "6A", "Grupo de Refuerzo"
    color = Column(String(20), default="#4caf50")  # Color identificativo
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    # Relaciones
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="groups_managed")
    students = relationship("User", secondary=group_students, back_populates="groups_enrolled")
    subjects = relationship("Subject", secondary="subject_groups", back_populates="groups")
    
    def __repr__(self):
        return f"<Group {self.name}>"
