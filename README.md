# 🚀 Poornasree AI Authentication System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **comprehensive, production-ready FastAPI authentication system** with role-based access control, OTP verification, email integration, and admin dashboard functionality. Built for **Poornasree AI** with enterprise-grade security and scalability.

## 🎯 Features

### ✨ **Core Authentication**
- 🔐 **JWT Token-based Authentication** - Secure, stateless authentication
- 👥 **Role-Based Access Control** - 4 user roles with granular permissions
- 📱 **OTP Verification System** - Email-based two-factor authentication
- 🔑 **Password Security** - BCrypt hashing with strong validation
- 🚫 **Rate Limiting** - Protection against brute force attacks

### 🎭 **User Roles & Permissions**

| Role | Description | Authentication | Permissions |
|------|-------------|----------------|-------------|
| **SUPER_ADMIN** | System Administrator | Password | Full system control, user management |
| **ADMIN** | Organization Admin | OTP-based | User management, reports, approval workflows |
| **ENGINEER** | Approved Engineer | Password | Project access after admin approval |
| **CUSTOMER** | Regular User | OTP-based | Profile management, basic access |

### 🛠️ **Advanced Features**
- 📧 **Professional Email System** - HTML templates for notifications
- 🔄 **Engineer Approval Workflow** - Admin review process for engineers
- 📊 **Admin Dashboard** - Comprehensive system statistics
- 📝 **Audit Logging** - Complete activity tracking
- 🗄️ **Database Migrations** - Alembic-powered schema versioning
- 🧪 **Comprehensive Testing** - Unit and integration tests

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Database      │
│   (Next.js)     │◄──►│   Backend       │◄──►│   (MySQL)       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   Email Service │
                       │   (SMTP/Gmail)  │
                       └─────────────────┘
```

## 📁 Project Structure

```
psr-ai-api/
├── 📂 app/                          # Main application package
│   ├── 🔌 api/                      # API layer
│   │   └── schemas.py              # Pydantic request/response models
│   ├── 🔐 auth/                     # Authentication logic
│   │   ├── auth.py                 # Password hashing, JWT tokens, OTP
│   │   └── dependencies.py         # Auth dependencies & middleware
│   ├── ⚙️ core/                     # Core utilities
│   │   ├── constants.py            # Enums (UserRole, UserStatus, etc.)
│   │   └── logging.py              # Logging configuration
│   ├── 🗄️ database/                 # Database layer
│   │   ├── database.py             # SQLAlchemy setup & session management
│   │   └── models.py               # Database models (User, OTP, etc.)
│   ├── 🛣️ routers/                  # API endpoints
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── admin.py                # Admin management endpoints
│   │   └── users.py                # User profile endpoints
│   ├── 🔧 services/                 # Business logic
│   │   ├── email_service.py        # Email/SMTP service
│   │   └── user_service.py         # User business logic
│   ├── 🎨 templates/                # HTML templates
│   └── ⚙️ config.py                 # Configuration management
├── 📦 alembic/                      # Database migrations
├── 📋 logs/                         # Application logs
├── 🚀 main.py                       # FastAPI application entry point
├── 🔧 init.py                       # Database setup script
├── 🧪 system_check.py               # System status verification
└── 📦 requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### 1️⃣ **Prerequisites**
```bash
# Python 3.8+
python --version

# MySQL 8.0+
mysql --version

# Git
git --version
```

### 2️⃣ **Installation**
```bash
# Clone the repository
git clone https://github.com/your-org/psr-ai-api.git
cd psr-ai-api

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ **Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section below)
nano .env
```

### 4️⃣ **Database Setup**
```bash
# Run complete database setup (creates DB, tables, super admin)
python init.py

# Or manually run migrations
alembic upgrade head
```

### 5️⃣ **Launch Application**
```bash
# Development server
python main.py

# Production server  
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6️⃣ **Access Application**
- 🌐 **API**: http://localhost:8000
- 📚 **Swagger Docs**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

## ⚙️ Configuration

### 🔧 **Environment Variables** (`.env`)

```bash
# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/poornasree_ai

# =============================================================================
# SECURITY & JWT CONFIGURATION  
# =============================================================================
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# =============================================================================
# SUPER ADMIN CONFIGURATION
# =============================================================================
SUPER_ADMIN_EMAIL=official.tishnu@gmail.com
SUPER_ADMIN_PASSWORD=Access@404

# =============================================================================
# EMAIL & SMTP CONFIGURATION
# =============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=Poornasree AI System

# =============================================================================
# OTP CONFIGURATION
# =============================================================================
OTP_SECRET_KEY=poornasree-ai-otp-secret-key-2025
OTP_EXPIRY_MINUTES=5
```

## 📡 API Documentation

### 🔢 **Total Endpoints: 14**

### 🔐 **Authentication Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/login` | User login with email/password | ❌ |
| `POST` | `/api/v1/auth/request-otp` | Request OTP for verification | ❌ |
| `POST` | `/api/v1/auth/verify-otp` | Verify OTP and complete auth | ❌ |
| `POST` | `/api/v1/auth/register/customer` | Register new customer | ❌ |
| `POST` | `/api/v1/auth/register/engineer` | Apply as engineer | ❌ |

