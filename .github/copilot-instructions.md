# GitHub Copilot Instructions for Poornasree AI Authentication System

## 🏗️ Project Overview

This is a **comprehensive FastAPI authentication system** with role-based access control, built for **Poornasree AI**. The system provides secure user management, OTP verification, email services, and admin functionality.

## 📁 Project Structure

```
psr-ai-api/
├── app/                          # Main application package
│   ├── api/                      # API layer
│   │   └── schemas.py           # Pydantic request/response models
│   ├── auth/                     # Authentication logic
│   │   ├── auth.py              # Password hashing, JWT tokens, OTP
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
│   │   ├── email_service.py     # Email/SMTP service
│   │   └── user_service.py      # User business logic
│   ├── templates/                # HTML templates
│   └── config.py                # Configuration management
├── alembic/                      # Database migrations
├── logs/                         # Application logs
├── main.py                       # FastAPI application entry point
├── init.py                       # Database setup script
├── system_check.py               # System status verification
└── requirements.txt              # Python dependencies
```

## 🎯 Key Technologies & Patterns

### **Framework & Architecture**
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM with async support
- **Alembic** - Database migrations
- **Pydantic** - Data validation & serialization
- **MySQL** - Primary database
- **Redis** - Caching layer

### **Authentication & Security**
- **JWT Tokens** - Bearer token authentication
- **bcrypt** - Password hashing
- **OTP Verification** - Email-based 2FA
- **Role-Based Access Control** - SUPER_ADMIN, ADMIN, ENGINEER, CUSTOMER
- **Rate Limiting** - Protection against brute force
- **Audit Logging** - Complete activity tracking

### **Design Patterns**
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic separation
- **Dependency Injection** - FastAPI dependencies
- **Factory Pattern** - Database session creation
- **Strategy Pattern** - Multiple authentication methods

## 🔑 Core Components

### **Database Models**
```python
# User roles and statuses
UserRole: SUPER_ADMIN | ADMIN | ENGINEER | CUSTOMER
UserStatus: PENDING | APPROVED | REJECTED | ACTIVE | INACTIVE | SUSPENDED

# Primary models
User                  # Main user entity
OTPVerification      # Email verification codes
EngineerApplication  # Engineer approval workflow
Notification         # In-app notifications
AuditLog            # Security audit trail
LoginAttempt        # Failed login tracking
```

### **Authentication Flow**
1. **Registration** → Email OTP → Account creation
2. **Login** → Password/OTP → JWT token
3. **Authorization** → Bearer token → Role checking
4. **Engineer Application** → Admin review → Approval/rejection

### **API Structure**
```
/api/v1/auth/*        # Public authentication endpoints
/api/v1/admin/*       # Admin-only management endpoints  
/api/v1/users/*       # User profile & notification endpoints
/health               # System health check
/docs                 # Swagger documentation
```

## 📝 Coding Guidelines

### **File Naming & Organization**
- Use snake_case for Python files
- Group related functionality in modules
- Separate concerns: routers → services → models
- Keep routers thin, business logic in services

### **Import Structure**
```python
# Standard library imports
from datetime import datetime
from typing import Optional, List

# Third-party imports  
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local imports
from ..api import schemas
from ..services import user_service
from ..database.models import User
from ..core.constants import UserRole
```

### **Error Handling**
```python
# Use FastAPI HTTPException for API errors
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Descriptive error message"
)

# Use try/catch for service layer
try:
    result = await some_operation()
except SomeException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### **Database Operations**
```python
# Always use dependency injection for DB sessions
def some_endpoint(db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, email)
    
# Use service layer for complex queries
def get_active_users(db: Session) -> List[User]:
    return db.query(User).filter(
        User.is_active == True,
        User.status == UserStatus.ACTIVE
    ).all()
```

### **Response Models**
```python
# Always define Pydantic schemas for responses
@router.get("/users", response_model=schemas.UserListResponse)
async def get_users():
    # Implementation
    
# Use examples in schemas
class LoginRequest(BaseSchema):
    email: EmailStr = Field(..., example="official.tishnu@gmail.com")
    password: str = Field(..., example="Access@404")
```

## 🔐 Authentication Patterns

### **Role-Based Decorators**
```python
# Use dependencies for role checking
@router.get("/admin/dashboard")
async def get_dashboard(
    current_user: User = Depends(require_super_admin)
):
    # Only SUPER_ADMIN can access
```

### **JWT Token Handling**
```python
# Token creation
access_token = auth.create_access_token(
    data={"sub": user.email}, 
    expires_delta=timedelta(minutes=30)
)

# Token validation
current_user = get_current_user(token)
```

### **OTP Verification**
```python
# Generate OTP for email verification
otp_code = generate_otp()
send_verification_email(email, otp_code)

# Verify OTP before account creation
verify_otp(email, otp_code, purpose="registration")
```

## 📧 Email Service Patterns

### **HTML Email Templates**
```python
# Use HTML templates for professional emails
template = f"""
<div style="font-family: Arial, sans-serif;">
    <h2>Welcome to Poornasree AI</h2>
    <p>Your verification code: <strong>{otp_code}</strong></p>
</div>
"""
```

### **Email Types**
- **Verification** - Account email confirmation
- **Welcome** - New user onboarding
- **Application** - Engineer application status
- **Notification** - System alerts

## 🛡️ Security Best Practices

### **Input Validation**
```python
# Always validate input with Pydantic
class UserCreate(BaseSchema):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)")
```

### **Password Security**
```python
# Use bcrypt for password hashing
hashed_password = get_password_hash(plain_password)
is_valid = verify_password(plain_password, hashed_password)
```

### **Rate Limiting & Audit**
```python
# Track login attempts
login_attempt = LoginAttempt(
    email=email,
    ip_address=request.client.host,
    success=success,
    failure_reason=reason if not success else None
)

# Log important actions
audit_log = AuditLog(
    user_id=current_user.id,
    action="USER_CREATED",
    entity_type="User",
    details=f"Created user {new_user.email}"
)
```

## 🧪 Testing Patterns

### **Endpoint Testing**
```python
# Test authentication endpoints
def test_login_success():
    response = client.post("/api/v1/auth/login", json={
        "email": "official.tishnu@gmail.com",
        "password": "Access@404"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### **Database Testing**
```python
# Use test database for isolation
@pytest.fixture
def test_db():
    # Create test database session
    # Run tests
    # Cleanup
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
    """
```

### **Code Comments**
```python
# Use descriptive comments for complex logic
def complex_business_logic():
    """
    Handle complex user approval workflow.
    
    Steps:
    1. Validate engineer application
    2. Check admin permissions  
    3. Update user status
    4. Send notification email
    5. Log audit trail
    """
```

## 🚀 Deployment & Operations

### **Environment Configuration**
```python
# Use .env for configuration
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/poornasree_ai
SECRET_KEY=your-secret-key
SMTP_HOST=smtp.gmail.com
```

### **Database Management**
```python
# Use Alembic for migrations
alembic revision --autogenerate -m "Add new table"
alembic upgrade head

# Use init.py for initial setup
python init.py  # Create database, tables, super admin
```

### **Monitoring & Health**
```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "database": "connected"
    }
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
