# GitHub Copilot Instructions for Poornasree AI Authentication System

## 🏗️ Project Overview

This is a **comprehensive FastAPI authentication system** with role-based access control, built for **Poornasree AI**. The system provides secure user management, OTP verification, email services, and admin functionality with enterprise-grade security features.

## 📁 Project Structure

```
psr-ai-api/
├── app/                          # Main application package
│   ├── api/                      # API layer
│   │   └── schemas.py           # Pydantic request/response models
│   ├── auth/                     # Authentication logic
│   │   ├── auth.py              # Password hashing, JWT tokens, OTP generation
│   │   └── dependencies.py      # Auth dependencies & middleware
│   ├── core/                     # Core utilities
│   │   ├── constants.py         # Enums (UserRole, UserStatus, etc.)
│   │   └── logging.py           # Logging configuration
│   ├── database/                 # Database layer
│   │   ├── database.py          # SQLAlchemy setup & session management
│   │   └── models.py            # Database models (User, OTP, etc.)
│   ├── routers/                  # API endpoints
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── admin.py             # Admin management endpoints
│   │   └── users.py             # User profile endpoints
│   ├── services/                 # Business logic
│   │   ├── email_service.py     # Email/SMTP service with HTML templates
│   │   └── user_service.py      # User business logic & application management
│   ├── templates/                # HTML email templates
│   └── config.py                # Configuration management with Pydantic Settings
├── alembic/                      # Database migrations
├── logs/                         # Application logs
├── main.py                       # FastAPI application entry point
├── init.py                       # Database setup script
├── system_check.py               # System status verification
└── requirements.txt              # Python dependencies
```

## 🎯 Key Technologies & Patterns

### **Framework & Architecture**
- **FastAPI 0.104+** - Modern async web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0** - Async ORM with declarative models
- **Alembic** - Database migration management
- **Pydantic v2** - Data validation & serialization with enhanced performance
- **MySQL 8.0** - Primary database with strict foreign key constraints
- **Redis** - Caching layer for session management and rate limiting

### **Authentication & Security**
- **JWT Tokens** - Bearer token authentication with configurable expiration
- **bcrypt** - Password hashing with salt rounds
- **OTP Verification** - Time-based email verification with expiration
- **Role-Based Access Control** - SUPER_ADMIN, ADMIN, ENGINEER, CUSTOMER hierarchy
- **Session Management** - Secure token storage with automatic cleanup
- **Audit Logging** - Complete activity tracking with IP and user agent capture

### **Design Patterns**
- **Repository Pattern** - Data access abstraction through service layer
- **Service Layer** - Business logic separation from API endpoints
- **Dependency Injection** - FastAPI dependencies for clean separation
- **Factory Pattern** - Database session creation and management
- **Strategy Pattern** - Multiple authentication methods (password/OTP)
- **Observer Pattern** - Email notifications for user actions

## 🔑 Core Components

### **Database Models**
```python
# User roles and statuses
UserRole: SUPER_ADMIN | ADMIN | ENGINEER | CUSTOMER
UserStatus: PENDING | APPROVED | REJECTED | ACTIVE | INACTIVE | SUSPENDED

# Primary models with relationships
User                  # Main user entity with role-specific fields
├── Customer fields   # machine_model, state
├── Engineer fields   # department, dealer
└── Profile fields    # phone_number, profile_picture

OTPVerification      # Email verification codes with expiration
├── purpose          # login, registration, password_reset
├── attempts         # Security tracking
└── expires_at       # Time-based validation

EngineerApplication  # Engineer approval workflow
├── application      # department, experience, skills, portfolio
├── review           # status, reviewer, notes, review_date
└── audit trail      # created_at, updated_at

Notification         # In-app notifications system
├── metadata         # title, message, type
├── relationships    # sender_id, recipient_id
└── read status      # is_read, read_at

AuditLog            # Security audit trail
├── action tracking  # user_id, action, entity_type, entity_id
├── request data     # ip_address, user_agent
└── details          # JSON metadata, timestamp

LoginAttempt        # Failed login tracking
├── attempt data     # email, ip_address, user_agent
├── outcome          # success, failure_reason
└── timestamp        # created_at for rate limiting
```

### **Authentication Flow**
1. **Registration** → Email OTP verification → Account creation → Role assignment
2. **Login** → Credential validation → JWT token generation → Role-based access
3. **Authorization** → Bearer token validation → User role checking → Endpoint access
4. **Engineer Application** → Admin review workflow → Approval/rejection → Email notifications
5. **Session Management** → Token expiration → Automatic refresh → Secure logout

