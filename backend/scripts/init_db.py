# backend/scripts/init_db.py
import asyncio
import sys
sys.path.append("..")

from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.analytics import AnalyticsData
from app.models.progress import UserProgress
from app.core.security import get_password_hash
from loguru import logger

async def init_db():
    """Initialize the database with required tables and initial data."""
    try:
        # Create async engine
        engine = create_async_engine(
            settings.ASYNC_DATABASE_URL,
            echo=True
        )

        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Creating default admin user...")
        # Create default admin user
        admin_data = {
            "email": "admin@pintarekspor.com",
            "hashed_password": get_password_hash("AKUADALAHSANG4DMIN!"),
            "role": UserRole.ADMIN.value,
            "refresh_token": None,
            "api_key": None,
            "last_login": None
        }

        async with engine.begin() as conn:
            await conn.execute(
                User.__table__.insert(),
                [admin_data]
            )

        logger.info("Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())