#!/usr/bin/env python3
"""
Test script to send engineer application notification email
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.services.email_service import send_engineer_application_notification
from app.database.database import get_db
from app.database.models import User, EngineerApplication
from sqlalchemy.orm import Session
import asyncio


async def test_email_notification():
    """Test sending engineer application notification email"""
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Get a pending engineer application
        pending_application = db.query(EngineerApplication).filter(
            EngineerApplication.status == 'pending'
        ).first()
        
        if not pending_application:
            print("No pending engineer applications found")
            return
            
        # Get admin users to notify
        admin_users = db.query(User).filter(
            User.role.in_(['ADMIN', 'SUPER_ADMIN']),
            User.is_active == True
        ).all()
        
        if not admin_users:
            print("No admin users found")
            return
            
        print(f"Testing email notification for application ID: {pending_application.id}")
        print(f"Engineer: {pending_application.user.first_name} {pending_application.user.last_name}")
        print(f"Notifying {len(admin_users)} admin(s)")
        
        # Send email notification to all admins
        admin_emails = [admin.email for admin in admin_users]
        print(f"Sending test emails to: {', '.join(admin_emails)}")
        
        success = await send_engineer_application_notification(
            engineer=pending_application.user,
            admin_emails=admin_emails,
            application_id=pending_application.id
        )
        
        if success:
            print("✅ Test emails sent successfully!")
        else:
            print("❌ Failed to send test emails")
        
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_email_notification())
