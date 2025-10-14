from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from app.core.database import Base

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    content = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    subject = Column(String, nullable=True)
    processed = Column(Boolean, default=False)