### **API Structure**
```
/api/v1/auth/*              # Public authentication endpoints
├── /login                  # Password-based authentication
├── /request-otp           # OTP request for login/registration
├── /verify-otp            # OTP verification and login
├── /register/customer     # Customer registration with OTP
├── /register/engineer     # Engineer application submission
└── /check-login-method    # Check user's available login methods

/api/v1/admin/*            # Admin-only management endpoints  
├── /dashboard             # Super admin dashboard statistics
├── /stats                 # Admin dashboard statistics
├── /engineers/pending     # Pending engineer applications
├── /engineers/{id}/approve # Approve engineer application
├── /engineers/{id}/reject  # Reject engineer application
├── /create-admin          # Create new admin user
└── /admins                # List all admin users

/api/v1/users/*           # User profile & notification endpoints
├── /me                   # Current user profile
├── /notifications        # User notifications
└── /notifications/{id}/read # Mark notification as read

/health                   # System health check endpoint
/docs                     # Swagger/OpenAPI documentation
/redoc                    # ReDoc API documentation
```

## 📝 Coding Guidelines

### **File Naming & Organization**
- Use snake_case for Python files and modules
- Group related functionality in logical modules
- Separate concerns: routers → services → models → database
- Keep routers thin, business logic in services
- Use clear, descriptive names for functions and variables

### **Import Structure**
```python
# Standard library imports (alphabetical)
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Third-party imports (alphabetical)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, EmailStr, Field

# Local imports (structured hierarchy)
from ..api import schemas
from ..services import user_service, email_service
from ..database.models import User, EngineerApplication
from ..database.database import get_db
from ..auth.dependencies import require_admin_or_above, get_current_active_user
from ..core.constants import UserRole, UserStatus, NotificationType
from ..config import settings
```

### **Error Handling & Logging**
```python
# Use FastAPI HTTPException for API errors with descriptive messages
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered with an active account"
)

# Comprehensive try/catch blocks with proper logging
try:
    result = await complex_operation()
    logger.info(f"Operation completed successfully: {result}")
    return result
except SpecificException as e:
    logger.error(f"Specific operation failed: {e}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Operation failed: {str(e)}"
    )
except Exception as e:
    logger.error(f"Unexpected error in operation: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error occurred"
    )
```

### **Database Operations & Service Layer**
```python
# Always use dependency injection for DB sessions
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_all_users()

# Implement complex queries in service layer with proper error handling
class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_pending_engineers(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get pending engineer applications with related data."""
        try:
            return self.db.query(User).join(EngineerApplication).filter(
                User.role == UserRole.ENGINEER,
                User.status == UserStatus.PENDING,
                EngineerApplication.status == UserStatus.PENDING
            ).options(joinedload(User.engineer_applications)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching pending engineers: {e}")
            raise HTTPException(status_code=500, detail="Database query failed")
```

### **Response Models & Validation**
```python
# Always define comprehensive Pydantic schemas for requests and responses
@router.post("/register/customer", response_model=schemas.UserResponse)
async def register_customer(
    customer_data: schemas.CustomerRegistration,
    db: Session = Depends(get_db)
):
    """Register new customer with OTP verification."""
    # Implementation with proper validation
    
# Use detailed examples and validation in schemas
class CustomerRegistration(BaseSchema):
    email: EmailStr = Field(..., example="customer@example.com", description="Customer email address")
    first_name: str = Field(..., min_length=1, max_length=100, example="John")
    last_name: str = Field(..., min_length=1, max_length=100, example="Doe")
    machine_model: str = Field(..., min_length=1, max_length=200, example="Model X1")
    state: str = Field(..., min_length=1, max_length=100, example="California")
    phone_number: str = Field(..., max_length=20, example="+1234567890")
    otp_code: str = Field(..., min_length=6, max_length=6, example="123456")
```

## 🔐 Authentication Patterns

### **Role-Based Access Control**
```python
# Use dependency injection for role checking with granular permissions
@router.get("/admin/dashboard")
async def get_dashboard(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Only SUPER_ADMIN can access dashboard statistics."""
    
@router.put("/engineers/{engineer_id}/approve")
async def approve_engineer(
    engineer_id: int,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """ADMIN and SUPER_ADMIN can approve engineers."""

# Multiple role checking patterns
async def require_admin_or_above(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### **JWT Token Management**
```python
# Token creation with proper expiration and metadata
access_token = auth.create_access_token(
    data={"sub": user.email, "role": user.role.value}, 
    expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
)

