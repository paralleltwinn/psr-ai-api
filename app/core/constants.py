# =============================================================================
# POORNASREE AI - CONSTANTS & ENUMS
# =============================================================================

"""
Application constants and enumerations.
Centralized location for all application constants.
"""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ENGINEER = "engineer"
    CUSTOMER = "customer"


class UserStatus(str, Enum):
    """User status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class NotificationType(str, Enum):
    """Notification type enumeration."""
    VERIFICATION = "verification"
    OTP = "otp"
    WELCOME = "welcome"
    ENGINEER_APPLICATION = "engineer_application"
    ENGINEER_APPROVED = "engineer_approved"
    ENGINEER_REJECTED = "engineer_rejected"
    GENERAL = "general"
    ENGINEER_REGISTRATION = "engineer_registration"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"
    ADMIN_CREATED = "admin_created"
    SYSTEM_NOTIFICATION = "system_notification"


class ApplicationStatus(str, Enum):
    """Application status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


class OTPPurpose(str, Enum):
    """OTP purpose enumeration."""
    LOGIN = "login"
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class EmailTemplate(str, Enum):
    """Email template enumeration."""
    OTP_VERIFICATION = "otp_verification"
    ENGINEER_REGISTRATION = "engineer_registration"
    APPLICATION_APPROVAL = "application_approval"
    APPLICATION_REJECTION = "application_rejection"
    ADMIN_CREATION = "admin_creation"
    WELCOME = "welcome"


# =============================================================================
# APPLICATION CONSTANTS
# =============================================================================

# Security
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 100
OTP_LENGTH = 6
MAX_LOGIN_ATTEMPTS = 5

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]

# Email
MAX_EMAIL_LENGTH = 320
MAX_NAME_LENGTH = 100

# API
API_TIMEOUT = 30
RATE_LIMIT_PER_MINUTE = 60

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300     # 5 minutes
CACHE_TTL_MEDIUM = 1800   # 30 minutes
CACHE_TTL_LONG = 3600     # 1 hour

# =============================================================================
# HTTP STATUS MESSAGES
# =============================================================================

HTTP_STATUS_MESSAGES = {
    200: "Success",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    422: "Validation Error",
    429: "Too Many Requests",
    500: "Internal Server Error"
}

# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES = {
    "USER_NOT_FOUND": "User not found",
    "INVALID_CREDENTIALS": "Invalid email or password",
    "EMAIL_ALREADY_EXISTS": "Email already registered",
    "INVALID_OTP": "Invalid or expired OTP",
    "ACCOUNT_INACTIVE": "Account is not active",
    "ACCOUNT_PENDING": "Account is pending approval",
    "INSUFFICIENT_PERMISSIONS": "Not enough permissions",
    "INVALID_TOKEN": "Invalid or expired token",
    "APPLICATION_NOT_FOUND": "Application not found",
    "NOTIFICATION_NOT_FOUND": "Notification not found",
    "EMAIL_SEND_FAILED": "Failed to send email",
    "WEAK_PASSWORD": "Password does not meet security requirements"
}

# =============================================================================
# SUCCESS MESSAGES
# =============================================================================

SUCCESS_MESSAGES = {
    "LOGIN_SUCCESS": "Login successful",
    "REGISTRATION_SUCCESS": "Registration successful",
    "OTP_SENT": "OTP sent successfully",
    "APPLICATION_SUBMITTED": "Application submitted successfully",
    "APPLICATION_REVIEWED": "Application reviewed successfully",
    "ADMIN_CREATED": "Admin created successfully",
    "NOTIFICATION_READ": "Notification marked as read",
    "EMAIL_SENT": "Email sent successfully"
}
