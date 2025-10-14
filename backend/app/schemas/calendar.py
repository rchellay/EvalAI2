# app/schemas/calendar.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Subject Schemas
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#3b86e3", pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None

class SubjectOut(SubjectBase):
    id: int
    
    class Config:
        from_attributes = True

# Calendar Event Schemas
class CalendarEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_at: datetime
    end_at: Optional[datetime] = None
    all_day: bool = False
    recurrence_rule: Optional[str] = Field(None, max_length=1000, description="iCal RRULE format")
    timezone: str = Field(default="UTC", max_length=64)
    event_type: Optional[str] = Field(None, max_length=50)
    subject_id: Optional[int] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

class CalendarEventCreate(CalendarEventBase):
    """Schema for creating a new calendar event"""
    pass

class CalendarEventUpdate(BaseModel):
    """Schema for updating an existing calendar event (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    all_day: Optional[bool] = None
    recurrence_rule: Optional[str] = Field(None, max_length=1000)
    timezone: Optional[str] = Field(None, max_length=64)
    event_type: Optional[str] = Field(None, max_length=50)
    subject_id: Optional[int] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

class CalendarEventOut(CalendarEventBase):
    """Schema for returning calendar event data"""
    id: int
    created_by: int
    parent_id: Optional[int] = None
    is_exception: bool
    exception_original_start: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CalendarEventWithSubject(CalendarEventOut):
    """Extended schema including subject details"""
    subject: Optional[SubjectOut] = None

# Schema for occurrence-specific operations (editing/deleting a single occurrence)
class OccurrenceEdit(BaseModel):
    """Schema for editing a single occurrence of a recurring event"""
    occurrence_start: datetime = Field(..., description="Original start datetime of the occurrence being edited")
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    event_type: Optional[str] = None
    subject_id: Optional[int] = None
    color: Optional[str] = None

# Query parameters schema
class EventsQueryParams(BaseModel):
    start: datetime
    end: datetime
    subject_id: Optional[int] = None
    event_types: Optional[str] = None  # Comma-separated list
    include_recurring: bool = True

# ICS Import result
class ICSImportResult(BaseModel):
    imported_count: int
    skipped_count: int
    errors: list[str] = []
