#!/usr/bin/env python3
# =============================================================================
# POORNASREE AI - SYSTEM STATUS CHECK
# =============================================================================

"""
System status check script to verify all components are working correctly.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import requests
from datetime import datetime

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.database.database import engine
from app.database.models import User
from app.core.constants import UserRole

def check_database_connection():
    """Check database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"✅ Database connected: {db_name}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_tables():
    """Check if all required tables exist."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = ['users', 'otp_verifications', 'notifications', 
                          'engineer_applications', 'audit_logs', 'login_attempts']
        
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            print(f"✅ All required tables exist: {tables}")
            return True
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False

def check_super_admin():
    """Check if super admin exists."""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
        
        if admin:
            print(f"✅ Super admin exists: {admin.email}")
            return True
        else:
            print("❌ No super admin found")
            return False
    except Exception as e:
        print(f"❌ Super admin check failed: {e}")
        return False
    finally:
        db.close()

def check_api_server():
    """Check if API server is running."""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running and responding")
            return True
        else:
            print(f"❌ API server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        return False
    except Exception as e:
        print(f"❌ API server check failed: {e}")
        return False

def system_status_check():
    """Run complete system status check."""
    print("🔍 POORNASREE AI SYSTEM STATUS CHECK")
    print("="*50)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Database URL: {settings.database_url}")
    print("="*50)
    
    checks = [
        ("Database Connection", check_database_connection),
        ("Tables", check_tables),
        ("Super Admin", check_super_admin),
        ("API Server", check_api_server)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n🔄 Checking {check_name}...")
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Your Poornasree AI application is ready!")
        print("\n📝 Next steps:")
        print("   • Access API docs: http://127.0.0.1:8000/docs")
        print("   • Login with: admin@poornasree.ai / Admin@2024")
        print("   • Change default password after first login")
    else:
        print("⚠️  SOME SYSTEMS NEED ATTENTION")
        print("❗ Please fix the failed checks above")
    
    print("="*50)
    return all_passed

if __name__ == "__main__":
    success = system_status_check()
    sys.exit(0 if success else 1)
