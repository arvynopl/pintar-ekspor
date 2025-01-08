# backend/app/schemas/analytics.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AnalyticsDataBase(BaseModel):
    data_type: str
    data: Dict[str, Any]
    user_id: Optional[int] = None
    course_id: Optional[int] = None

class AnalyticsDataCreate(AnalyticsDataBase):
    pass

class AnalyticsData(AnalyticsDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True