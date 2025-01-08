# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session
import secrets
import logging
from ..models.user import User, UserRole
from .config import get_settings
from ..models.base import get_db

logger = logging.getLogger(__name__)
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_token(data: dict, expires_delta: Optional[timedelta] = None, is_refresh: bool = False) -> str:
    """Create access or refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + (
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) if is_refresh 
            else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    
    to_encode.update({
        "exp": expire,
        "type": "refresh" if is_refresh else "access"
    })
    
    encoded_token = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=ALGORITHM
    )
    return encoded_token

def create_token_pair(user: User) -> Dict[str, str]:
    """Generate both access and refresh tokens"""
    access_token_data = {
        "sub": user.email,
        "role": user.role
    }
    
    refresh_token_data = {
        "sub": user.email,
        "role": user.role
    }
    
    access_token = create_token(access_token_data)
    refresh_token = create_token(refresh_token_data, is_refresh=True)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def verify_token(token: str) -> Dict:
    """Verify token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Existing password functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# API Key generation and management
class APIKeyManager:
    def __init__(self):
        self._rate_limits: Dict[str, Dict] = {}
        self.max_requests = 100  # Requests per window
        self.window_size = 3600  # Window size in seconds (1 hour)

    async def generate_api_key(self) -> str:
        """Generate a new API key"""
        return f"pntr_{''.join(secrets.token_urlsafe(32))}"

    async def validate_api_key(
        self,
        api_key: str = Security(APIKeyHeader(name="X-API-Key")),
        db: Session = Depends(get_db)
    ) -> User:
        """Validate API key and check rate limits"""
        try:
            user = db.query(User).filter(
                User.api_key == api_key,
                User.role == UserRole.DEVELOPER
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key or insufficient permissions",
                    headers={"WWW-Authenticate": "ApiKey"},
                )

            self._check_rate_limit(api_key)
            self._update_rate_limit(api_key)
            
            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API key validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during API key validation"
            )

    def _check_rate_limit(self, api_key: str) -> None:
        """Check if the API key has exceeded its rate limit"""
        now = datetime.utcnow()
        
        if api_key in self._rate_limits:
            window_start = self._rate_limits[api_key]["window_start"]
            request_count = self._rate_limits[api_key]["request_count"]
            
            if (now - window_start).total_seconds() > self.window_size:
                self._rate_limits[api_key] = {
                    "window_start": now,
                    "request_count": 0
                }
            elif request_count >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "reset_time": (window_start + timedelta(seconds=self.window_size)).isoformat(),
                        "limit": self.max_requests,
                        "window_size": f"{self.window_size} seconds"
                    }
                )

    def _update_rate_limit(self, api_key: str) -> None:
        """Update the rate limit counter for an API key"""
        now = datetime.utcnow()
        
        if api_key not in self._rate_limits:
            self._rate_limits[api_key] = {
                "window_start": now,
                "request_count": 1
            }
        else:
            self._rate_limits[api_key]["request_count"] += 1

api_key_manager = APIKeyManager()