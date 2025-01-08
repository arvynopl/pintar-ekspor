# backend/app/models/user.py
from sqlalchemy import Integer, Column, String, DateTime
from sqlalchemy.sql import func
import enum
from .base import Base

class UserRole(str, enum.Enum):
    """
    User role enumeration with explicit string values
    
    Defines roles for access control and system permissions:
    - PUBLIC: Standard registered user
    - DEVELOPER: User with API access
    - ADMIN: System administrator with full permissions
    """
    PUBLIC = "public"
    DEVELOPER = "developer"
    ADMIN = "admin"

class User(Base):
    """
    User model representing system users with role-based access control
    
    Attributes:
        id (int): Unique user identifier
        email (str): User's email address (unique)
        hashed_password (str): Securely hashed user password
        role (UserRole): User's role in the system
        api_key (str, optional): Developer API key
        refresh_token (str, optional): Current refresh token
        last_login (datetime, optional): Timestamp of last user login
        created_at (datetime): User registration timestamp
        updated_at (datetime, optional): Last user profile update timestamp
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default=UserRole.PUBLIC.value)
    api_key = Column(String, unique=True, nullable=True)
    refresh_token = Column(String, unique=True, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def is_admin(self) -> bool:
        """
        Check if user has admin role
        
        Returns:
            bool: True if user is an admin, False otherwise
        """
        return self.role == UserRole.ADMIN.value

    @property
    def is_developer(self) -> bool:
        """
        Check if user has developer role
        
        Returns:
            bool: True if user is a developer, False otherwise
        """
        return self.role == UserRole.DEVELOPER.value

    def __repr__(self) -> str:
        """
        String representation of the User model
        
        Returns:
            str: User details for logging and debugging
        """
        return (
            f"<User(id={self.id}, email='{self.email}', "
            f"role='{self.role}', last_login='{self.last_login}')>"
        )