# =============================================================================
# POORNASREE AI - SERVICES MODULE
# =============================================================================

"""
Services module for business logic, email handling, and external integrations.
"""

# Email service
from .email_service import (
    send_verification_email,
    send_otp_email,
    send_welcome_email,
    send_password_reset_email,
    send_engineer_application_notification,
    send_engineer_approval_notification,
    send_engineer_rejection_notification,
    send_notification_email,
    EmailService
)

# User service
from .user_service import (
    UserService,
    create_user_account,
    verify_user_email,
    update_user_profile,
    deactivate_user_account,
    get_user_by_email,
    get_user_by_id,
    get_users_by_role,
    search_users
)

__all__ = [
    # Email service
    "send_verification_email",
    "send_otp_email", 
    "send_welcome_email",
    "send_password_reset_email",
    "send_engineer_application_notification",
    "send_engineer_approval_notification",
    "send_engineer_rejection_notification",
    "send_notification_email",
    "EmailService",
    
    # User service
    "UserService",
    "create_user_account",
    "verify_user_email",
    "update_user_profile",
    "deactivate_user_account",
    "get_user_by_email",
    "get_user_by_id",
    "get_users_by_role",
    "search_users"
]
