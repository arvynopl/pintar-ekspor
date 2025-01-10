# backend/scripts/create_admin.py
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to Python path to make app module accessible
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.models.base import Base  # Add this import

# Using the same database URL as in docker-compose.yml
DATABASE_URL = "postgresql://expor_user:AKUADALAHSANGPEMILIKD13!@db:5432/pintar_ekspor"

def create_admin(email: str, password: str):
    engine = create_engine(DATABASE_URL)
    
    # Create all tables before proceeding
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        admin_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        print(f"Admin user {email} created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    ADMIN_EMAIL = "admin@pintarekspor.com"
    ADMIN_PASSWORD = "AKUADALAHSANG4DMIN!"
    
    create_admin(ADMIN_EMAIL, ADMIN_PASSWORD)