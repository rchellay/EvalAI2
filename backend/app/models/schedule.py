from sqlalchemy import Column, Integer, String, DateTime, Time
from app.core.database import Base

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    subject = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    classroom = Column(String, nullable=True)
    teacher = Column(String, nullable=True)
    color = Column(String, default="#3b86e3")
