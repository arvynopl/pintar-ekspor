# backend/app/models/analytics.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class AnalyticsData(Base):
    __tablename__ = "analytics_data"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String, index=True)  # e.g., 'course_view', 'completion'
    data = Column(JSON)  # Flexible JSON data storage
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())