# Token validation with comprehensive error handling
def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token validation failed")
```

### **OTP Verification & Email Integration**
```python
# Generate secure OTP with expiration tracking
def generate_otp() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(6))

# OTP verification with attempt limiting
async def verify_otp(db: Session, email: str, otp_code: str, purpose: str) -> bool:
    verification = db.query(OTPVerification).filter(
        OTPVerification.email == email,
        OTPVerification.otp_code == otp_code,
        OTPVerification.purpose == purpose,
        OTPVerification.is_used == False,
        OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not verification:
        return False
    
    # Mark as used and track attempts
    verification.is_used = True
    verification.attempts += 1
    db.commit()
    return True

# Send OTP with professional email templates
await email_service.send_otp_email(
    to_email=email, 
    otp_code=otp_code, 
    purpose=purpose,
    user_name=f"{user.first_name} {user.last_name}"
)
```

## 📧 Email Service Patterns

### **HTML Email Templates**
```python
# Professional HTML email templates with consistent branding
def create_otp_email_template(user_name: str, otp_code: str, purpose: str) -> str:
    """Create HTML template for OTP verification emails."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Poornasree AI - Verification Code</title>
        <style>
            .email-container {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 600px; margin: 0 auto; padding: 20px;
                background-color: #f8f9fa; border-radius: 8px;
            }}
            .otp-code {{ 
                background-color: #007bff; color: white; 
                padding: 15px 30px; font-size: 24px; font-weight: bold;
                letter-spacing: 3px; border-radius: 6px; text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <h2>Hello {user_name},</h2>
            <p>Your verification code for {purpose}:</p>
            <div class="otp-code">{otp_code}</div>
            <p><strong>This code expires in 5 minutes.</strong></p>
        </div>
    </body>
    </html>
    """

# Comprehensive email service with error handling and logging
class EmailService:
    async def send_otp_email(self, to_email: str, otp_code: str, purpose: str, user_name: str) -> bool:
        try:
            html_content = create_otp_email_template(user_name, otp_code, purpose)
            subject = f"Poornasree AI - Your {purpose.title()} Code: {otp_code}"
            
            success = self.send_email(to_email, subject, html_content)
            if success:
                logger.info(f"OTP email sent successfully to {to_email}")
            return success
        except Exception as e:
            logger.error(f"Failed to send OTP email to {to_email}: {e}")
            return False
```

### **Email Notification Types**
- **OTP Verification** - Account email confirmation with secure codes
- **Welcome Messages** - New user onboarding with brand introduction
- **Engineer Applications** - Application status updates with admin notifications
- **Admin Notifications** - System alerts and user management updates
- **Security Alerts** - Login attempts and account security notifications

## 🛡️ Security Best Practices

### **Input Validation & Sanitization**
```python
# Comprehensive Pydantic validation with security constraints
class UserRegistration(BaseSchema):
    email: EmailStr = Field(
        ..., 
        max_length=320, 
        description="Valid email address with domain validation"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
        description="Strong password with mixed case, numbers, and special characters"
    )
    first_name: str = Field(..., min_length=1, max_length=100, regex=r"^[a-zA-Z\s'-]+$")
    phone_number: str = Field(..., regex=r"^\+?[1-9]\d{1,14}$", description="Valid international phone number")

# SQL injection prevention with parameterized queries
def get_user_by_email_secure(db: Session, email: str) -> Optional[User]:
    """Secure user lookup with parameterized query."""
    return db.query(User).filter(User.email == email.lower().strip()).first()
```

### **Password Security & Hashing**
```python
# Advanced password hashing with bcrypt salt rounds
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # Higher security with more rounds
)

def get_password_hash(password: str) -> str:
    """Hash password with secure bcrypt algorithm."""
    try:
        # Additional validation before hashing
        if len(password) < 8 or len(password) > 100:
            raise ValueError("Password length invalid")
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise HTTPException(status_code=500, detail="Security processing error")

