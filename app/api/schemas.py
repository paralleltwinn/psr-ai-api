# =============================================================================
# POORNASREE AI - PYDANTIC SCHEMAS
# =============================================================================

"""
Pydantic schemas for request/response validation and serialization.
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from ..core.constants import UserRole, UserStatus, NotificationType


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        str_strip_whitespace = True


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseSchema):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="User first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User last name")
    role: UserRole = Field(..., description="User role")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="User password")
    phone_number: Optional[str] = Field(None, max_length=20, description="User phone number")


class UserUpdate(BaseSchema):
    """Schema for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_picture: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    status: UserStatus
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None


class UserListResponse(BaseSchema):
    """Schema for paginated user list response."""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


# =============================================================================
# AUTHENTICATION SCHEMAS
# =============================================================================

class LoginRequest(BaseSchema):
    """
    Schema for user login request.
    
    **Example:**
    ```json
    {
      "email": "admin@poornasree.ai",
      "password": "Admin@2024"
    }
    ```
    """
    email: EmailStr = Field(
        ..., 
        description="User email address",
        example="admin@poornasree.ai"
    )
    password: Optional[str] = Field(
        None, 
        description="User password (required for password login)",
        example="Admin@2024",
        min_length=8
    )


class LoginResponse(BaseSchema):
    """
    Schema for successful login response.
    
    **Example:**
    ```json
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "email": "admin@poornasree.ai",
        "role": "SUPER_ADMIN",
        "status": "ACTIVE"
      },
      "expires_in": 1800
    }
    ```
    """
    access_token: str = Field(
        ..., 
        description="JWT access token for authentication",
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    )
    token_type: str = Field(
        default="bearer", 
        description="Token type (always 'bearer')",
        example="bearer"
    )
    user: UserResponse = Field(
        ..., 
        description="User profile information"
    )
    expires_in: int = Field(
        ..., 
        description="Token expiration time in seconds",
        example=1800
    )


class TokenData(BaseSchema):
    """Schema for token data."""
    email: Optional[str] = None


# =============================================================================
# OTP SCHEMAS
# =============================================================================

class OTPRequest(BaseSchema):
    """Schema for OTP request."""
    email: EmailStr = Field(..., description="Email address for OTP")
    purpose: str = Field(default="login", description="Purpose of OTP")


class OTPVerifyRequest(BaseSchema):
    """Schema for OTP verification."""
    email: EmailStr = Field(..., description="Email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    purpose: str = Field(default="login", description="Purpose of OTP")


# =============================================================================
# REGISTRATION SCHEMAS
# =============================================================================

class CustomerRegistration(BaseSchema):
    """Schema for customer registration."""
    email: EmailStr = Field(..., description="Customer email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="Customer first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Customer last name")
    otp_code: str = Field(..., min_length=6, max_length=6, description="OTP verification code")
    phone_number: Optional[str] = Field(None, max_length=20, description="Customer phone number")


class EngineerRegistration(BaseSchema):
    """Schema for engineer registration."""
    email: EmailStr = Field(..., description="Engineer email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="Engineer first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Engineer last name")
    password: str = Field(..., min_length=8, max_length=100, description="Engineer password")
    experience_years: int = Field(..., ge=0, le=50, description="Years of experience")
    skills: str = Field(..., min_length=10, max_length=2000, description="Technical skills")
    previous_company: Optional[str] = Field(None, max_length=200, description="Previous company")
    portfolio_url: Optional[str] = Field(None, max_length=500, description="Portfolio URL")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    cover_letter: Optional[str] = Field(None, max_length=5000, description="Cover letter")
    
    @validator('portfolio_url')
    def validate_portfolio_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Portfolio URL must start with http:// or https://')
        return v


class AdminCreation(BaseSchema):
    """Schema for admin creation."""
    email: EmailStr = Field(..., description="Admin email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="Admin first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Admin last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Admin phone number")


# =============================================================================
# NOTIFICATION SCHEMAS
# =============================================================================

class NotificationBase(BaseSchema):
    """Base notification schema."""
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message")
    notification_type: str = Field(..., description="Notification type")


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    recipient_id: int = Field(..., description="Recipient user ID")
    sender_id: Optional[int] = Field(None, description="Sender user ID")
    metadata_json: Optional[str] = Field(None, description="Additional metadata as JSON")


class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    sender: Optional[UserResponse] = None


class NotificationListResponse(BaseSchema):
    """Schema for paginated notification list response."""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    size: int
    pages: int


# =============================================================================
# ENGINEER APPLICATION SCHEMAS
# =============================================================================

class EngineerApplicationResponse(BaseSchema):
    """Schema for engineer application response."""
    id: int
    experience_years: int
    skills: str
    previous_company: Optional[str]
    portfolio_url: Optional[str]
    cover_letter: Optional[str]
    status: UserStatus
    review_notes: Optional[str]
    review_date: Optional[datetime]
    created_at: datetime
    user: UserResponse
    reviewer: Optional[UserResponse] = None


class EngineerApplicationReview(BaseSchema):
    """Schema for reviewing engineer application."""
    status: UserStatus = Field(..., description="Application status")
    review_notes: Optional[str] = Field(None, max_length=2000, description="Review notes")


class EngineerApplicationListResponse(BaseSchema):
    """Schema for paginated engineer application list response."""
    applications: List[EngineerApplicationResponse]
    total: int
    pending_count: int
    page: int
    size: int
    pages: int


# =============================================================================
# DASHBOARD SCHEMAS
# =============================================================================

class DashboardStats(BaseSchema):
    """Schema for dashboard statistics."""
    total_users: int = Field(..., description="Total number of users")
    pending_engineers: int = Field(..., description="Number of pending engineer applications")
    total_admins: int = Field(..., description="Total number of admins")
    total_engineers: int = Field(..., description="Total number of engineers")
    total_customers: int = Field(..., description="Total number of customers")
    active_users: int = Field(..., description="Number of active users")
    inactive_users: int = Field(..., description="Number of inactive users")


class AdminDashboard(BaseSchema):
    """Schema for admin dashboard."""
    stats: DashboardStats = Field(..., description="Dashboard statistics")
    recent_notifications: List[NotificationResponse] = Field(..., description="Recent notifications")
    pending_applications: List[EngineerApplicationResponse] = Field(..., description="Pending applications")


class SuperAdminDashboard(AdminDashboard):
    """Schema for super admin dashboard."""
    recent_logins: List[dict] = Field(default=[], description="Recent login attempts")
    system_health: dict = Field(default={}, description="System health metrics")


# =============================================================================
# UTILITY SCHEMAS
# =============================================================================

class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")


class SearchParams(PaginationParams):
    """Schema for search parameters."""
    query: Optional[str] = Field(None, min_length=1, max_length=100, description="Search query")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class APIResponse(BaseSchema):
    """Generic API response schema."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")


class HealthCheck(BaseSchema):
    """Schema for health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Check timestamp")
    database: str = Field(..., description="Database status")
    redis: str = Field(..., description="Redis status")
