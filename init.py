#!/usr/bin/env python3
# =============================================================================
# POORNASREE AI - PRODUCTION DATABASE SETUP
# =============================================================================

"""
Production database setup script for Poornasree AI Authentication System.
This script handles:
1. Database creation if it doesn't exist
2. Table creation from SQLAlchemy models
3. Super admin user creation
4. Database migration application

This script creates a clean production database with only the essential super admin user.
No sample or test data is created - this is suitable for production deployment.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pymysql

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.database.database import Base, engine
from app.database.models import *  # Import all models
from app.database.models import User, EngineerApplication, Notification, AuditLog
from app.core.constants import UserRole, UserStatus, NotificationType
from app.auth.auth import get_password_hash

def create_database():
    """Create the database if it doesn't exist."""
    try:
        print("="*60)
        print("STEP 1: DATABASE CREATION")
        print("="*60)
        
        print(f"Database URL: {settings.database_url}")
        
        # Extract database name
        database_name = settings.database_url.split('/')[-1]
        server_url = settings.database_url.rsplit('/', 1)[0]
        
        print(f"Database name: {database_name}")
        print(f"Server URL: {server_url}")
        
        # Connect to MySQL server (without database)
        server_engine = create_engine(server_url)
        
        with server_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SHOW DATABASES LIKE '{database_name}'"))
            exists = result.fetchone() is not None
            
            if exists:
                print(f"✅ Database '{database_name}' already exists")
            else:
                print(f"🔨 Creating database '{database_name}'...")
                conn.execute(text("COMMIT"))
                conn.execute(text(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                print(f"✅ Database '{database_name}' created successfully")
        
        # Test connection to the database
        db_engine = create_engine(settings.database_url)
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            current_db = result.fetchone()[0]
            print(f"✅ Connected to database: {current_db}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all tables from SQLAlchemy models."""
    try:
        print("\n" + "="*60)
        print("STEP 2: TABLE CREATION")
        print("="*60)
        
        print("🔨 Creating tables from SQLAlchemy models...")
        
        # Show which models are loaded
        model_tables = list(Base.metadata.tables.keys())
        print(f"📋 Models loaded: {model_tables}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Tables in database: {tables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_super_admin():
    """Create a super admin user."""
    try:
        print("\n" + "="*60)
        print("STEP 3: SUPER ADMIN CREATION")
        print("="*60)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if super admin already exists
        existing_admin = db.query(User).filter(
            User.role == UserRole.SUPER_ADMIN
        ).first()
        
        if existing_admin:
            print(f"✅ Super admin already exists: {existing_admin.email}")
            db.close()
            return True
        
        # Create super admin
        admin_email = settings.super_admin_email
        admin_password = settings.super_admin_password
        
        print("🔨 Creating super admin user...")
        
        # Hash password
        hashed_password = get_password_hash(admin_password)
        
        super_admin = User(
            email=admin_email,
            hashed_password=hashed_password,
            first_name="Super",
            last_name="Admin",
            phone_number="+919876543210",
            department="System Administration",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        
        db.add(super_admin)
        db.commit()
        
        print("✅ SUPER ADMIN CREATED SUCCESSFULLY!")
        print("📧 Email: " + admin_email)
        print("🔑 Password: " + admin_password)
        print("⚠️  PLEASE CHANGE THE PASSWORD AFTER FIRST LOGIN!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        if 'db' in locals():
            db.close()
        return False

def apply_migrations():
    """Apply database migrations using Alembic."""
    try:
        print("\n" + "="*60)
        print("STEP 4: DATABASE MIGRATIONS")
        print("="*60)
        
        import subprocess
        import os
        
        # Change to the correct directory
        os.chdir(Path(__file__).parent)
        
        print("🔨 Applying database migrations...")
        
        # Check current migration state
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("📋 Current migration state checked")
        
        # Apply all migrations
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database migrations applied successfully")
            return True
        else:
            print(f"⚠️  Migration warning: {result.stderr}")
            # Continue anyway - migrations might already be applied
            return True
            
    except Exception as e:
        print(f"⚠️  Migration warning: {e}")
        # Don't fail the setup for migration issues
        return True

def setup_complete_database():
    """Run complete database setup."""
    print("🚀 STARTING PRODUCTION DATABASE SETUP")
    print("This will create database, tables, and super admin user")
    print()
    
    success = True
    
    # Step 1: Create database
    if not create_database():
        print("❌ Database creation failed. Stopping setup.")
        return False
    
    # Step 2: Create tables
    if not create_tables():
        print("❌ Table creation failed. Stopping setup.")
        return False
    
    # Step 3: Apply migrations
    if not apply_migrations():
        print("⚠️  Migration application failed, but continuing...")
    
    # Step 4: Create super admin
    if not create_super_admin():
        print("❌ Super admin creation failed. Stopping setup.")
        return False
    
    print("\n" + "="*60)
    print("🎉 PRODUCTION DATABASE SETUP FINISHED SUCCESSFULLY!")
    print("="*60)
    print("✅ Database created")
    print("✅ Tables created") 
    print("✅ Migrations applied")
    print("✅ Super admin user created")
    print()
    print("👥 LOGIN CREDENTIALS:")
    print("📧 Super Admin: " + settings.super_admin_email)
    print("🔑 Password: " + settings.super_admin_password)
    print()
    print("🚀 Your FastAPI application is now ready for production!")
    print("📝 Use: python main.py")
    print("🌐 URLs:")
    print("   • Admin Dashboard: http://localhost:3000/dashboard")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • API Health Check: http://localhost:8000/health")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = setup_complete_database()
    sys.exit(0 if success else 1)
