"""
Main FastAPI application for the Authentication Service.

This module contains the main FastAPI application with all endpoints,
middleware, and service initialization.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from src.core.database import DatabaseService
from src.core.jwt import JWTService
from src.core.password import PasswordService
from src.core.mfa import MFAService
from src.core.audit import AuditService
from src.core.auth import AuthService
from src.models.schemas import *

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Security
security = HTTPBearer()

# Global services
db_service: DatabaseService = None
jwt_service: JWTService = None
password_service: PasswordService = None
mfa_service: MFAService = None
audit_service: AuditService = None
auth_service: AuthService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global db_service, jwt_service, password_service, mfa_service, audit_service, auth_service
    
    # Initialize services
    logger.info("Initializing Authentication Service...")
    
    # Database service
    database_url = os.getenv("DATABASE_URL", "postgresql://auth_user:auth_password@localhost:5432/auth_service")
    db_service = DatabaseService(database_url)
    await db_service.initialize()
    
    # JWT service
    jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    jwt_service = JWTService(
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        access_token_expire_minutes=access_token_expire,
        refresh_token_expire_days=refresh_token_expire
    )
    
    # Password service
    bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
    password_service = PasswordService(bcrypt_rounds=bcrypt_rounds)
    
    # MFA service
    issuer_name = os.getenv("MFA_ISSUER_NAME", "BMAD")
    mfa_service = MFAService(issuer_name=issuer_name)
    
    # Audit service
    audit_service = AuditService(db_service)
    
    # Auth service
    auth_service = AuthService(
        database_service=db_service,
        jwt_service=jwt_service,
        password_service=password_service,
        mfa_service=mfa_service,
        audit_service=audit_service
    )
    
    logger.info("Authentication Service initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Authentication Service...")
    if db_service:
        await db_service.close()
    logger.info("Authentication Service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Authentication Service",
    description="BMAD Authentication and Authorization Microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from token."""
    try:
        token = credentials.credentials
        validation_result = await auth_service.validate_token(token)
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return validation_result
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current user with admin role."""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_client_ip(request: Request) -> str:
    """Get client IP address."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def get_user_agent(request: Request) -> str:
    """Get user agent string."""
    return request.headers.get("User-Agent", "")


# Health check endpoints
@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Basic health check."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="auth-service",
        version="1.0.0"
    )


@app.get("/health/ready", response_model=HealthStatus)
async def readiness_check():
    """Readiness probe."""
    try:
        # Check database connectivity
        db_healthy = await db_service.health_check()
        
        if not db_healthy:
            return HealthStatus(
                status="unhealthy",
                timestamp=datetime.utcnow(),
                service="auth-service",
                version="1.0.0"
            )
        
        return HealthStatus(
            status="ready",
            timestamp=datetime.utcnow(),
            service="auth-service",
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            service="auth-service",
            version="1.0.0"
        )


@app.get("/health/live", response_model=HealthStatus)
async def liveness_check():
    """Liveness probe."""
    return HealthStatus(
        status="alive",
        timestamp=datetime.utcnow(),
        service="auth-service",
        version="1.0.0"
    )


# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister,
    request: Request
):
    """Register a new user."""
    try:
        result = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return TokenResponse(**result["tokens"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@app.post("/auth/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    request: Request
):
    """Login user."""
    try:
        result = await auth_service.login_user(
            email=login_data.email,
            password=login_data.password,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        return TokenResponse(**result["tokens"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate user"
        )


@app.post("/auth/logout")
async def logout_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request
):
    """Logout user."""
    try:
        # For now, we'll just return success
        # In a real implementation, you'd need to pass the session ID
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"User logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout user"
        )


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    request: Request
):
    """Refresh access token."""
    try:
        result = await auth_service.refresh_token(
            refresh_token=refresh_data.refresh_token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        return TokenResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@app.post("/auth/validate")
async def validate_token(
    token_data: TokenValidate
):
    """Validate access token."""
    try:
        result = await auth_service.validate_token(token_data.token)
        return result
        
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate token"
        )


@app.post("/auth/forgot-password")
async def forgot_password(
    reset_data: PasswordResetRequest,
    request: Request
):
    """Request password reset."""
    try:
        result = await auth_service.request_password_reset(
            email=reset_data.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {"message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process reset request"
        )


@app.post("/auth/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    request: Request
):
    """Reset password."""
    try:
        result = await auth_service.reset_password(
            reset_token=reset_data.token,
            new_password=reset_data.new_password,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {"message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@app.post("/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request
):
    """Change password."""
    try:
        result = await auth_service.change_password(
            user_id=current_user["user_id"],
            current_password=password_data.current_password,
            new_password=password_data.new_password,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {"message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


# User management endpoints
@app.get("/users", response_model=UserList)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """List all users (admin only)."""
    try:
        users = await db_service.list_users(skip=skip, limit=limit)
        total = await db_service.count_users()
        
        return UserList(
            users=users,
            total=total,
            page=skip // limit + 1,
            size=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user details."""
    try:
        # Users can only access their own data unless they're admin
        if current_user["user_id"] != user_id and "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile."""
    try:
        # Users can only update their own data unless they're admin
        if current_user["user_id"] != user_id and "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        update_data = user_data.dict(exclude_unset=True)
        user = await db_service.update_user(user_id, update_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Delete user (admin only)."""
    try:
        success = await db_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


# Service information
@app.get("/info", response_model=ServiceInfo)
async def get_service_info():
    """Get service information."""
    import time
    start_time = time.time()
    
    return ServiceInfo(
        name="Authentication Service",
        version="1.0.0",
        description="BMAD Authentication and Authorization Microservice",
        status="healthy",
        uptime=time.time() - start_time,
        timestamp=datetime.utcnow()
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 