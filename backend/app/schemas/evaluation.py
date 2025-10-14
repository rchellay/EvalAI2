# app/schemas/evaluation.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class EvaluationBase(BaseModel):
    student_id: int
    subject_id: int
    title: str
    evaluation_type: Optional[str] = None
    grade: Optional[float] = None
    max_grade: float = 10.0
    mood: Optional[str] = None
    date: date
    notes: Optional[str] = None

class EvaluationCreate(BaseModel):
    subject_id: int
    title: str
    evaluation_type: Optional[str] = "exam"
    grade: Optional[float] = None
    max_grade: float = 10.0
    mood: Optional[str] = "neutral"
    date: date
    notes: Optional[str] = None

class EvaluationUpdate(BaseModel):
    title: Optional[str] = None
    grade: Optional[float] = None
    mood: Optional[str] = None
    notes: Optional[str] = None

class EvaluationResponse(EvaluationBase):
    id: int
    recorded_by: int
    subject_name: Optional[str] = None
    percentage: Optional[float] = None
    
    class Config:
        from_attributes = True

class SubjectAverageResponse(BaseModel):
    subject_id: int
    subject_name: str
    average_grade: float
    evaluation_count: int
    
    class Config:
        from_attributes = True
