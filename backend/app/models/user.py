from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Relaciones
    subjects_taught = relationship("Subject", back_populates="teacher")
    groups_managed = relationship("Group", foreign_keys="Group.teacher_id", back_populates="teacher")
    groups_enrolled = relationship("Group", secondary="group_students", back_populates="students")
    attendances = relationship("Attendance", foreign_keys="Attendance.student_id", back_populates="student")
    evaluations = relationship("Evaluation", foreign_keys="Evaluation.student_id", back_populates="student")
    # comments_received = relationship("Comment", foreign_keys="Comment.student_id", back_populates="student")
    # comments_created = relationship("Comment", foreign_keys="Comment.created_by", back_populates="author")