def verify_password_secure(plain_password: str, hashed_password: str) -> bool:
    """Verify password with timing attack protection."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Password verification attempt failed: {e}")
        return False
```

### **Rate Limiting & Attack Prevention**
```python
# Login attempt tracking with automatic lockout
class SecurityService:
    def track_login_attempt(self, email: str, ip_address: str, success: bool, reason: str = None):
        """Track login attempts for security monitoring."""
        attempt = LoginAttempt(
            email=email.lower(),
            ip_address=ip_address,
            user_agent=request.headers.get("User-Agent", "Unknown"),
            success=success,
            failure_reason=reason if not success else None,
            created_at=datetime.utcnow()
        )
        self.db.add(attempt)
        self.db.commit()
        
        # Check for brute force attempts
        if not success:
            recent_failures = self.db.query(LoginAttempt).filter(
                LoginAttempt.email == email.lower(),
                LoginAttempt.success == False,
                LoginAttempt.created_at > datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            if recent_failures >= 5:
                logger.warning(f"Potential brute force attack on {email} from {ip_address}")
                # Implement temporary account lockout or enhanced security measures

# Audit logging for security-critical operations
def log_security_event(user_id: int, action: str, details: str, ip_address: str):
    """Log security-critical events for audit trail."""
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type="Security",
        details=details,
        ip_address=ip_address,
        user_agent=request.headers.get("User-Agent"),
        created_at=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()
```

### **Session Management & Token Security**
```python
# Secure JWT token creation with role-based claims
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create secure JWT token with comprehensive claims."""
    to_encode = data.copy()
    now = datetime.utcnow()
    
    # Add security claims
    to_encode.update({
        "exp": now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes)),
        "iat": now,
        "nbf": now,  # Not before claim
        "iss": "poornasree-ai",  # Issuer
        "aud": "poornasree-ai-frontend",  # Audience
        "type": "access",
        "jti": str(uuid.uuid4())  # JWT ID for token tracking
    })
    
    try:
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication token generation failed")

# Token blacklisting for logout security
async def invalidate_token(token: str, user_id: int):
    """Add token to blacklist for secure logout."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        jti = payload.get("jti")
        
        # Store in Redis blacklist with expiration
        await redis_client.setex(f"blacklist:{jti}", 
                               settings.access_token_expire_minutes * 60, 
                               user_id)
    except Exception as e:
        logger.error(f"Token invalidation failed: {e}")
```

## 🧪 Testing Patterns

### **API Endpoint Testing**
```python
# Comprehensive authentication endpoint testing
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
    """Create test client with isolated database."""
    return TestClient(app)

def test_login_success(test_client):
    """Test successful user login with valid credentials."""
    response = test_client.post("/api/v1/auth/login", json={
        "email": "official.tishnu@gmail.com",
        "password": "Access@404"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "super_admin"

def test_login_invalid_credentials(test_client):
    """Test login failure with invalid credentials."""
    response = test_client.post("/api/v1/auth/login", json={
        "email": "invalid@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_otp_verification_flow(test_client):
    """Test complete OTP verification workflow."""
    # Request OTP
    otp_response = test_client.post("/api/v1/auth/request-otp", json={
        "email": "test@example.com",
        "purpose": "registration"
    })
    assert otp_response.status_code == 200
    
    # Verify OTP (mock OTP code for testing)
    verify_response = test_client.post("/api/v1/auth/verify-otp", json={
        "email": "test@example.com",
        "otp_code": "123456",  # Mock OTP
        "purpose": "registration"
    })
    assert verify_response.status_code == 200
```

### **Database Testing & Fixtures**
```python
# Database testing with proper isolation
@pytest.fixture
def test_db():
    """Create isolated test database session."""
    engine = create_engine(settings.test_database_url)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user(test_db):
    """Create sample user for testing."""
    user = User(
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        role=UserRole.CUSTOMER,
        status=UserStatus.ACTIVE,
        hashed_password=get_password_hash("testpassword123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

def test_user_service_operations(test_db, sample_user):
    """Test user service CRUD operations."""
    service = UserService(test_db)
    
    # Test user retrieval
    found_user = service.get_user_by_email("testuser@example.com")
    assert found_user is not None
    assert found_user.email == sample_user.email
    
    # Test user update
    service.update_user_profile(found_user.id, {"first_name": "Updated"})
    updated_user = service.get_user_by_id(found_user.id)
    assert updated_user.first_name == "Updated"
```

### **Security Testing**
```python
# Security-focused testing patterns
def test_sql_injection_protection(test_client):
    """Test protection against SQL injection attacks."""
    malicious_email = "test'; DROP TABLE users; --"
    response = test_client.post("/api/v1/auth/login", json={
        "email": malicious_email,
        "password": "anypassword"
    })
    # Should not cause internal server error, should handle gracefully
    assert response.status_code in [400, 401, 422]

def test_rate_limiting(test_client):
    """Test rate limiting on authentication endpoints."""
    failed_attempts = 0
    for _ in range(10):  # Attempt multiple failed logins
        response = test_client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        if response.status_code == 429:  # Too Many Requests
            break
        failed_attempts += 1
    
    # Should trigger rate limiting before 10 attempts
    assert failed_attempts < 10

def test_jwt_token_validation(test_client):
    """Test JWT token validation and expiration."""
    # Test with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    
    # Test with expired token (mock expired token)
    expired_token = create_access_token(
        data={"sub": "test@example.com"}, 
        expires_delta=timedelta(seconds=-1)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = test_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
```

## 📊 Documentation Standards

### **Swagger Documentation**
```python
@router.post("/login", response_model=schemas.LoginResponse)
async def login(login_data: schemas.LoginRequest):
    """
    ## 🔑 User Login
    
    Authenticate user with email and password.
    
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
        "role": "super_admin",
        "status": "active"
      },
      "expires_in": 1800
    }
    ```
    
    **Error Codes:**
    - `401`: Invalid credentials or account not active
    - `400`: Missing required fields
    - `423`: Account suspended or pending approval
    """
```

