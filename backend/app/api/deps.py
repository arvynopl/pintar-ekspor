# backend/app/api/deps.py
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    OAuth2PasswordBearer, 
    APIKeyHeader, 
    APIKeyQuery
)
from sqlalchemy.orm import Session
from typing import Union, Optional

from ..models.base import get_db
from ..models.user import User, UserRole
from ..core.security import verify_token

# OAuth2 token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# API key authentication methods
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Validate access token and retrieve the current user
    
    Args:
        token (str): JWT access token
        db (Session): Database session
    
    Returns:
        User: Authenticated user
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token and extract payload
        payload = verify_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    # Retrieve user from database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

async def get_api_key_user(
    api_key_header: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Validate API key from header or query parameter
    
    Args:
        api_key_header (str, optional): API key from header
        api_key_query (str, optional): API key from query parameter
        db (Session): Database session
    
    Returns:
        Optional[User]: User with matching API key or None
    
    Raises:
        HTTPException: If API key is invalid
    """
    # Prioritize header, then query parameter
    api_key = api_key_header
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Find user with matching API key and developer role
    user = db.query(User).filter(
        User.api_key == api_key,
        User.role == UserRole.DEVELOPER.value
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user

def get_user_with_role(required_roles: Union[UserRole, list[UserRole]]):
    """
    Create a dependency for role-based access control
    
    Args:
        required_roles (Union[UserRole, list[UserRole]]): 
            Single role or list of roles allowed to access the endpoint
    
    Returns:
        Callable: A dependency function for role verification
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Check if the current user has the required role
        
        Args:
            current_user (User): Currently authenticated user
        
        Returns:
            User: User if role is authorized
        
        Raises:
            HTTPException: If user lacks required role
        """
        # Convert single role to list for consistent checking
        if not isinstance(required_roles, list):
            roles_to_check = [required_roles]
        else:
            roles_to_check = required_roles
        
        # Check if user's role is in the allowed roles
        if current_user.role not in [role.value for role in roles_to_check]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return role_checker

# Predefined role checkers for common access scenarios
get_current_admin = get_user_with_role(UserRole.ADMIN)
get_current_developer = get_user_with_role(UserRole.DEVELOPER)
async def get_current_public_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Modified to work alongside API key auth"""
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            return None
            
        user = db.query(User).filter(User.email == email).first()
        return user
        
    except Exception:
        return None