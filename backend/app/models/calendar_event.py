# app/models/calendar_event.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class CalendarEvent(Base):
    """
    Calendar Event model with full recurrence support.
    Supports single events, recurring events (RRULE), and exceptions to recurring series.
    """
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps (always stored in UTC)
    start_at = Column(DateTime(timezone=True), nullable=False, index=True)
    end_at = Column(DateTime(timezone=True), nullable=True, index=True)
    all_day = Column(Boolean, default=False)
    
    # Recurrence support
    recurrence_rule = Column(String(1000), nullable=True)  # iCal RRULE format
    timezone = Column(String(64), default="UTC")  # Original timezone of event
    
    # Event categorization
    event_type = Column(String(50), index=True, nullable=True)  # exam, meeting, note, class, etc.
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    color = Column(String(20), nullable=True)  # Override subject color if needed
    
    # Ownership and exceptions
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)
    is_exception = Column(Boolean, default=False)  # True if this is an exception to a recurring event
    exception_original_start = Column(DateTime(timezone=True), nullable=True)  # Original start of the occurrence being modified
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subject = relationship("Subject", backref="events")
    creator = relationship("User", foreign_keys=[created_by], backref="created_events")
    parent = relationship("CalendarEvent", remote_side=[id], backref="exceptions")
    
    def __repr__(self):
        return f"<CalendarEvent {self.title} at {self.start_at}>"
