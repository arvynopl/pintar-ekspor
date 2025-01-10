# backend/app/models/__init__.py
from .base import Base, engine, create_enum_type
from .user import User, UserRole
from .course import Course
from .progress import UserProgress
from .analytics import AnalyticsData
from ..core.audit import AuditBase, AuditLog

def init_db():
    """
    Initialize database:
    1. Create enum types
    2. Create all tables (including audit tables)
    3. Handle initialization errors
    """
    try:
        # Create enum types first
        create_enum_type(UserRole)
        
        # Create audit tables
        AuditBase.metadata.create_all(bind=engine)
        
        # Create all other tables
        Base.metadata.create_all(bind=engine)
        
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        raise