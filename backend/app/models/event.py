from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_type = Column(String, nullable=False)  # exam, meeting, holiday, etc.
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    all_day = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    color = Column(String, default="#3b86e3")
    created_at = Column(DateTime, server_default=func.now())
