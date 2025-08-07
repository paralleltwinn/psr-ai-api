#!/usr/bin/env python3
# =============================================================================
# UPDATE SUPER ADMIN PASSWORD
# =============================================================================

"""
Script to update the super admin password to match the .env configuration.
"""

import sys
from pathlib import Path
from sqlalchemy.orm import sessionmaker

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.database.database import engine
from app.database.models import User
from app.core.constants import UserRole
from app.auth.auth import get_password_hash

def update_admin_password():
    """Update super admin password to match .env configuration."""
    try:
        print("🔐 UPDATING SUPER ADMIN PASSWORD")
        print("="*50)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Find super admin
        admin_user = db.query(User).filter(
            User.email == settings.super_admin_email,
            User.role == UserRole.SUPER_ADMIN
        ).first()
        
        if not admin_user:
            print(f"❌ Super admin not found with email: {settings.super_admin_email}")
            return False
        
        # Hash the new password
        new_hashed_password = get_password_hash(settings.super_admin_password)
        
        # Update password
        admin_user.hashed_password = new_hashed_password
        db.commit()
        
        print(f"✅ Super admin password updated successfully!")
        print(f"📧 Email: {settings.super_admin_email}")
        print(f"🔑 New password: {settings.super_admin_password}")
        print("🚀 You can now login with the updated credentials!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = update_admin_password()
    sys.exit(0 if success else 1)
