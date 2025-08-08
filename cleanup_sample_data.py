#!/usr/bin/env python3
# =============================================================================
# POORNASREE AI - CLEANUP SAMPLE DATA
# =============================================================================

"""
Script to remove sample/test data from Poornasree AI Authentication System database.
This script will:
1. Remove all test users (customer1@test.com, engineer1@test.com, etc.)
2. Remove sample admin (admin@poornasree.ai)
3. Remove associated applications and data
4. Keep only the super admin user and production data

WARNING: This will permanently delete test data. Use only in production environments.
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

def cleanup_sample_data():
    """Remove all sample/test data from the database."""
    try:
        print("="*60)
        print("CLEANING UP SAMPLE DATA")
        print("="*60)
        print("⚠️  WARNING: This will permanently delete test data!")
        print()
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Count existing data before cleanup
        total_users = db.query(User).count()
        total_applications = db.query(EngineerApplication).count()
        total_notifications = db.query(Notification).count()
        total_audit_logs = db.query(AuditLog).count()
        
        print(f"📊 BEFORE CLEANUP:")
        print(f"   • Total Users: {total_users}")
        print(f"   • Total Applications: {total_applications}")
        print(f"   • Total Notifications: {total_notifications}")
        print(f"   • Total Audit Logs: {total_audit_logs}")
        print()
        
        # 1. Remove test customers (customer1@test.com, customer2@test.com, etc.)
        print("🔨 Removing test customers...")
        test_customers = db.query(User).filter(
            User.email.like('%@test.com'),
            User.role == UserRole.CUSTOMER
        ).all()
        
        customer_ids = [user.id for user in test_customers]
        if customer_ids:
            # Remove related applications first
            db.query(EngineerApplication).filter(
                EngineerApplication.user_id.in_(customer_ids)
            ).delete(synchronize_session=False)
            
            # Remove related notifications
            db.query(Notification).filter(
                Notification.user_id.in_(customer_ids)
            ).delete(synchronize_session=False)
            
            # Remove related audit logs
            db.query(AuditLog).filter(
                AuditLog.user_id.in_(customer_ids)
            ).delete(synchronize_session=False)
            
            # Remove users
            for customer in test_customers:
                db.delete(customer)
            
            print(f"✅ Removed {len(test_customers)} test customers")
        
        # 2. Remove test engineers (engineer1@test.com, engineer2@test.com, etc.)
        print("🔨 Removing test engineers...")
        test_engineers = db.query(User).filter(
            User.email.like('%@test.com'),
            User.role == UserRole.ENGINEER
        ).all()
        
        engineer_ids = [user.id for user in test_engineers]
        if engineer_ids:
            # Remove related applications
            db.query(EngineerApplication).filter(
                EngineerApplication.user_id.in_(engineer_ids)
            ).delete(synchronize_session=False)
            
            # Remove related notifications
            db.query(Notification).filter(
                Notification.user_id.in_(engineer_ids)
            ).delete(synchronize_session=False)
            
            # Remove related audit logs
            db.query(AuditLog).filter(
                AuditLog.user_id.in_(engineer_ids)
            ).delete(synchronize_session=False)
            
            # Remove users
            for engineer in test_engineers:
                db.delete(engineer)
            
            print(f"✅ Removed {len(test_engineers)} test engineers")
        
        # 3. Remove sample admin (admin@poornasree.ai)
        print("🔨 Removing sample admin...")
        sample_admin = db.query(User).filter(
            User.email == "admin@poornasree.ai"
        ).first()
        
        if sample_admin:
            # Remove related notifications
            db.query(Notification).filter(
                Notification.user_id == sample_admin.id
            ).delete(synchronize_session=False)
            
            # Remove related audit logs
            db.query(AuditLog).filter(
                AuditLog.user_id == sample_admin.id
            ).delete(synchronize_session=False)
            
            # Update applications that were reviewed by this admin
            db.query(EngineerApplication).filter(
                EngineerApplication.reviewer_id == sample_admin.id
            ).update({"reviewer_id": None}, synchronize_session=False)
            
            db.delete(sample_admin)
            print("✅ Removed sample admin user")
        
        # 4. Remove any orphaned applications, notifications, and audit logs
        print("🔨 Cleaning up orphaned data...")
        
        # Get all valid user IDs
        valid_user_ids = [user.id for user in db.query(User.id).all()]
        
        # Remove orphaned applications
        orphaned_apps = db.query(EngineerApplication).filter(
            ~EngineerApplication.user_id.in_(valid_user_ids)
        ).delete(synchronize_session=False)
        
        # Remove orphaned notifications
        orphaned_notifications = db.query(Notification).filter(
            ~Notification.user_id.in_(valid_user_ids)
        ).delete(synchronize_session=False)
        
        # Remove orphaned audit logs
        orphaned_logs = db.query(AuditLog).filter(
            ~AuditLog.user_id.in_(valid_user_ids)
        ).delete(synchronize_session=False)
        
        if orphaned_apps or orphaned_notifications or orphaned_logs:
            print(f"✅ Cleaned up orphaned data: {orphaned_apps} apps, {orphaned_notifications} notifications, {orphaned_logs} logs")
        
        # Commit all changes
        db.commit()
        
        # Count remaining data after cleanup
        remaining_users = db.query(User).count()
        remaining_applications = db.query(EngineerApplication).count()
        remaining_notifications = db.query(Notification).count()
        remaining_audit_logs = db.query(AuditLog).count()
        
        print()
        print(f"📊 AFTER CLEANUP:")
        print(f"   • Remaining Users: {remaining_users}")
        print(f"   • Remaining Applications: {remaining_applications}")
        print(f"   • Remaining Notifications: {remaining_notifications}")
        print(f"   • Remaining Audit Logs: {remaining_audit_logs}")
        print()
        
        # Show remaining users
        remaining_user_list = db.query(User).all()
        print("👥 REMAINING USERS:")
        for user in remaining_user_list:
            print(f"   • {user.email} ({user.role.value}) - {user.status.value}")
        
        db.close()
        
        print("\n" + "="*60)
        print("🎉 SAMPLE DATA CLEANUP COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ All test data removed")
        print("✅ Database ready for production")
        print(f"✅ {remaining_users} production users remain")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

if __name__ == "__main__":
    print("🚨 SAMPLE DATA CLEANUP UTILITY")
    print("This will remove ALL test data from the database.")
    print("Only the super admin and genuine production data will remain.")
    print()
    
    response = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        success = cleanup_sample_data()
        sys.exit(0 if success else 1)
    else:
        print("❌ Cleanup cancelled by user.")
        sys.exit(0)
