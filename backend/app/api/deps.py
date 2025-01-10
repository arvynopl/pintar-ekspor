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
from ..core.security import verify_token, api_key_manager, oauth2_scheme, api_key_header

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Validate access token and retrieve the current user
    """
    if not token:
        return None
    try:
        payload = verify_token(token)
        email = payload.get("sub")
        if email:
            return db.query(User).filter(User.email == email).first()
    except Exception:
        return None
    return None

async def get_api_key_user(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Validate API key from header or query parameter
    
    Args:
        api_key (str, optional): API key from header
        db (Session): Database session
    
    Returns:
        Optional[User]: User with matching API key or None
    
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        return None
    return await api_key_manager.validate_api_key(api_key, db)

async def get_authenticated_user(
    db: Session = Depends(get_db),
    jwt_user: Optional[User] = Depends(get_current_user),
    api_key_user: Optional[User] = Depends(get_api_key_user)
) -> User:
    """Combined authentication"""
    user = jwt_user or api_key_user
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: either JWT token or API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

# Role-based authentication functions
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
        current_user: User = Depends(get_authenticated_user)
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
get_current_developer = get_user_with_role([UserRole.DEVELOPER, UserRole.ADMIN])
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