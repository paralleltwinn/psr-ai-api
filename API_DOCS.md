# 📚 Poornasree AI API Documentation

## 🚀 Quick Start

### Base URL
```
http://localhost:8000
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Authentication

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@poornasree.ai",
  "password": "Admin@2024"
}
```

**Response:**
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

### Using Authentication
Include the token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 👥 User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `SUPER_ADMIN` | System administrator | Full system access |
| `ADMIN` | Organization admin | User management, reports |
| `ENGINEER` | Approved engineer | Project access, applications |
| `CUSTOMER` | Regular user | Basic profile access |

## 🔗 API Endpoints

### Authentication Endpoints

#### 🔑 Login
```http
POST /api/v1/auth/login
```
- **Purpose**: Authenticate user and get access token
- **Auth Required**: No
- **Body**: `{ "email": "string", "password": "string" }`

#### 📝 Register Customer
```http
POST /api/v1/auth/register/customer
```
- **Purpose**: Register new customer account
- **Auth Required**: No
- **Body**: `{ "email": "string", "password": "string", "first_name": "string", "last_name": "string" }`

#### 🛠️ Apply as Engineer
```http
POST /api/v1/auth/register/engineer
```
- **Purpose**: Submit engineer application
- **Auth Required**: No
- **Body**: `{ "email": "string", "password": "string", "first_name": "string", "last_name": "string", "experience_years": 5, "skills": "string" }`

#### 📧 Verify Email
```http
POST /api/v1/auth/verify-email
```
- **Purpose**: Verify email with OTP code
- **Auth Required**: No
- **Body**: `{ "email": "string", "otp_code": "string" }`

#### 🔄 Resend OTP
```http
POST /api/v1/auth/resend-otp
```
- **Purpose**: Resend OTP verification code
- **Auth Required**: No
- **Body**: `{ "email": "string" }`

### Admin Endpoints

#### 👥 Get All Users
```http
GET /api/v1/admin/users
```
- **Purpose**: Get paginated list of all users
- **Auth Required**: Yes (ADMIN or SUPER_ADMIN)
- **Query Params**: `?page=1&limit=10&role=CUSTOMER&status=ACTIVE`

#### 🔧 Update User Status
```http
PUT /api/v1/admin/users/{user_id}/status
```
- **Purpose**: Update user status (activate/deactivate/suspend)
- **Auth Required**: Yes (ADMIN or SUPER_ADMIN)
- **Body**: `{ "status": "ACTIVE" }`

#### 🛠️ Get Engineer Applications
```http
GET /api/v1/admin/engineer-applications
```
- **Purpose**: Get all engineer applications
- **Auth Required**: Yes (ADMIN or SUPER_ADMIN)
- **Query Params**: `?page=1&limit=10&status=PENDING`

#### ✅ Review Engineer Application
```http
PUT /api/v1/admin/engineer-applications/{application_id}/review
```
- **Purpose**: Approve or reject engineer application
- **Auth Required**: Yes (ADMIN or SUPER_ADMIN)
- **Body**: `{ "status": "APPROVED", "review_notes": "string" }`

#### 📊 Get Dashboard Stats
```http
GET /api/v1/admin/dashboard/stats
```
- **Purpose**: Get system statistics for dashboard
- **Auth Required**: Yes (ADMIN or SUPER_ADMIN)

### User Endpoints

#### 👤 Get Profile
```http
GET /api/v1/users/profile
```
- **Purpose**: Get current user's profile
- **Auth Required**: Yes (Any authenticated user)

#### ✏️ Update Profile
```http
PUT /api/v1/users/profile
```
- **Purpose**: Update current user's profile
- **Auth Required**: Yes (Any authenticated user)
- **Body**: `{ "first_name": "string", "last_name": "string", "phone_number": "string" }`

#### 🔒 Change Password
```http
PUT /api/v1/users/change-password
```
- **Purpose**: Change user password
- **Auth Required**: Yes (Any authenticated user)
- **Body**: `{ "current_password": "string", "new_password": "string" }`

### Health Endpoints

#### 🏥 Health Check
```http
GET /health
```
- **Purpose**: Check API health status
- **Auth Required**: No

#### ⚙️ Get Configuration
```http
GET /api/v1/config
```
- **Purpose**: Get public API configuration
- **Auth Required**: No

## 🔒 Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Rate Limiting
- Login attempts: 5 per minute per IP
- Registration: 3 per minute per IP
- OTP requests: 3 per minute per email

### Security Headers
- CORS protection
- Content Security Policy
- Rate limiting
- Request validation

## 📨 Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": "Detailed error information",
  "code": "ERROR_CODE"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🧪 Testing with curl

### Login Example
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@poornasree.ai",
    "password": "Admin@2024"
  }'
```

### Authenticated Request Example
```bash
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛠️ Development

### Start Server
```bash
python main.py
```

### Database Setup
```bash
python init.py
```

### System Check
```bash
python system_check.py
```

## 📞 Support

- **Email**: info.pydart@gmail.com
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

*For more detailed information, visit the interactive Swagger documentation at `/docs`*
