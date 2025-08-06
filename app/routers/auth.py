# =============================================================================
# POORNASREE AI - AUTHENTICATION ROUTES
# =============================================================================

"""
Authentication endpoints for login, registration, and OTP verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

# Import from reorganized modules
from ..api import schemas
from ..services import email_service, user_service
from ..auth import auth, dependencies
from ..database.models import User, OTPVerification, LoginAttempt, AuditLog, EngineerApplication
from ..database.database import get_db
from ..core.constants import UserRole, UserStatus
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/login", response_model=schemas.LoginResponse)
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    ## 🔑 User Login
    
    Authenticate a user with email and password.
    
    **Request Body:**
    - `email`: User's email address
    - `password`: User's password
    
    **Returns:**
    - `access_token`: JWT token for authentication
    - `token_type`: Always "bearer"
    - `user`: User profile information
    
    **Example:**
    ```json
    {
      "email": "admin@poornasree.ai",
      "password": "Admin@2024"
    }
    ```
    
    **Success Response:**
    ```json
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "email": "admin@poornasree.ai",
        "role": "SUPER_ADMIN",
        "status": "ACTIVE"
      }
    }
    ```
    
    **Error Codes:**
    - `401`: Invalid credentials
    - `400`: Missing password
    - `423`: Account suspended
    """
    if not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for this login method"
        )
    
    # Get user by email
    user = user_service.get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not auth.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active or user.status not in [UserStatus.ACTIVE, UserStatus.APPROVED]:
        if user.status == UserStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is pending approval"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/request-otp")
async def request_otp(
    otp_request: schemas.OTPRequest,
    db: Session = Depends(get_db)
):
    """Request OTP for login or registration"""
    # Check if user exists for login
    if otp_request.purpose == "login":
        user = user_service.get_user_by_email(db, otp_request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only allow OTP login for admin and customer roles
        if user.role not in [UserRole.ADMIN, UserRole.CUSTOMER]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP login not supported for this user type"
            )
    
    # Generate OTP and send email
    otp_code = auth.generate_random_otp()
    
    # Create OTP verification record
    otp_verification = OTPVerification(
        email=otp_request.email,
        otp_code=otp_code,
        purpose=otp_request.purpose
    )
    db.add(otp_verification)
    db.commit()
    
    # Send OTP email
    if otp_request.purpose == "login":
        user = user_service.get_user_by_email(db, otp_request.email)
        await email_service.send_otp_email(user, otp_code)
    
    return {"message": "OTP sent successfully"}


@router.post("/verify-otp", response_model=schemas.LoginResponse)
async def verify_otp_login(
    otp_data: schemas.OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify OTP and login"""
    # Get OTP verification record
    otp_verification = db.query(OTPVerification).filter(
        OTPVerification.email == otp_data.email,
        OTPVerification.otp_code == otp_data.otp_code,
        OTPVerification.purpose == otp_data.purpose,
        OTPVerification.is_used == False
    ).first()
    
    if not otp_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp_verification.is_used = True
    db.commit()
    
    # Get user
    user = user_service.get_user_by_email(db, otp_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active or user.status not in [UserStatus.ACTIVE, UserStatus.APPROVED]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/register/customer", response_model=schemas.UserResponse)
async def register_customer(
    customer_data: schemas.CustomerRegistration,
    db: Session = Depends(get_db)
):
    """
    ## 👤 Register Customer Account
    
    Register a new customer account with email verification.
    
    **Request Body:**
    - `email`: Valid email address
    - `password`: Strong password (8+ chars, mixed case, numbers, symbols)
    - `first_name`: Customer's first name
    - `last_name`: Customer's last name
    - `phone_number`: Optional phone number
    - `otp_code`: Email verification code (get from `/request-otp`)
    
    **Process:**
    1. Request OTP: `POST /auth/request-otp` with `purpose: "registration"`
    2. Check email for verification code
    3. Register with OTP code
    
    **Example:**
    ```json
    {
      "email": "customer@example.com",
      "password": "SecurePass123!",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "otp_code": "123456"
    }
    ```
    
    **Returns:**
    - User profile with `CUSTOMER` role
    - Account status will be `ACTIVE`
    
    **Error Codes:**
    - `400`: Email already registered or invalid OTP
    - `422`: Validation errors (weak password, invalid email)
    """
    # Check if user already exists
    existing_user = user_service.get_user_by_email(db, customer_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify OTP
    otp_verification = db.query(OTPVerification).filter(
        OTPVerification.email == customer_data.email,
        OTPVerification.otp_code == customer_data.otp_code,
        OTPVerification.purpose == "registration",
        OTPVerification.is_used == False
    ).first()
    
    if not otp_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp_verification.is_used = True
    db.commit()
    
    # Create customer user
    user_data = schemas.UserCreate(
        email=customer_data.email,
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        phone_number=customer_data.phone_number,
        role=UserRole.CUSTOMER
    )
    
    user = user_service.create_user_account(db, user_data)
    user.is_verified = True
    user.status = UserStatus.ACTIVE
    db.commit()
    
    # Send welcome email
    await email_service.send_welcome_email(user)
    
    return user


@router.post("/register/engineer", response_model=schemas.UserResponse)
async def register_engineer(
    engineer_data: schemas.EngineerRegistration,
    db: Session = Depends(get_db)
):
    """Register engineer (requires admin approval)"""
    # Check if user already exists
    existing_user = user_service.get_user_by_email(db, engineer_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create engineer user with pending status
    user_data = schemas.UserCreate(
        email=engineer_data.email,
        first_name=engineer_data.first_name,
        last_name=engineer_data.last_name,
        phone_number=engineer_data.phone_number,
        password=engineer_data.password,
        role=UserRole.ENGINEER
    )
    
    user = user_service.create_user_account(db, user_data)
    user.status = UserStatus.PENDING
    db.commit()
    
    # Create engineer application
    engineer_app = EngineerApplication(
        user_id=user.id,
        experience_years=engineer_data.experience_years,
        skills=engineer_data.skills,
        previous_company=engineer_data.previous_company,
        portfolio_url=engineer_data.portfolio_url,
        cover_letter=engineer_data.cover_letter,
        status=UserStatus.PENDING
    )
    db.add(engineer_app)
    db.commit()
    
    # Send notification to admins
    admin_users = user_service.get_users_by_role(db, UserRole.ADMIN)
    admin_emails = [admin.email for admin in admin_users]
    if admin_emails:
        await email_service.send_engineer_application_notification(user, admin_emails)
    
    return user
