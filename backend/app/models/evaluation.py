# app/models/evaluation.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Evaluation(Base):
    """Evaluaciones/Notas de estudiantes por asignatura"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)  # Ej: "Examen Parcial 1"
    evaluation_type = Column(String(50), nullable=True)  # exam, quiz, homework, project, etc.
    grade = Column(Float, nullable=True)  # Nota numérica (ej: 8.5)
    max_grade = Column(Float, default=10.0)  # Nota máxima posible
    
    # Estado emocional del estudiante durante la evaluación
    mood = Column(String(50), nullable=True)  # confident, satisfied, neutral, anxious, etc.
    
    date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # Quién registró la evaluación
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    student = relationship("User", foreign_keys=[student_id], back_populates="evaluations")
    subject = relationship("Subject")
    recorder = relationship("User", foreign_keys=[recorded_by])
    
    def __repr__(self):
        return f"<Evaluation {self.student_id} - {self.title} - {self.grade}>"
