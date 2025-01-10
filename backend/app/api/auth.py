# backend/app/api/auth.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import (
    APIRouter, Depends, HTTPException, status, Response, 
    Security, Request
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from ..core.config import get_settings
from ..core.security import (
    create_token_pair, verify_password, get_password_hash, 
    APIKeyManager, verify_token
)
from ..models.base import get_db
from ..models.user import User, UserRole
from ..schemas.user import (
    UserCreate, UserResponse, Token, RefreshToken,
    RoleUpgradeRequest, UserUpdate
)
from .deps import get_current_user, get_current_admin
from ..services.email.email_service import email_service

# Configure logging
logger = logging.getLogger(__name__)

# Router and dependencies setup
router = APIRouter()
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
api_key_manager = APIKeyManager()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve user by email with comprehensive error handling
    
    Args:
        db (Session): Database session
        email (str): User's email address
    
    Returns:
        Optional[User]: User object if found, None otherwise
    """
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error(f"Database error in get_user_by_email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query failed"
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate user credentials
    
    Args:
        db (Session): Database session
        email (str): User's email
        password (str): User's password
    
    Returns:
        Optional[User]: Authenticated user or None
    """
    try:
        user = get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication process failed"
        )

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Public user registration endpoint
    
    Args:
        user_data (UserCreate): User registration details
        db (Session): Database session
    
    Returns:
        UserResponse: Registered user details
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create new user with PUBLIC role by default
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            role=UserRole.PUBLIC.value  # Explicit role assignment
        )
        
        # Add and commit user
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User registration failed due to a conflict"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint generating access and refresh tokens
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials
        db (Session): Database session
    
    Returns:
        Token: Access and refresh tokens
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token pair
    tokens = create_token_pair(user)
    
    # Update user's refresh token and last login
    user.refresh_token = tokens["refresh_token"]
    user.last_login = datetime.utcnow()
    db.commit()
    
    return tokens

@router.post("/upgrade-role", response_model=UserResponse)
async def upgrade_user_role(
    upgrade_request: RoleUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade the user's role from PUBLIC to DEVELOPER.
    Now includes email notification for API key.
    """
    try:
        # Check if the current user is requesting the upgrade
        if current_user.email != upgrade_request.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upgrade your own role."
            )

        # Check if the user's current role is PUBLIC
        if current_user.role != UserRole.PUBLIC:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your role is already upgraded."
            )

        # Upgrade the user's role to DEVELOPER and generate a new API key
        current_user.role = upgrade_request.new_role
        current_user.api_key = await api_key_manager.generate_api_key()

        # Commit changes first to ensure database update succeeds
        db.commit()
        db.refresh(current_user)
        
        # Send email notification
        try:
            await email_service.send_api_key_notification(
                user_email=current_user.email,
                api_key=current_user.api_key
            )
        except HTTPException as email_error:
            # Log the email error but don't fail the upgrade
            logger.error(f"Failed to send API key email: {str(email_error)}")
            
        return current_user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Role upgrade error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role upgrade failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: RefreshToken,
    db: Session = Depends(get_db)
):
    """
    Token refresh endpoint
    
    Args:
        refresh_token (RefreshToken): Refresh token
        db (Session): Database session
    
    Returns:
        Token: New access and refresh tokens
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_token.refresh_token)
        
        # Validate token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        # Find user with matching refresh token
        user = db.query(User).filter(
            User.email == payload.get("sub"),
            User.refresh_token == refresh_token.refresh_token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new token pair
        tokens = create_token_pair(user)
        
        # Update refresh token
        user.refresh_token = tokens["refresh_token"]
        db.commit()
        
        return tokens
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User logout endpoint
    
    Args:
        response (Response): HTTP response
        current_user (User): Currently authenticated user
        db (Session): Database session
    
    Returns:
        dict: Logout confirmation message
    """
    try:
        # Clear refresh token
        current_user.refresh_token = None
        db.commit()
        
        # Clear any authentication cookies
        response.delete_cookie("refresh_token")
        
        return {"message": "Successfully logged out"}
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/api-key/generate")
async def generate_api_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    API key generation for developers
    Now includes email notification for new API key.

    Args:
        current_user (User): Currently authenticated user
        db (Session): Database session
    
    Returns:
        dict: API key and rate limit details
    """
    try:
        # Ensure only developers can generate API keys
        if current_user.role != UserRole.DEVELOPER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only developers can generate API keys"
            )

        # Generate new API key
        new_api_key = await api_key_manager.generate_api_key()
        
        # Update user's API key
        current_user.api_key = new_api_key
        db.commit()
        
        # Send email notification
        try:
            await email_service.send_api_key_notification(
                user_email=current_user.email,
                api_key=new_api_key
            )
        except HTTPException as email_error:
            # Log the email error but don't fail the key generation
            logger.error(f"Failed to send API key email: {str(email_error)}")
            # We continue since the key generation succeeded
        
        return {
            "status": "success",
            "api_key": new_api_key,
            "rate_limit": {
                "requests_per_hour": api_key_manager.max_requests,
                "window_size": f"{api_key_manager.window_size} seconds"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"API key generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key generation failed"
        )