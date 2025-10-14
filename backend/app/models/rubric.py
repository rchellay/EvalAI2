from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base

class Rubric(Base):
    __tablename__ = "rubrics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    criteria = Column(String, nullable=True)  # JSON string of criteria
    applied = Column(Boolean, default=False)
