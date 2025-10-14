# app/schemas/subject.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import time
from app.models.subject import DayOfWeek


class SubjectScheduleBase(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time


class SubjectScheduleCreate(SubjectScheduleBase):
    pass


class SubjectScheduleResponse(SubjectScheduleBase):
    id: int
    subject_id: int

    class Config:
        from_attributes = True


class SubjectBase(BaseModel):
    name: str
    color: Optional[str] = "#137fec"
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    group_ids: Optional[List[int]] = []
    schedules: Optional[List[SubjectScheduleCreate]] = []


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    group_ids: Optional[List[int]] = None
    schedules: Optional[List[SubjectScheduleCreate]] = None


class SubjectResponse(SubjectBase):
    id: int
    teacher_id: int
    schedules: List[SubjectScheduleResponse]
    group_count: Optional[int] = 0
    student_count: Optional[int] = 0

    class Config:
        from_attributes = True


class SubjectDetailResponse(SubjectResponse):
    """Response with full group and student details"""
    groups: List[dict] = []  # Will be populated manually

    class Config:
        from_attributes = True
