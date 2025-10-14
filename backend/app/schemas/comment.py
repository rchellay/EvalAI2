# app/schemas/comment.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    content: str
    comment_type: Optional[str] = "general"  # general, behavior, academic, progress
    is_voice_transcription: bool = False

class CommentCreate(BaseModel):
    subject_id: Optional[int] = None
    content: str
    comment_type: Optional[str] = "general"
    is_voice_transcription: bool = False

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    comment_type: Optional[str] = None

class CommentResponse(BaseModel):
    id: int
    student_id: int
    subject_id: Optional[int] = None
    content: str
    comment_type: str
    is_voice_transcription: bool
    created_by: int
    created_at: datetime
    author_name: Optional[str] = None
    student_username: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True
