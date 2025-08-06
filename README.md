"""
FastAPI Authentication System

A comprehensive authentication system with role-based access control supporting:
- Super Admin (hardcoded credentials)
- Admin (OTP-based login)
- Engineer (password-based, requires approval)
- Customer (OTP-based registration)

Setup Instructions:

1. Install dependencies:
   pip install -r requirements.txt

2. Set up MySQL database and update DATABASE_URL in .env

3. Configure email settings in .env for OTP delivery

4. Run the application:
   uvicorn main:app --reload

5. Access the web interface at http://localhost:8000

Default Super Admin Credentials:
- Email: superadmin@company.com
- Password: SuperSecurePassword123!

Features:
- JWT-based authentication
- OTP verification for admins and customers
- Email notifications for engineer registration
- Dashboard for different user roles
- Engineer application approval workflow
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