### **Code Comments & Docstrings**
```python
def complex_business_logic(user_id: int, application_data: dict) -> bool:
    """
    Handle complex engineer application approval workflow.
    
    This function manages the complete engineer application process including:
    - Validation of application data
    - Admin permission checks
    - Status updates with audit trail
    - Email notifications to relevant parties
    - Database transaction management
    
    Args:
        user_id (int): ID of the user applying as engineer
        application_data (dict): Application details including department, experience, etc.
        
    Returns:
        bool: True if application processed successfully, False otherwise
        
    Raises:
        HTTPException: 400 if validation fails, 403 if insufficient permissions,
                      500 if database operation fails
                      
    Example:
        >>> success = complex_business_logic(123, {
        ...     "department": "Software Engineering",
        ...     "experience": "5 years",
        ...     "skills": "Python, FastAPI, React"
        ... })
        >>> assert success == True
    """
    # Step 1: Validate engineer application data
    if not _validate_application_data(application_data):
        logger.error(f"Invalid application data for user {user_id}")
        raise HTTPException(status_code=400, detail="Invalid application data")
    
    # Step 2: Check admin permissions for approval
    # ... rest of implementation
```

### **Pydantic Schema Documentation**
```python
class EngineerRegistration(BaseSchema):
    """
    Schema for engineer registration with comprehensive validation.
    
    Engineers must apply and be approved by administrators before gaining access.
    All fields are required and validated according to business rules.
    """
    
    email: EmailStr = Field(
        ..., 
        description="Professional email address for communication",
        example="engineer@company.com"
    )
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Engineer's first name",
        example="John"
    )
    department: str = Field(
        ...,
        description="Engineering department or specialization",
        example="Software Engineering",
        regex=r"^[a-zA-Z\s&-]+$"
    )
    experience: str = Field(
        ...,
        description="Years of relevant engineering experience",
        example="5+ years",
        max_length=50
    )
    
    @validator('department')
    def validate_department(cls, v):
        """Ensure department is from approved list."""
        approved_departments = [
            "Software Engineering", "Mechanical Engineering", 
            "Electrical Engineering", "Civil Engineering"
        ]
        if v not in approved_departments:
            raise ValueError(f"Department must be one of: {', '.join(approved_departments)}")
        return v
```

## 🚀 Deployment & Operations

### **Environment Configuration**
```python
# Use .env for configuration with validation
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/poornasree_ai
SECRET_KEY=your-secret-key-min-32-chars
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SUPER_ADMIN_EMAIL=official.tishnu@gmail.com
SUPER_ADMIN_PASSWORD=Access@404
REDIS_URL=redis://localhost:6379
FRONTEND_URL=http://localhost:3000

# Pydantic Settings validation
class Settings(BaseSettings):
    database_url: str
    secret_key: str = Field(..., min_length=32)
    smtp_host: str
    super_admin_email: EmailStr
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### **Database Management**
```python
# Use Alembic for migrations with proper versioning
alembic revision --autogenerate -m "Add engineer application tracking"
alembic upgrade head
alembic downgrade -1  # Rollback if needed

