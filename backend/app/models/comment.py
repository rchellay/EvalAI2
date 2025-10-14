# app/models/comment.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Comment(Base):
    """Comentarios sobre estudiantes"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), default="general")  # general, behavior, academic, progress
    is_voice_transcription = Column(Boolean, default=False)
    
    # Quién creó el comentario
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    # student = relationship("User", foreign_keys=[student_id], back_populates="comments_received")
    # author = relationship("User", foreign_keys=[created_by], back_populates="comments_created")
    subject = relationship("Subject")
