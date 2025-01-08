# backend/app/models/__init__.py
from .base import Base, engine, create_enum_type
from .user import User, UserRole
from .course import Course
from .progress import UserProgress
from .analytics import AnalyticsData

# Create all tables
def init_db():
    """
    Initialize database:
    1. Create enum types
    2. Create all tables
    """
    # Create enum types first
    create_enum_type(UserRole)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)