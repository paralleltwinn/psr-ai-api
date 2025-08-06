# =============================================================================
# POORNASREE AI - AUTHENTICATION MODULE
# =============================================================================

"""
Authentication module for user authentication, authorization, and security.
Handles JWT tokens, password hashing, OTP verification, and role-based access control.
"""

# Authentication utilities
from .auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    generate_otp_secret,
    generate_otp_code,
    verify_otp_code,
    generate_random_otp,
    is_super_admin,
    create_refresh_token,
    verify_refresh_token
)

# Authentication dependencies
from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    require_super_admin,
    require_admin_or_above,
    require_engineer_or_above,
    require_role,
    require_any_role,
    optional_user,
    RoleChecker,
    require_customer,
    require_engineer,
    require_admin,
    require_super_admin_role,
    require_staff,
    require_management,
    check_permission,
    check_resource_ownership,
    verify_resource_access
)

__all__ = [
    # Auth utilities
    "verify_password",
    "get_password_hash", 
    "create_access_token",
    "verify_token",
    "generate_otp_secret",
    "generate_otp_code",
    "verify_otp_code",
    "generate_random_otp",
    "is_super_admin",
    "create_refresh_token",
    "verify_refresh_token",
    
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "require_super_admin",
    "require_admin_or_above", 
    "require_engineer_or_above",
    "require_role",
    "require_any_role",
    "optional_user",
    "RoleChecker",
    "require_customer",
    "require_engineer",
    "require_admin",
    "require_super_admin_role",
    "require_staff",
    "require_management",
    "check_permission",
    "check_resource_ownership",
    "verify_resource_access"
]
