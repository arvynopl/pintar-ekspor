# backend/scripts/init_db.py
import asyncio
import sys
sys.path.append("..")  # Add parent directory to Python path

from app.core.config import settings
from app.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.user import User
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
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Creating default admin user...")
        # Create default admin user
        admin_data = {
            "email": "admin@pintarexpor.com",
            "hashed_password": get_password_hash("admin123"),  # Change this in production!
            "is_active": True,
            "is_superuser": True,
            "role": "admin"
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