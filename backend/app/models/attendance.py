# app/models/attendance.py
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

class Attendance(Base):
    """Registro de asistencia de estudiantes"""
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default=AttendanceStatus.PRESENT.value)
    notes = Column(Text, nullable=True)
    
    # Quién registró la asistencia
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    student = relationship("User", foreign_keys=[student_id], back_populates="attendances")
    subject = relationship("Subject")
    recorder = relationship("User", foreign_keys=[recorded_by])
    
    def __repr__(self):
        return f"<Attendance {self.student_id} - {self.date} - {self.status}>"
