# =============================================================================
# POORNASREE AI - CORE MODULE
# =============================================================================

"""
Core module containing essential components for the authentication system.
"""

from .constants import (
    UserRole,
    UserStatus,
    NotificationType,
    OTPPurpose,
    EmailTemplate,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)

__all__ = [
    "UserRole",
    "UserStatus", 
    "NotificationType",
    "OTPPurpose",
    "EmailTemplate",
    "ERROR_MESSAGES",
    "SUCCESS_MESSAGES"
]
