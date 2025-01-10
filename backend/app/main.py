# backend/app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import logging
from pathlib import Path
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import List, Optional

from .api import auth, courses, analytics
from .models import init_db
from .core.config import get_settings
from .core.types import TypedFastAPI, AppState
from .core.rate_limit import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to every response"""
    
    def __init__(
        self,
        app: ASGIApp,
        allowed_hosts: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or []

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = self._build_csp_header()
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        
        return response

    def _build_csp_header(self) -> str:
        """Build Content Security Policy header with relaxed rules for Swagger UI"""
        csp_directives = [
            "default-src 'self'",
            "img-src 'self' data: https: blob:",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
            "font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com",
            "connect-src 'self' *",
            "frame-src 'self'",
            "form-action 'self'",
            "base-uri 'self'",
            "object-src 'none'"
        ]
        return "; ".join(csp_directives)

class CORSConfigMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware with dynamic origin validation"""
    
    def __init__(
        self,
        app: ASGIApp,
        allowed_origins: List[str],
        allow_credentials: bool = True
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins
        self.allow_credentials = allow_credentials

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Validate origin
        if origin:
            if not any(
                self._match_origin(origin, allowed)
                for allowed in self.allowed_origins
            ):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid origin"}
                )
        
        response = await call_next(request)
        
        # Add CORS headers
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                "Accept, Authorization, Content-Type, X-API-Key, "
                "X-Requested-With"
            )
            response.headers["Access-Control-Max-Age"] = "600"  # 10 minutes
            
        return response

    def _match_origin(self, origin: str, pattern: str) -> bool:
        """Match origin against allowed pattern with wildcard support"""
        if pattern == "*":
            return True
        if pattern.startswith("*"):
            return origin.endswith(pattern[1:])
        if pattern.endswith("*"):
            return origin.startswith(pattern[:-1])
        return origin == pattern

# Create the FastAPI application with our custom type
app = TypedFastAPI(
    title="Pintar Ekspor API",
    description="API for Pintar Ekspor platform with analytics capabilities",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# Initialize the application state
app.state = AppState()

# Create and store the rate limit middleware
rate_limit_middleware = RateLimitMiddleware(app)
app.state.rate_limit_middleware = rate_limit_middleware

# Remove duplicate CORS middleware and consolidate into one
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# Add security headers middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    allowed_hosts=settings.get_hosts_list()
)

# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI endpoint"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Update the shutdown event to use the stored instance:
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown"""
    try:
        if app.state.rate_limit_middleware is not None:
            await app.state.rate_limit_middleware.cleanup()
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {str(e)}")

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Database initialization event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler
    - Initialize database
    - Perform any necessary startup tasks
    """
    try:
        logger.info("Initializing application...")
        
        # Initialize database tables
        init_db()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup initialization failed: {str(e)}")
        raise

# API Routers
app.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Authentication"]
)
app.include_router(
    courses.router, 
    prefix="/courses", 
    tags=["Courses"]
)
app.include_router(
    analytics.router, 
    prefix="/analytics", 
    tags=["Analytics"]
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing basic API information"""
    return {
        "message": "Welcome to Pintar Ekspor API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/auth",
            "courses": "/courses",
            "analytics": {
                "main": "/analytics",
                "documentation": "/analytics/documentation"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and system status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0",
        "environment": settings.ENV,
        "database": "Connected",
        "services": {
            "authentication": "Operational",
            "courses": "Operational",
            "analytics": "Operational"
        }
    }

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header to all responses"""
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response