#!/usr/bin/env python3
# =============================================================================
# POORNASREE AI - DATABASE CLEANUP SCRIPT
# =============================================================================

"""
Database cleanup script for removing sample/test data from production.
This script will:
1. Remove all sample users (customer1@test.com, engineer1@test.com, etc.)
2. Remove sample admin accounts (admin@poornasree.ai)
3. Remove associated engineer applications and notifications
4. Keep only the super admin user and real production data

WARNING: This will permanently delete test data. Use with caution!
"""

import sys
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.database.database import engine
from app.database.models import User, EngineerApplication, Notification, AuditLog
from app.core.constants import UserRole, UserStatus

def clean_sample_data():
    """Remove all sample/test data from the database."""
    try:
        print("="*60)
        print("🧹 CLEANING SAMPLE DATA FROM DATABASE")
        print("="*60)
        print("⚠️  WARNING: This will permanently delete test data!")
        
        # Ask for confirmation
        confirm = input("Are you sure you want to proceed? Type 'YES' to continue: ")
        if confirm != 'YES':
            print("❌ Operation cancelled.")
            return False
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        deleted_counts = {
            'users': 0,
            'applications': 0,
            'notifications': 0,
            'audit_logs': 0
        }
        
        print("\n🔍 Identifying sample data...")
        
        # Define patterns for sample data
        sample_email_patterns = [
            'customer%@test.com',
            'engineer%@test.com', 
            'pending.engineer%@test.com',
            'rejected.engineer%@test.com',
            'admin@poornasree.ai'
        ]
        
        # Get all sample users
        sample_users = []
        for pattern in sample_email_patterns:
            users = db.query(User).filter(User.email.like(pattern)).all()
            sample_users.extend(users)
        
        print(f"📊 Found {len(sample_users)} sample users to remove")
        
        if len(sample_users) == 0:
            print("✅ No sample data found. Database is clean.")
            db.close()
            return True
        
        # Show what will be deleted
        print("\n📋 Sample users to be removed:")
        for user in sample_users:
            print(f"  • {user.email} ({user.role.value}) - {user.status.value}")
        
        # Get user IDs for cleanup
        user_ids = [user.id for user in sample_users]
        
        print("\n🗑️  Removing related data...")
        
        # Remove engineer applications for sample users
        applications = db.query(EngineerApplication).filter(
            EngineerApplication.user_id.in_(user_ids)
        ).all()
        deleted_counts['applications'] = len(applications)
        for app in applications:
            db.delete(app)
        
        # Remove notifications for sample users
        notifications = db.query(Notification).filter(
            (Notification.sender_id.in_(user_ids)) | 
            (Notification.recipient_id.in_(user_ids))
        ).all()
        deleted_counts['notifications'] = len(notifications)
        for notification in notifications:
            db.delete(notification)
        
        # Remove audit logs for sample users
        audit_logs = db.query(AuditLog).filter(
            AuditLog.user_id.in_(user_ids)
        ).all()
        deleted_counts['audit_logs'] = len(audit_logs)
        for log in audit_logs:
            db.delete(log)
        
        # Remove sample users
        deleted_counts['users'] = len(sample_users)
        for user in sample_users:
            db.delete(user)
        
        # Commit all changes
        db.commit()
        
        print("\n✅ CLEANUP COMPLETED SUCCESSFULLY!")
        print("="*40)
        print(f"🗑️  Deleted {deleted_counts['users']} sample users")
        print(f"🗑️  Deleted {deleted_counts['applications']} engineer applications")
        print(f"🗑️  Deleted {deleted_counts['notifications']} notifications")
        print(f"🗑️  Deleted {deleted_counts['audit_logs']} audit log entries")
        print("="*40)
        
        # Verify super admin still exists
        super_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
        if super_admin:
            print(f"✅ Super admin preserved: {super_admin.email}")
        else:
            print("⚠️  WARNING: No super admin found! You may need to recreate it.")
        
        # Show remaining user count
        remaining_users = db.query(User).count()
        print(f"📊 Remaining users in database: {remaining_users}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def show_current_data():
    """Show current users in the database."""
    try:
        print("="*60)
        print("📊 CURRENT DATABASE USERS")
        print("="*60)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        users = db.query(User).order_by(User.role, User.email).all()
        
        if not users:
            print("🚫 No users found in database")
            db.close()
            return
        
        print(f"Total users: {len(users)}\n")
        
        # Group by role
        by_role = {}
        for user in users:
            role = user.role.value
            if role not in by_role:
                by_role[role] = []
            by_role[role].append(user)
        
        for role, role_users in by_role.items():
            print(f"📋 {role.upper()} ({len(role_users)} users):")
            for user in role_users:
                status_emoji = "✅" if user.is_active else "❌"
                print(f"  {status_emoji} {user.email} - {user.first_name} {user.last_name} ({user.status.value})")
            print()
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error showing data: {e}")
        if 'db' in locals():
            db.close()

def main():
    """Main function to handle user choice."""
    print("🧹 POORNASREE AI - DATABASE CLEANUP UTILITY")
    print("="*50)
    print("Choose an option:")
    print("1. Show current database users")
    print("2. Clean sample/test data")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            show_current_data()
            break
        elif choice == '2':
            success = clean_sample_data()
            if success:
                print("\n🎉 Database cleanup completed!")
            else:
                print("\n❌ Database cleanup failed!")
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