# Use init.py for initial setup and seeding
def create_super_admin():
    """Create default super admin user."""
    existing_admin = db.query(User).filter(
        User.email == settings.super_admin_email
    ).first()
    
    if not existing_admin:
        admin_user = User(
            email=settings.super_admin_email,
            hashed_password=get_password_hash(settings.super_admin_password),
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        logger.info("Super admin created successfully")

# Database health checks
async def check_database_health() -> bool:
    """Check database connectivity and basic operations."""
    try:
        # Test basic query
        result = await database.fetch_one("SELECT 1 as health_check")
        return result["health_check"] == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
```

### **Monitoring & Health Checks**
```python
# Comprehensive health check endpoint
@app.get("/health")
async def health_check():
    """
    System health check with detailed component status.
    
    Returns service health including database connectivity,
    email service status, and Redis cache availability.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "components": {}
    }
    
    # Check database
    try:
        db_healthy = await check_database_health()
        health_status["components"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "connection": "active" if db_healthy else "failed"
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Redis cache
    try:
        await redis_client.ping()
        health_status["components"]["cache"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check email service
    try:
        email_service = EmailService()
        email_healthy = email_service.check_smtp_connection()
        health_status["components"]["email"] = {
            "status": "healthy" if email_healthy else "degraded"
        }
    except Exception as e:
        health_status["components"]["email"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Overall status
    component_statuses = [comp["status"] for comp in health_status["components"].values()]
    if "unhealthy" in component_statuses:
        health_status["status"] = "unhealthy"
    elif "degraded" in component_statuses:
        health_status["status"] = "degraded"
    
    return health_status

# Performance monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header for performance monitoring."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### **Logging & Observability**
```python
# Structured logging configuration
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", 
                          "pathname", "filename", "module", "lineno", 
                          "funcName", "created", "msecs", "relativeCreated", 
                          "thread", "threadName", "processName", "process",
                          "getMessage", "exc_info", "exc_text", "stack_info"]:
                log_entry[key] = value
        
        return json.dumps(log_entry)

# Application logging setup
def setup_logging():
    """Configure application logging with JSON formatter."""
    formatter = JSONFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(settings.log_file)
    file_handler.setFormatter(formatter)
    
    # Root logger configuration
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        handlers=[console_handler, file_handler]
    )
    
    # Disable noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
```

## 🔧 Development Workflow

### **Adding New Features**
1. **Define Schema** → Add Pydantic models in `schemas.py`
2. **Create Database Model** → Add SQLAlchemy model in `models.py`
3. **Implement Service** → Add business logic in appropriate service
4. **Create Router** → Add API endpoints with proper documentation
5. **Add Tests** → Write comprehensive tests
6. **Update Documentation** → Update API docs and README

### **Code Review Checklist**
- ✅ Proper error handling with descriptive messages
- ✅ Input validation with Pydantic schemas
- ✅ Authentication/authorization checks
- ✅ Swagger documentation with examples
- ✅ Database operations use service layer
- ✅ Sensitive data not logged
- ✅ Rate limiting considered
- ✅ Audit logging for important actions

## 🎯 Common Patterns to Follow

### **Service Layer Pattern**
```python
# user_service.py
def create_user(db: Session, user_data: UserCreate) -> User:
    """Create new user with proper validation."""
    # Business logic here
    
# auth.py router
@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user_data)
```

### **Dependency Injection**
```python
# dependencies.py
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Token validation logic
    
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

### **Response Consistency**
```python
# Always use consistent response formats
{
    "success": true,
    "data": { ... },
    "message": "Operation successful"
}

# For errors
{
    "success": false, 
    "error": "Error description",
    "code": "ERROR_CODE"
}
```

---

## 🎉 Project Goals

This authentication system provides:
- 🔐 **Secure Authentication** - JWT + OTP + Role-based access
- 👥 **User Management** - Complete lifecycle management
- 📧 **Email Integration** - Professional email communications  
- ⚙️ **Admin Dashboard** - Comprehensive system management
- 📊 **Audit & Monitoring** - Complete activity tracking
- 🚀 **Scalable Architecture** - Clean, maintainable codebase

**Remember**: Always prioritize security, maintainability, and comprehensive documentation in your code!
