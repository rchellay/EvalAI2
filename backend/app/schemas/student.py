from pydantic import BaseModel
from datetime import datetime

class StudentOut(BaseModel):
    id: int
    name: str
    created_at: datetime | None = None

    class Config:
        orm_mode = True
