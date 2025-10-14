# app/schemas/attendance.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class AttendanceBase(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    date: date
    status: str  # present, absent, late, excused
    notes: Optional[str] = None

class AttendanceCreate(BaseModel):
    subject_id: Optional[int] = None
    date: date
    status: str
    notes: Optional[str] = None

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int
    recorded_by: int
    subject_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class AttendanceStatsResponse(BaseModel):
    total_days: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_percentage: float
    
    class Config:
        from_attributes = True
