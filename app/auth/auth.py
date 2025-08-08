# =============================================================================
# POORNASREE AI - AUTHENTICATION UTILITIES
# =============================================================================

"""
Authentication utilities for password hashing, JWT tokens, and OTP generation.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from ..config import settings
import pyotp
import secrets
import string
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating access token"
        )


def create_action_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT action token for email-based actions."""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Action tokens expire in 7 days by default
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "action"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Action token creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating action token"
        )


def verify_token(token: str) -> str:
    """Verify and decode JWT token, return email."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check token type
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get email from payload
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return email
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_action_token(token: str) -> dict:
    """Verify and decode action token, return payload."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check token type
        token_type = payload.get("type")
        if token_type != "action":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid action token type"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Action token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate action token"
        )
    except jwt.JWTError as e:
        logger.warning(f"JWT verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_otp_secret() -> str:
    """Generate a random secret for OTP."""
    try:
        return pyotp.random_base32()
    except Exception as e:
        logger.error(f"OTP secret generation error: {e}")
        return secrets.token_urlsafe(32)


def generate_otp_code(secret: str) -> str:
    """Generate OTP code using TOTP."""
    try:
        totp = pyotp.TOTP(secret, interval=settings.otp_expiry_minutes * 60)
        return totp.now()
    except Exception as e:
        logger.error(f"OTP code generation error: {e}")
        return generate_random_otp()


def verify_otp_code(secret: str, code: str) -> bool:
    """Verify OTP code."""
    try:
        totp = pyotp.TOTP(secret, interval=settings.otp_expiry_minutes * 60)
        return totp.verify(code, valid_window=1)
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        return False


def generate_random_otp(length: int = 6) -> str:
    """Generate a random numeric OTP."""
    try:
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    except Exception as e:
        logger.error(f"Random OTP generation error: {e}")
        return "123456"  # Fallback for development


def is_super_admin(email: str, password: str) -> bool:
    """Check if credentials match super admin."""
    try:
        return (email.lower() == settings.super_admin_email.lower() and 
                password == settings.super_admin_password)
    except Exception as e:
        logger.error(f"Super admin verification error: {e}")
        return False


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh token valid for 7 days
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Refresh token creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating refresh token"
        )


def verify_refresh_token(token: str) -> str:
    """Verify refresh token and return email."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check token type
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        return email
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.JWTError as e:
        logger.warning(f"Refresh token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token"
        )
