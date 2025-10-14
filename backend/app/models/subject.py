# app/models/subject.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

# Enum para los días de la semana
class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

# Tabla de asociación entre asignaturas y grupos
subject_groups = Table(
    'subject_groups',
    Base.metadata,
    Column('subject_id', Integer, ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
)

class Subject(Base):
    """Subject/Asignatura model with schedules and group associations"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), default="#137fec")  # Color para el calendario
    description = Column(Text, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    # Relaciones
    teacher = relationship("User", back_populates="subjects_taught")
    schedules = relationship("SubjectSchedule", back_populates="subject", cascade="all, delete-orphan")
    groups = relationship("Group", secondary=subject_groups, back_populates="subjects")
    attendances = relationship("Attendance", back_populates="subject")
    evaluations = relationship("Evaluation", back_populates="subject")
    
    def __repr__(self):
        return f"<Subject {self.name}>"


class SubjectSchedule(Base):
    """Modelo de Horario de Asignatura (recurrente semanal)"""
    __tablename__ = "subject_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=False)  # Lunes, Martes, etc.
    start_time = Column(Time, nullable=False)  # Ej: 11:00
    end_time = Column(Time, nullable=False)  # Ej: 12:00
    description = Column(Text, nullable=True)  # Descripción opcional del horario
    
    # Relaciones
    subject = relationship("Subject", back_populates="schedules")
    
    def __repr__(self):
        return f"<Schedule {self.day_of_week.value} {self.start_time}-{self.end_time}>"
