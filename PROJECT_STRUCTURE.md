# =============================================================================
# POORNASREE AI - PROJECT STRUCTURE
# =============================================================================

"""
Poornasree AI Authentication System

A comprehensive, well-organized FastAPI authentication system with role-based access control.

Project Structure:
├── app/
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database connection setup
│   ├── models.py                   # SQLAlchemy models
│   ├── schemas.py                  # Pydantic schemas
│   ├── auth.py                     # Authentication utilities
│   ├── email_service.py            # Email service with HTML templates
│   ├── services.py                 # Business logic services
│   ├── dependencies.py             # FastAPI dependencies
│   ├── utils.py                    # Utility functions
│   ├── exceptions.py               # Custom exceptions and handlers
│   ├── core/
│   │   ├── __init__.py            # Core module initialization
│   │   ├── constants.py           # Application constants and enums
│   │   └── logging.py             # Logging configuration
│   ├── routers/
│   │   ├── __init__.py            # Router module initialization
│   │   ├── auth.py                # Authentication routes
│   │   ├── admin.py               # Admin routes
│   │   └── users.py               # User routes
│   └── templates/
│       └── index.html             # Frontend interface
├── alembic/                       # Database migrations
├── logs/                          # Application logs
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── alembic.ini                   # Alembic configuration
├── setup.sh                     # Setup script
└── README.md                     # Project documentation

Features:
- ✅ Role-based authentication (Super Admin, Admin, Engineer, Customer)
- ✅ JWT token-based security
- ✅ OTP verification system
- ✅ Email notifications with HTML templates
- ✅ Engineer approval workflow
- ✅ Comprehensive logging
- ✅ Error handling and validation
- ✅ Database migrations with Alembic
- ✅ Professional code organization
- ✅ Type hints and documentation
- ✅ Security best practices

Technology Stack:
- FastAPI (Web framework)
- SQLAlchemy (ORM)
- Alembic (Database migrations)
- MySQL (Database)
- Redis (Caching)
- JWT (Authentication)
- Pydantic (Data validation)
- Jinja2 (Templating)
- PyOTP (OTP generation)
- SMTP (Email delivery)

Getting Started:
1. Copy .env.example to .env and configure settings
2. Install dependencies: pip install -r requirements.txt
3. Run migrations: alembic upgrade head
4. Start application: python main.py
5. Access at: http://localhost:8000

Default Super Admin:
- Email: admin@poornasree.ai
- Password: PoornasreeAI@2025!
"""

__version__ = "1.0.0"
__author__ = "Poornasree AI Team"
