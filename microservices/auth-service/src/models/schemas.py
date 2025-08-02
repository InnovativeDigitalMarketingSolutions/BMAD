"""
Pydantic schemas for request/response validation.

This module contains all the Pydantic models used for API request/response
validation and serialization.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class RoleStatus(str, Enum):
    """Role status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


# Health Check Models
class HealthStatus(BaseModel):
    """Health status response model."""
    status: str
    timestamp: datetime
    service: str = "auth-service"
    version: str = "1.0.0"


class ServiceHealth(BaseModel):
    """Service health check response model."""
    status: str
    database: str
    redis: str
    auth0: str
    timestamp: datetime


# Authentication Models
class UserRegister(BaseModel):
    """User registration request model."""
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str


class TokenRefresh(BaseModel):
    """Token refresh request model."""
    refresh_token: str


class TokenValidate(BaseModel):
    """Token validation request model."""
    token: str


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset model."""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordChange(BaseModel):
    """Password change model."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# User Models
class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """User update model."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    """User response model."""
    id: str
    status: UserStatus
    email_verified: bool
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}
    
    model_config = {"from_attributes": True}


class UserList(BaseModel):
    """User list response model."""
    users: List[UserResponse]
    total: int
    page: int
    size: int


# Role Models
class RoleBase(BaseModel):
    """Base role model."""
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Role creation model."""
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    """Role update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(RoleBase):
    """Role response model."""
    id: str
    permissions: List[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class RoleList(BaseModel):
    """Role list response model."""
    roles: List[RoleResponse]
    total: int
    page: int
    size: int


# Session Models
class SessionBase(BaseModel):
    """Base session model."""
    device_info: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SessionResponse(SessionBase):
    """Session response model."""
    id: str
    user_id: str
    expires_at: datetime
    created_at: datetime
    last_used_at: datetime
    is_active: bool
    
    model_config = {"from_attributes": True}


class SessionList(BaseModel):
    """Session list response model."""
    sessions: List[SessionResponse]
    total: int
    page: int
    size: int


# MFA Models
class MFAEnable(BaseModel):
    """MFA enable request model."""
    password: str


class MFASetup(BaseModel):
    """MFA setup response model."""
    secret: str
    qr_code: str
    backup_codes: List[str]


class MFAVerify(BaseModel):
    """MFA verification model."""
    code: str = Field(..., min_length=6, max_length=6)


class MFABackupCode(BaseModel):
    """MFA backup code model."""
    code: str = Field(..., min_length=8, max_length=8)


# Analytics Models
class UserAnalytics(BaseModel):
    """User analytics model."""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    verified_users: int
    mfa_enabled_users: int


class SessionAnalytics(BaseModel):
    """Session analytics model."""
    total_sessions: int
    active_sessions: int
    expired_sessions: int
    revoked_sessions: int
    average_session_duration: float


class SecurityAnalytics(BaseModel):
    """Security analytics model."""
    failed_login_attempts: int
    password_reset_requests: int
    mfa_verification_attempts: int
    suspicious_activities: int


# Audit Models
class AuditLogBase(BaseModel):
    """Base audit log model."""
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}


class AuditLogCreate(AuditLogBase):
    """Audit log creation model."""
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Audit log response model."""
    id: int
    user_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AuditLogList(BaseModel):
    """Audit log list response model."""
    logs: List[AuditLogResponse]
    total: int
    page: int
    size: int


# Error Models
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Validation error model."""
    field: str
    message: str
    value: Optional[Any] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""
    error: str = "validation_error"
    message: str = "Validation failed"
    details: List[ValidationError]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Success Models
class SuccessResponse(BaseModel):
    """Success response model."""
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Service Info Models
class ServiceInfo(BaseModel):
    """Service information model."""
    name: str = "Authentication Service"
    version: str = "1.0.0"
    description: str = "BMAD Authentication and Authorization Microservice"
    status: str = "healthy"
    uptime: float
    timestamp: datetime = Field(default_factory=datetime.utcnow) 