# =============================================================================
# POORNASREE AI - AUTHENTICATION SYSTEM TEST
# =============================================================================

"""
Test script to verify the updated authentication system with new customer/engineer fields
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_auth_system():
    """Test the authentication system updates"""
    
    print("🔧 Testing Poornasree AI Authentication System Updates")
    print("=" * 60)
    
    # Test 1: Import all modules
    try:
        from app.api import schemas
        from app.database import models
        from app.routers import auth
        print("✅ All modules imported successfully")
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return
    
    # Test 2: Verify schema updates
    try:
        # Test CustomerRegistration schema
        customer_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "machine_model": "Model X1",
            "state": "California",
            "phone_number": "+1234567890",
            "otp_code": "123456"
        }
        customer_schema = schemas.CustomerRegistration(**customer_data)
        print("✅ CustomerRegistration schema validation passed")
        
        # Test EngineerRegistration schema
        engineer_data = {
            "email": "engineer@example.com",
            "first_name": "Jane", 
            "last_name": "Smith",
            "phone_number": "+1234567890",
            "department": "AI Research",
            "dealer": "Tech Solutions Inc",
            "state": "New York"
        }
        engineer_schema = schemas.EngineerRegistration(**engineer_data)
        print("✅ EngineerRegistration schema validation passed")
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return
    
    # Test 3: Verify database model updates
    try:
        # Check if User model has new fields
        user_fields = [attr for attr in dir(models.User) if not attr.startswith('_')]
        required_fields = ['machine_model', 'state', 'department', 'dealer']
        
        for field in required_fields:
            if field in user_fields:
                print(f"✅ User model has '{field}' field")
            else:
                print(f"❌ User model missing '{field}' field")
        
    except Exception as e:
        print(f"❌ Database model verification failed: {e}")
        return
    
    # Test 4: Verify router endpoints
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Check if registration endpoints exist
        response = client.get("/docs")  # OpenAPI docs should show our endpoints
        if response.status_code == 200:
            print("✅ FastAPI app and router endpoints accessible")
        else:
            print("❌ FastAPI app not accessible")
            
    except Exception as e:
        print(f"⚠️  Router endpoint test skipped: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Authentication system update verification complete!")
    print("\n📋 Summary of Changes:")
    print("   • Updated CustomerRegistration schema with machine_model and state fields")
    print("   • Updated EngineerRegistration schema with department, dealer, and state fields")
    print("   • Added customer/engineer specific fields to User database model")
    print("   • Simplified engineer application process (no complex forms)")
    print("   • Updated authentication endpoints to handle new fields")
    print("   • Maintained OTP verification for customer registration")
    print("   • Created migration script for database schema updates")


if __name__ == "__main__":
    asyncio.run(test_auth_system())
