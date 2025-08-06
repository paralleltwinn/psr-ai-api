# =============================================================================
# POORNASREE AI - API SCHEMAS MODULE
# =============================================================================

"""
API schemas module containing request/response models and validation.
"""

from .schemas import *

__all__ = [
    # Base schemas
    "BaseSchema",
    
    # User schemas
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    
    # Authentication schemas
    "LoginRequest",
    "LoginResponse", 
    "TokenData",
    
    # OTP schemas
    "OTPRequest",
    "OTPVerifyRequest",
    
    # Registration schemas
    "CustomerRegistration",
    "EngineerRegistration",
    "AdminCreation",
    
    # Notification schemas
    "NotificationBase",
    "NotificationCreate",
    "NotificationResponse",
    "NotificationListResponse",
    
    # Engineer application schemas
    "EngineerApplicationResponse",
    "EngineerApplicationReview",
    "EngineerApplicationListResponse",
    
    # Dashboard schemas
    "DashboardStats",
    "AdminDashboard",
    "SuperAdminDashboard",
    
    # Utility schemas
    "PaginationParams",
    "SearchParams",
    "APIResponse",
    "HealthCheck"
]