### ⚙️ **Admin Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/admin/dashboard` | Dashboard statistics | ✅ ADMIN+ |
| `POST` | `/api/v1/admin/create-admin` | Create new admin | ✅ SUPER_ADMIN |
| `GET` | `/api/v1/admin/users` | Get all users (paginated) | ✅ ADMIN+ |
| `GET` | `/api/v1/admin/engineer-applications` | Get applications | ✅ ADMIN+ |
| `PUT` | `/api/v1/admin/engineer-applications/{id}/review` | Review application | ✅ ADMIN+ |
| `DELETE` | `/api/v1/admin/users/{user_id}` | Delete user | ✅ SUPER_ADMIN |

### 👥 **User Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/users/me` | Get current user profile | ✅ Any User |
| `GET` | `/api/v1/users/notifications` | Get notifications | ✅ Any User |
| `POST` | `/api/v1/users/notifications/{id}/read` | Mark as read | ✅ Any User |

### 🏥 **System Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | API health check | ❌ |
| `GET` | `/api/v1/config` | Public configuration | ❌ |

## 🔐 Authentication Examples

### 🚀 **Super Admin Login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "official.tishnu@gmail.com",
       "password": "Access@404"
     }'
```

**Response:**
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

### 📱 **Customer Registration with OTP**
```bash
# Step 1: Register customer
curl -X POST "http://localhost:8000/api/v1/auth/register/customer" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "customer@example.com",
       "first_name": "John",
       "last_name": "Doe",
       "phone_number": "+1234567890",
       "machine_model": "Model X1",
       "state": "California"
     }'

# Step 2: Verify with OTP (sent to email)
curl -X POST "http://localhost:8000/api/v1/auth/verify-otp" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "customer@example.com",
       "otp_code": "123456"
     }'
```

### 🔧 **Using Authenticated Requests**
```bash
# Include JWT token in Authorization header
curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## 🛠️ Development

### 📊 **Database Management**
```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Reset database
python init.py
```

### 🧪 **Testing**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

### 📋 **Logging & Monitoring**
```bash
# View logs
tail -f logs/app.log

# System health check
python system_check.py

# Check API health
curl http://localhost:8000/health
```

## 🔒 Security Features

### 🛡️ **Authentication Security**
- **JWT Tokens**: Secure, stateless authentication with configurable expiration
- **Password Hashing**: BCrypt with salt for secure password storage
- **OTP Verification**: Time-based one-time passwords for email verification
- **Rate Limiting**: Protection against brute force attacks
- **CORS Configuration**: Controlled cross-origin resource sharing

### 🔐 **Data Protection**
- **Input Validation**: Pydantic schemas for request/response validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Proper HTML escaping in templates
- **Environment Secrets**: Sensitive data stored in environment variables

### 📊 **Audit & Monitoring**
- **Audit Logs**: Complete tracking of user actions and system events
- **Login Attempts**: Failed login tracking and alerting
- **Error Handling**: Comprehensive error logging and user-friendly responses
- **Health Monitoring**: System status endpoints for monitoring tools

## 🎯 Default Credentials

### 👑 **Super Admin Access**
```
Email: official.tishnu@gmail.com
Password: Access@404
```

⚠️ **Important**: Change the default super admin password after first login in production!

## 🚀 Deployment

### 🐳 **Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### ☁️ **Production Deployment**
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use Docker
docker build -t psr-ai-api .
docker run -p 8000:8000 psr-ai-api
```

## 🔧 Troubleshooting

### ❓ **Common Issues**

**Database Connection Failed**
```bash
# Check MySQL service
sudo systemctl status mysql

# Verify credentials in .env
# Ensure database exists: CREATE DATABASE poornasree_ai;
```

**OTP Email Not Sending**
```bash
# Verify SMTP settings in .env
# Check email service logs
# Ensure app password for Gmail (not regular password)
```

**Permission Denied Errors**
```bash
# Check user roles in database
# Verify JWT token is valid
# Ensure proper Authorization header format
```

## 📞 Support

### 🆘 **Getting Help**
- 📧 **Email**: support@poornasree.ai
- 📚 **Documentation**: See `/docs` endpoint
- 🐛 **Issues**: Create GitHub issue
- 💬 **Community**: Join our Discord

### 🔗 **Useful Links**
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Guide](https://docs.sqlalchemy.org)
- [Alembic Tutorial](https://alembic.sqlalchemy.org)
- [JWT.io](https://jwt.io) - JWT token debugger

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

- **Poornasree AI Team** - *Initial development*

---

<div align="center">

**Built with ❤️ by the Poornasree AI Team**

[![FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Powered%20by-Python-blue.svg)](https://python.org)

</div>
