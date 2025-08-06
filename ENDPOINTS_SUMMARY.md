# 📊 Poornasree AI API - Endpoint Summary

## 🔢 **Total Endpoints: 14**

---

## 🔐 **Authentication Endpoints (5)**
*Prefix: `/api/v1/auth`*

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/login` | User login with email/password | ❌ |
| `POST` | `/request-otp` | Request OTP for login/registration | ❌ |
| `POST` | `/verify-otp` | Verify OTP and login | ❌ |
| `POST` | `/register/customer` | Register new customer account | ❌ |
| `POST` | `/register/engineer` | Apply as engineer | ❌ |

---

## ⚙️ **Admin Endpoints (6)**
*Prefix: `/api/v1/admin`*

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/dashboard` | Get dashboard statistics | ✅ ADMIN/SUPER_ADMIN |
| `POST` | `/create-admin` | Create new admin user | ✅ SUPER_ADMIN |
| `GET` | `/users` | Get all users (paginated) | ✅ ADMIN/SUPER_ADMIN |
| `GET` | `/engineer-applications` | Get engineer applications | ✅ ADMIN/SUPER_ADMIN |
| `PUT` | `/engineer-applications/{id}/review` | Review engineer application | ✅ ADMIN/SUPER_ADMIN |
| `DELETE` | `/users/{user_id}` | Delete user account | ✅ SUPER_ADMIN |

---

## 👥 **User Endpoints (3)**
*Prefix: `/api/v1/users`*

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/me` | Get current user profile | ✅ Any authenticated user |
| `GET` | `/notifications` | Get user notifications | ✅ Any authenticated user |
| `POST` | `/notifications/{id}/read` | Mark notification as read | ✅ Any authenticated user |

---

## 🏥 **Health & System Endpoints (3)**
*No prefix*

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | API health check | ❌ |
| `GET` | `/api/v1/config` | Get public configuration | ❌ |
| `GET` | `/` | Serve main application page | ❌ (Hidden from docs) |

---

## 📋 **Endpoint Summary by Category**

### 🔒 **Public Endpoints (6)**
- Health check
- Configuration
- All authentication endpoints
- Main page

### 🔐 **Protected Endpoints (8)**
- All admin endpoints (6)
- All user endpoints (3)

### 👑 **Super Admin Only (2)**
- Create admin
- Delete user

### 👨‍💼 **Admin/Super Admin (4)**
- Dashboard
- User management
- Engineer applications
- Application reviews

### 👤 **Any Authenticated User (3)**
- Profile access
- Notifications
- Mark notifications read

---

## 🌐 **API Documentation URLs**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔗 **Full Endpoint List with URLs**

### Authentication
```
POST /api/v1/auth/login
POST /api/v1/auth/request-otp
POST /api/v1/auth/verify-otp
POST /api/v1/auth/register/customer
POST /api/v1/auth/register/engineer
```

### Admin
```
GET  /api/v1/admin/dashboard
POST /api/v1/admin/create-admin
GET  /api/v1/admin/users
GET  /api/v1/admin/engineer-applications
PUT  /api/v1/admin/engineer-applications/{application_id}/review
DELETE /api/v1/admin/users/{user_id}
```

### Users
```
GET  /api/v1/users/me
GET  /api/v1/users/notifications
POST /api/v1/users/notifications/{notification_id}/read
```

### Health
```
GET /health
GET /api/v1/config
GET / (main page)
```

---

*🎯 Your API provides comprehensive authentication, user management, and admin functionality with proper role-based access control!*
