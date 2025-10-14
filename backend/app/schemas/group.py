# app/schemas/group.py
from pydantic import BaseModel
from typing import List, Optional


class GroupBase(BaseModel):
    name: str
    color: Optional[str] = "#4caf50"


class GroupCreate(GroupBase):
    student_ids: Optional[List[int]] = []


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    student_ids: Optional[List[int]] = None


class GroupResponse(GroupBase):
    id: int
    teacher_id: int
    student_count: Optional[int] = 0
    subject_count: Optional[int] = 0

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    """Response with full student and subject details"""
    students: List[dict] = []  # Will be populated manually
    subjects: List[dict] = []  # Will be populated manually

    class Config:
        from_attributes = True


class GroupAddStudentsRequest(BaseModel):
    student_ids: List[int]


class GroupRemoveStudentsRequest(BaseModel):
    student_ids: List[int]
