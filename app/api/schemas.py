# =============================================================================
# POORNASREE AI - PYDANTIC SCHEMAS
# =============================================================================

"""
Pydantic schemas for request/response validation and serialization.
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict
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
    
    # Customer specific fields
    machine_model: Optional[str] = None
    state: Optional[str] = None
    
    # Engineer specific fields  
    department: Optional[str] = None
    dealer: Optional[str] = None


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
      "email": "official.tishnu@gmail.com",
      "password": "Access@404"
    }
    ```
    """
    email: EmailStr = Field(
        ..., 
        description="User email address",
        example="official.tishnu@gmail.com"
    )
    password: Optional[str] = Field(
        None, 
        description="User password (required for password login)",
        example="Access@404",
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
        "email": "official.tishnu@gmail.com",
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
    """
    Schema for customer registration - simplified fields only.
    
    **Example:**
    ```json
    {
      "email": "customer@example.com",
      "first_name": "John",
      "last_name": "Doe", 
      "machine_model": "Model X1",
      "state": "California",
      "phone_number": "+1234567890",
      "otp_code": "123456"
    }
    ```
    """
    email: EmailStr = Field(..., description="Customer email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="Customer first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Customer last name")
    machine_model: str = Field(..., min_length=1, max_length=200, description="Machine model")
    state: str = Field(..., min_length=1, max_length=100, description="State/Province")
    phone_number: str = Field(..., max_length=20, description="Customer phone number")
    otp_code: str = Field(..., min_length=6, max_length=6, description="OTP verification code")


class EngineerRegistration(BaseSchema):
    """
    Schema for engineer registration - simplified fields only.
    
    **Example:**
    ```json
    {
      "email": "engineer@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "phone_number": "+1234567890",
      "department": "AI Research",
      "dealer": "Tech Solutions Inc",
      "state": "New York"
    }
    ```
    """
    email: EmailStr = Field(..., description="Engineer email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="Engineer first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Engineer last name")
    phone_number: str = Field(..., max_length=20, description="Engineer phone number")
    department: str = Field(..., min_length=1, max_length=100, description="Department/Specialization")
    dealer: Optional[str] = Field(None, max_length=200, description="Dealer/Company (optional)")
    state: str = Field(..., min_length=1, max_length=100, description="State/Province")


class AdminCreation(BaseSchema):
    """Schema for admin creation."""
    email: EmailStr = Field(..., description="Admin email address")
    password: str = Field(..., min_length=8, description="Admin password")
    first_name: str = Field(..., min_length=1, max_length=100, description="Admin first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Admin last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Admin phone number")
    department: str = Field(..., min_length=1, max_length=100, description="Admin department")


class SuperAdminProfileUpdate(BaseSchema):
    """Schema for updating super admin profile."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    current_password: str = Field(..., min_length=8, description="Current password for verification")
    new_password: Optional[str] = Field(None, min_length=8, description="New password (optional)")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")


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
    """Schema for engineer application response - simplified."""
    id: int
    status: UserStatus
    review_notes: Optional[str]
    review_date: Optional[datetime]
    created_at: datetime
    user: UserResponse
    reviewer: Optional[UserResponse] = None
    
    # New admin dashboard fields
    department: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None
    portfolio: Optional[str] = None
    cover_letter: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None


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
# ADMIN MANAGEMENT SCHEMAS
# =============================================================================

class AdminCreation(BaseSchema):
    """Schema for creating admin accounts (Super Admin only)."""
    email: EmailStr = Field(..., description="Admin email address")
    password: str = Field(..., min_length=8, max_length=100, description="Admin password")
    first_name: str = Field(..., min_length=1, max_length=100, description="Admin first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Admin last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Admin phone number")
    department: Optional[str] = Field(None, max_length=100, description="Department")


class SuperAdminProfileUpdate(BaseSchema):
    """Schema for super admin profile updates."""
    current_password: str = Field(..., description="Current password for verification")
    email: Optional[EmailStr] = Field(None, description="New email address")
    new_password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="New first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="New last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="New phone number")


class AdminListResponse(BaseSchema):
    """Response for admin list."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    admins: List[UserResponse] = Field(..., description="List of admin users")
    total_count: int = Field(..., description="Total number of admins")


class AdminDashboardStats(BaseSchema):
    """Schema for admin dashboard statistics (limited access)."""
    total_engineers: int = Field(..., description="Total number of engineers")
    total_customers: int = Field(..., description="Total number of customers")
    pending_engineers: int = Field(..., description="Number of pending engineer applications")
    approved_engineers: int = Field(..., description="Number of approved engineers")
    rejected_engineers: int = Field(..., description="Number of rejected engineers")
    active_customers: int = Field(..., description="Number of active customers")


class AdminStatsResponse(BaseSchema):
    """Response for admin dashboard statistics."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    stats: AdminDashboardStats = Field(..., description="Admin dashboard statistics")


class PendingEngineerResponse(BaseSchema):
    """Response for pending engineer applications."""
    id: int = Field(..., description="Application ID")
    first_name: str = Field(..., description="Engineer first name")
    last_name: str = Field(..., description="Engineer last name")
    email: EmailStr = Field(..., description="Engineer email")
    department: str = Field(..., description="Department")
    experience: str = Field(..., description="Years of experience")
    skills: str = Field(..., description="Technical skills")
    portfolio: Optional[str] = Field(None, description="Portfolio URL")
    created_at: datetime = Field(..., description="Application date")


class PendingEngineersResponse(BaseSchema):
    """Response for pending engineers list."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    engineers: List[PendingEngineerResponse] = Field(..., description="List of pending engineers")


class EngineerActionResponse(BaseSchema):
    """Response for engineer approval/rejection actions."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    engineer_id: int = Field(..., description="Engineer ID")
    action: str = Field(..., description="Action performed (approve/reject)")


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


class APISuccessResponse(BaseSchema):
    """Success API response schema."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Response data")


class APIErrorResponse(BaseSchema):
    """Error API response schema."""
    success: bool = Field(False, description="Operation success status")
    message: str = Field(..., description="Error message")
    errors: Optional[List[str]] = Field(None, description="Detailed error messages")
    error_code: Optional[str] = Field(None, description="Error code for frontend handling")


class UserCreationResponse(BaseSchema):
    """Response for user creation operations."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    user: UserResponse = Field(..., description="Created user data")


class ProfileUpdateResponse(BaseSchema):
    """Response for profile update operations."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    user: UserResponse = Field(..., description="Updated user data")


class DashboardStatsResponse(BaseSchema):
    """Response for dashboard statistics."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    stats: DashboardStats = Field(..., description="Dashboard statistics")


class AdminListResponse(BaseSchema):
    """Response for admin list operations."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    admins: List[UserResponse] = Field(..., description="List of admin users")
    total_count: int = Field(..., description="Total number of admins")


class LoginMethodResponse(BaseSchema):
    """Response for login method check."""
    requires_password: bool = Field(..., description="Whether user requires password login")
    user_role: Optional[str] = Field(None, description="User role if exists")
    user_exists: bool = Field(..., description="Whether user exists in system")


class HealthCheck(BaseSchema):
    """Schema for health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Check timestamp")
    database: str = Field(..., description="Database status")
    redis: str = Field(..., description="Redis status")


# =============================================================================
# ADMIN DASHBOARD SCHEMAS
# =============================================================================

class AdminCreateRequest(BaseSchema):
    """Admin Creation Request Schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)


class ApplicationReviewRequest(BaseSchema):
    """Application Review Request Schema"""
    reason: Optional[str] = Field(None, description="Reason for rejection (required for reject)")


class AdminStatsResponse(BaseSchema):
    """Admin Dashboard Stats Response Schema"""
    total_engineers: int
    approved_engineers: int
    total_customers: int
    active_customers: int
    pending_engineers: int
    rejected_engineers: int
    last_updated: str


class SuperAdminStatsResponse(BaseSchema):
    """Super Admin Dashboard Stats Response Schema"""
    total_users: int
    active_users: int
    users_by_role: Dict[str, int]
    users_by_status: Dict[str, int]
    last_updated: str


class AdminDashboardResponse(BaseSchema):
    """Admin Dashboard Response Schema"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    stats: AdminStatsResponse = Field(..., description="Admin dashboard statistics")


class SuperAdminDashboardResponse(BaseSchema):
    """Super Admin Dashboard Response Schema"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    stats: SuperAdminStatsResponse = Field(..., description="Super admin dashboard statistics")
