# backend/app/schemas/progress.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserProgressBase(BaseModel):
    user_id: int
    course_id: int
    completed: bool = False

class UserProgressCreate(UserProgressBase):
    pass

class UserProgress(UserProgressBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True