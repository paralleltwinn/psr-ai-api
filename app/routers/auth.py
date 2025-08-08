# =============================================================================
# POORNASREE AI - AUTHENTICATION ROUTES
# =============================================================================

"""
Authentication endpoints for login, registration, and OTP verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

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
      "email": "official.tishnu@gmail.com",
      "password": "Access@404"
    }
    ```
    
    **Success Response:**
    ```json
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "email": "official.tishnu@gmail.com",
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
    
    # Check if user exists
    existing_user = user_service.get_user_by_email(db, otp_request.email)
    
    if otp_request.purpose == "login":
        # For login, user must exist
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only allow OTP login for admin and customer roles
        if existing_user.role not in [UserRole.ADMIN, UserRole.CUSTOMER]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP login not supported for this user type"
            )
    
    elif otp_request.purpose == "registration":
        # For registration, user should not exist
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists. Please use login instead."
            )
    
    # Clean up any existing unused OTPs for this email and purpose
    db.query(OTPVerification).filter(
        OTPVerification.email == otp_request.email,
        OTPVerification.purpose == otp_request.purpose,
        OTPVerification.is_used == False
    ).delete()
    
    # Generate OTP and send email
    otp_code = auth.generate_random_otp()
    
    # Create OTP verification record with expiration (15 minutes from now)
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    otp_verification = OTPVerification(
        email=otp_request.email,
        otp_code=otp_code,
        purpose=otp_request.purpose,
        expires_at=expires_at
    )
    db.add(otp_verification)
    db.commit()
    
    # Send OTP email
    if otp_request.purpose == "login":
        await email_service.send_otp_email(existing_user, otp_code, purpose="login")
    elif otp_request.purpose == "registration":
        # For registration, create a temporary user object for email sending
        temp_user = User(
            email=otp_request.email,
            first_name="User",  # We don't have the name yet for registration
            last_name=""
        )
        await email_service.send_otp_email(temp_user, otp_code, purpose="registration")
    
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
    
    Register a new customer account with simplified fields and email verification.
    
    **Request Body:**
    - `email`: Valid email address
    - `first_name`: Customer's first name
    - `last_name`: Customer's last name
    - `machine_model`: Machine model used by customer
    - `state`: State/Province of customer
    - `phone_number`: Customer phone number
    - `otp_code`: Email verification code (get from `/request-otp`)
    
    **Process:**
    1. Request OTP: `POST /auth/request-otp` with `purpose: "registration"`
    2. Check email for verification code
    3. Register with OTP code
    
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
    
    **Returns:**
    - User profile with `CUSTOMER` role
    - Account status will be `ACTIVE`
    
    **Error Codes:**
    - `400`: Email already registered with an active account or invalid OTP
    - `422`: Validation errors (invalid email)
    
    **Note:** If a user previously registered but has PENDING status, 
    they can register again to update their details.
    """
    # Check if user already exists
    existing_user = user_service.get_user_by_email(db, customer_data.email)
    if existing_user:
        # Allow update in these cases:
        # 1. Registration was incomplete (no machine_model/state)
        # 2. User status is PENDING (allows re-registration with updated details)
        can_update = (
            existing_user.machine_model is None or 
            existing_user.state is None or 
            existing_user.status == UserStatus.PENDING
        )
        
        if can_update:
            # Update the existing user with complete information
            existing_user.first_name = customer_data.first_name
            existing_user.last_name = customer_data.last_name
            existing_user.phone_number = customer_data.phone_number
            existing_user.machine_model = customer_data.machine_model
            existing_user.state = customer_data.state
            existing_user.status = UserStatus.ACTIVE
            db.commit()
            db.refresh(existing_user)
            
            # Send welcome email
            await email_service.send_welcome_email(existing_user)
            
            return existing_user
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered with an active account"
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
    
    # Create customer user with new fields
    user_data = schemas.UserCreate(
        email=customer_data.email,
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        phone_number=customer_data.phone_number,
        role=UserRole.CUSTOMER
    )
    
    user = user_service.create_user_account(db, user_data)
    
    # Add customer-specific fields
    user.machine_model = customer_data.machine_model
    user.state = customer_data.state
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
    """
    ## ⚙️ Register Engineer Account
    
    Submit engineer application with simplified fields (requires admin approval).
    
    **Request Body:**
    - `email`: Valid email address
    - `first_name`: Engineer's first name
    - `last_name`: Engineer's last name
    - `phone_number`: Engineer's phone number
    - `department`: Department/Specialization
    - `dealer`: Dealer/Company (optional)
    - `state`: State/Province
    
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
    
    **Returns:**
    - User profile with `ENGINEER` role
    - Account status will be `PENDING` until admin approval
    
    **Error Codes:**
    - `400`: Email already registered with an active account
    - `422`: Validation errors
    
    **Note:** If an engineer previously applied but has PENDING status, 
    they can apply again to update their details.
    """
    # Check if user already exists
    existing_user = user_service.get_user_by_email(db, engineer_data.email)
    if existing_user:
        # Allow re-registration if status is PENDING (allows updating details)
        if existing_user.status == UserStatus.PENDING and existing_user.role == UserRole.ENGINEER:
            # Update the existing engineer with new information
            existing_user.first_name = engineer_data.first_name
            existing_user.last_name = engineer_data.last_name
            existing_user.phone_number = engineer_data.phone_number
            existing_user.department = engineer_data.department
            existing_user.dealer = engineer_data.dealer
            existing_user.state = engineer_data.state
            existing_user.status = UserStatus.PENDING  # Keep as pending for admin approval
            db.commit()
            db.refresh(existing_user)
            
            # Update or create engineer application
            engineer_app = db.query(EngineerApplication).filter(
                EngineerApplication.user_id == existing_user.id
            ).first()
            
            if engineer_app:
                engineer_app.status = UserStatus.PENDING
                engineer_app.updated_at = datetime.utcnow()
            else:
                engineer_app = EngineerApplication(
                    user_id=existing_user.id,
                    status=UserStatus.PENDING
                )
                db.add(engineer_app)
            
            db.commit()
            
            # Send notification to admins about updated application
            admin_users = user_service.get_users_by_role(db, UserRole.ADMIN)
            admin_emails = [admin.email for admin in admin_users]
            if admin_emails:
                await email_service.send_engineer_application_notification(existing_user, admin_emails)
            
            return existing_user
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered with an active account"
            )
    
    # Create engineer user with pending status
    user_data = schemas.UserCreate(
        email=engineer_data.email,
        first_name=engineer_data.first_name,
        last_name=engineer_data.last_name,
        phone_number=engineer_data.phone_number,
        role=UserRole.ENGINEER
    )
    
    user = user_service.create_user_account(db, user_data)
    
    # Add engineer-specific fields
    user.department = engineer_data.department
    user.dealer = engineer_data.dealer
    user.state = engineer_data.state
    user.status = UserStatus.PENDING
    db.commit()
    
    # Create simplified engineer application
    engineer_app = EngineerApplication(
        user_id=user.id,
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


@router.get("/check-login-method/{email}", response_model=schemas.LoginMethodResponse)
async def check_login_method(
    email: str,
    db: Session = Depends(get_db)
):
    """
    ## 🔍 Check User Login Method
    
    Check whether a user requires password or OTP login.
    
    **Parameters:**
    - `email`: User's email address to check
    
    **Returns:**
    - `requires_password`: True if user has a password set
    - `user_role`: User's role if found
    - `user_exists`: True if user exists in system
    
    **Example:**
    ```json
    {
      "requires_password": true,
      "user_role": "super_admin",
      "user_exists": true
    }
    ```
    """
    user = user_service.get_user_by_email(db, email)
    
    if not user:
        return schemas.LoginMethodResponse(
            requires_password=False,
            user_role=None,
            user_exists=False
        )
    
    # Check if user has a password set
    has_password = user.hashed_password is not None and len(user.hashed_password) > 0
    
    return schemas.LoginMethodResponse(
        requires_password=has_password,
        user_role=user.role.value if user.role else None,
        user_exists=True
    )
