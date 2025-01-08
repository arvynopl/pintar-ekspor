# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    """
    User role enumeration for schema validation
    
    Matches the model's UserRole definition to ensure consistency
    """
    PUBLIC = "public"
    DEVELOPER = "developer"
    ADMIN = "admin"

class UserBase(BaseModel):
    """
    Base user schema for common user attributes
    """
    email: EmailStr

class UserCreate(UserBase):
    """
    Schema for user creation request
    
    Validates password strength and format
    """
    password: str = Field(
        min_length=8, 
        description="Password must be at least 8 characters long",
        example="StrongP@ssw0rd!"
    )

    @validator('password')
    def validate_password(cls, password):
        """
        Validate password complexity
        
        Args:
            password (str): User's password
        
        Returns:
            str: Validated password
        
        Raises:
            ValueError: If password does not meet complexity requirements
        """
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            raise ValueError("Password must contain at least one special character")
        return password

class UserUpdate(BaseModel):
    """
    Schema for user profile updates
    """
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    """
    Schema for user response, excluding sensitive information
    """
    id: int
    role: UserRole
    created_at: datetime
    api_key: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """
    Authentication token schema
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """
    Token payload schema for validation
    """
    sub: str  # user email
    role: UserRole
    exp: datetime
    type: str  # 'access' or 'refresh'

class RefreshToken(BaseModel):
    """
    Refresh token request schema
    """
    refresh_token: str

class RoleUpgradeRequest(BaseModel):
    """
    Schema for role upgrade requests
    """
    email: EmailStr
    new_role: UserRole