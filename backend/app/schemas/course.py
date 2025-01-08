# backend/app/schemas/course.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: str
    content: str

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None

class Course(CourseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True