# =============================================================================
# POORNASREE AI - CONFIGURATION MANAGEMENT
# =============================================================================

"""
Configuration management using Pydantic Settings.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    database_url: str
    test_database_url: Optional[str] = None
    
    # =============================================================================
    # CACHE & REDIS CONFIGURATION
    # =============================================================================
    redis_url: str
    
    # =============================================================================
    # SECURITY & JWT CONFIGURATION
    # =============================================================================
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # =============================================================================
    # SUPER ADMIN CONFIGURATION
    # =============================================================================
    super_admin_email: str
    super_admin_password: str
    
    # =============================================================================
    # EMAIL & SMTP CONFIGURATION
    # =============================================================================
    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    mail_from: str
    mail_from_name: str
    
    # =============================================================================
    # OTP & VERIFICATION CONFIGURATION
    # =============================================================================
    otp_secret_key: str
    otp_expiry_minutes: int = 5
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    app_name: str = "Poornasree AI Authentication System"
    app_version: str = "1.0.0"
    app_description: str = "Comprehensive role-based authentication system"
    debug: bool = True
    environment: str = "development"
    frontend_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    
    # =============================================================================
    # API & CORS CONFIGURATION
    # =============================================================================
    api_v1_prefix: str = "/api/v1"
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def generate_secret_key(self) -> str:
        """Generate a secure secret key if not provided."""
        return secrets.token_urlsafe(32)


# Global settings instance
settings = Settings()
