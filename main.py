# =============================================================================
# POORNASREE AI - MAIN APPLICATION
# =============================================================================

"""
FastAPI main application with modular architecture and comprehensive authentication.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import from reorganized modules
from app.database.database import database, Base, engine
from app.routers import auth_router, admin_router, users_router
from app.routers.ai import router as ai_router
from app.routers.database import router as database_router
from app.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Poornasree AI FastAPI application...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Connect to database
    await database.connect()
    logger.info("Database connected successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    await database.disconnect()
    logger.info("Database disconnected")


# Create FastAPI app with comprehensive documentation
app = FastAPI(
    title="🚀 Poornasree AI Authentication API",
    version=settings.app_version,
    description="""
## 🔐 Comprehensive Authentication System

**Poornasree AI** provides a robust, role-based authentication system with advanced security features.

### 🎯 Key Features

* **🔑 JWT Authentication** - Secure token-based authentication
* **👥 Role-Based Access Control** - SUPER_ADMIN, ADMIN, ENGINEER, CUSTOMER roles
* **📧 Email Verification** - Secure email-based account verification
* **📱 OTP Authentication** - Two-factor authentication support
* **🛡️ Security Features** - Rate limiting, login attempt tracking, audit logs
* **⚙️ Engineer Applications** - Streamlined engineer onboarding process
* **📊 Admin Dashboard** - Comprehensive user and system management

### 🏗️ Architecture

* **FastAPI** - Modern, fast web framework
* **SQLAlchemy** - Powerful ORM with MySQL database
* **Alembic** - Database migration management
* **JWT Tokens** - Secure authentication tokens
* **Email Service** - HTML email templates with SMTP
* **Redis Cache** - Performance optimization

### 🔒 Security

* **Password Hashing** - bcrypt encryption
* **Rate Limiting** - Protection against brute force
* **Audit Logging** - Complete activity tracking
* **CORS Protection** - Cross-origin request security
* **Input Validation** - Comprehensive data validation

### 📚 Getting Started

1. **Authentication**: Use `/api/auth/login` to get access token
2. **Authorization**: Include `Bearer <token>` in Authorization header
3. **Roles**: Different endpoints require different role permissions
4. **Registration**: Users can register as CUSTOMER or apply as ENGINEER

### 🌟 Default Super Admin

* **Email**: `official.tishnu@gmail.com`
* **Password**: `Access@404` (⚠️ Change after first login)
* **Role**: `SUPER_ADMIN`

---
*Built with ❤️ for secure, scalable authentication*
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Poornasree AI Support",
        "email": "info.pydart@gmail.com",
        "url": "https://github.com/poornasree-ai"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    terms_of_service="https://poornasree.ai/terms",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "🔐 User authentication, registration, and login operations",
        },
        {
            "name": "Admin",
            "description": "👥 Administrative functions for user and system management",
        },
        {
            "name": "Users",
            "description": "👤 User profile management and notifications",
        },
        {
            "name": "AI Services",
            "description": "🤖 AI services including Weaviate vector database and Google AI integration",
        },
        {
            "name": "Database",
            "description": "🗄️ MySQL database health monitoring and statistics",
        },
        {
            "name": "Health",
            "description": "🏥 System health and status monitoring",
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Include routers with enhanced documentation
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/v1", tags=["Admin"]) 
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(ai_router, prefix="/api/v1", tags=["AI Services"])
app.include_router(database_router, prefix="/api/v1", tags=["Database"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Health"])
async def health_check():
    """
    ## 🏥 Health Check Endpoint
    
    Returns the current health status of the API server.
    
    **Returns:**
    - `status`: Current health status
    - `version`: API version
    - `service`: Service name
    - `timestamp`: Current server time
    """
    from datetime import datetime
    return {
        "status": "healthy", 
        "version": settings.app_version,
        "service": "Poornasree AI API",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment
    }


@app.get("/api/v1/config", tags=["Health"])
async def get_config():
    """
    ## ⚙️ Get Public Configuration
    
    Returns public configuration information about the API.
    
    **Returns:**
    - `app_name`: Application name
    - `app_version`: Current version
    - `features`: Available features
    - `super_admin_email`: Default admin email (for reference)
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "super_admin_email": settings.super_admin_email,  # Only email, not password
        "features": {
            "email_verification": True,
            "otp_authentication": True,
            "role_based_access": True,
            "engineer_applications": True,
            "audit_logging": True,
            "rate_limiting": True
        },
        "api_info": {
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Updated module path
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
