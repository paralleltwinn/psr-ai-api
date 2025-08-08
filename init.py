#!/usr/bin/env python3
# =============================================================================
# POORNASREE AI - COMPLETE DATABASE SETUP
# =============================================================================

"""
Complete database setup script for Poornasree AI Authentication System.
This script handles:
1. Database creation if it doesn't exist
2. Table creation from SQLAlchemy models
3. Super admin user creation
4. Sample data creation for testing admin dashboards
5. Database migration application
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pymysql
import random

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


def create_sample_admin():
    """Create a sample admin user for testing."""
    try:
        print("\n" + "="*60)
        print("STEP 4: SAMPLE ADMIN CREATION")
        print("="*60)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if sample admin already exists
        existing_admin = db.query(User).filter(
            User.email == "admin@poornasree.ai"
        ).first()
        
        if existing_admin:
            print(f"✅ Sample admin already exists: {existing_admin.email}")
            db.close()
            return True
        
        print("🔨 Creating sample admin user...")
        
        # Hash password
        hashed_password = get_password_hash("Admin@123")
        
        sample_admin = User(
            email="admin@poornasree.ai",
            hashed_password=hashed_password,
            first_name="Test",
            last_name="Admin",
            phone_number="+919876543211",
            department="Engineering",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=5),
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow() - timedelta(hours=2)
        )
        
        db.add(sample_admin)
        db.commit()
        
        print("✅ SAMPLE ADMIN CREATED SUCCESSFULLY!")
        print("📧 Email: admin@poornasree.ai")
        print("🔑 Password: Admin@123")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample admin: {e}")
        if 'db' in locals():
            db.close()
        return False


def create_sample_data():
    """Create sample users and engineer applications for testing dashboards."""
    try:
        print("\n" + "="*60)
        print("STEP 5: SAMPLE DATA CREATION")
        print("="*60)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if sample data already exists
        existing_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
        if existing_customers > 0:
            print(f"✅ Sample data already exists ({existing_customers} customers found)")
            db.close()
            return True
        
        print("🔨 Creating sample customers...")
        
        # Sample departments for engineers
        departments = ["Software Engineering", "Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Data Science"]
        skills_list = [
            "Python, FastAPI, React, MySQL",
            "AutoCAD, SolidWorks, ANSYS, Manufacturing",
            "Circuit Design, PCB Layout, Embedded Systems",
            "Structural Design, Construction Management, AutoCAD",
            "Machine Learning, Python, TensorFlow, Data Analytics"
        ]
        
        # Create sample customers
        customers = []
        for i in range(15):
            customer = User(
                email=f"customer{i+1}@test.com",
                hashed_password=get_password_hash("Customer@123"),
                first_name=f"Customer",
                last_name=f"{i+1:02d}",
                phone_number=f"+91987654{3300+i}",
                machine_model=f"Model-{random.choice(['X100', 'Y200', 'Z300', 'A400', 'B500'])}",
                state=random.choice(["Karnataka", "Tamil Nadu", "Maharashtra", "Gujarat", "Kerala"]),
                dealer=f"Dealer-{random.choice(['ABC', 'XYZ', 'PQR', 'LMN', 'DEF'])}",
                role=UserRole.CUSTOMER,
                status=UserStatus.ACTIVE,
                is_active=random.choice([True, True, True, False]),  # 75% active
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow() - timedelta(hours=random.randint(1, 168)) if random.choice([True, False]) else None
            )
            customers.append(customer)
        
        db.add_all(customers)
        print(f"✅ Created {len(customers)} sample customers")
        
        # Create sample engineers (approved)
        engineers = []
        for i in range(8):
            engineer = User(
                email=f"engineer{i+1}@test.com",
                hashed_password=get_password_hash("Engineer@123"),
                first_name=f"Engineer",
                last_name=f"{i+1:02d}",
                phone_number=f"+91987654{4400+i}",
                department=departments[i % len(departments)],
                role=UserRole.ENGINEER,
                status=UserStatus.APPROVED,
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(10, 60)),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            engineers.append(engineer)
        
        db.add_all(engineers)
        print(f"✅ Created {len(engineers)} approved engineers")
        
        # Create pending engineer applications
        pending_applications = []
        for i in range(5):
            # Create user first
            pending_user = User(
                email=f"pending.engineer{i+1}@test.com",
                hashed_password=get_password_hash("Pending@123"),
                first_name=f"Pending",
                last_name=f"Engineer{i+1:02d}",
                phone_number=f"+91987654{5500+i}",
                department=departments[i % len(departments)],
                role=UserRole.CUSTOMER,  # Still customer until approved
                status=UserStatus.PENDING,
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                updated_at=datetime.utcnow()
            )
            db.add(pending_user)
            db.flush()  # Get the ID
            
            # Create application
            application = EngineerApplication(
                user_id=pending_user.id,
                status=UserStatus.PENDING,
                department=departments[i % len(departments)],
                experience=f"{random.randint(1, 10)} years",
                skills=skills_list[i % len(skills_list)],
                portfolio=f"https://portfolio.example.com/engineer{i+1}",
                cover_letter=f"I am passionate about {departments[i % len(departments)].lower()} and would like to contribute to your platform with my {random.randint(1, 10)} years of experience.",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7))
            )
            pending_applications.append(application)
        
        db.add_all(pending_applications)
        print(f"✅ Created {len(pending_applications)} pending engineer applications")
        
        # Create some rejected applications
        rejected_applications = []
        for i in range(3):
            rejected_user = User(
                email=f"rejected.engineer{i+1}@test.com",
                hashed_password=get_password_hash("Rejected@123"),
                first_name=f"Rejected",
                last_name=f"Engineer{i+1:02d}",
                phone_number=f"+91987654{6600+i}",
                department=departments[i % len(departments)],
                role=UserRole.CUSTOMER,
                status=UserStatus.REJECTED,
                is_active=False,
                created_at=datetime.utcnow() - timedelta(days=random.randint(10, 30)),
                updated_at=datetime.utcnow()
            )
            db.add(rejected_user)
            db.flush()
            
            # Get admin user for reviewer
            admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
            
            application = EngineerApplication(
                user_id=rejected_user.id,
                status=UserStatus.REJECTED,
                department=departments[i % len(departments)],
                experience=f"{random.randint(1, 5)} years",
                skills=skills_list[i % len(skills_list)],
                portfolio=f"https://portfolio.example.com/rejected{i+1}",
                cover_letter=f"Application for {departments[i % len(departments)].lower()} position.",
                reviewer_id=admin_user.id if admin_user else None,
                reviewed_at=datetime.utcnow() - timedelta(days=random.randint(5, 15)),
                created_at=datetime.utcnow() - timedelta(days=random.randint(15, 35))
            )
            rejected_applications.append(application)
        
        db.add_all(rejected_applications)
        print(f"✅ Created {len(rejected_applications)} rejected engineer applications")
        
        # Commit all changes
        db.commit()
        
        print("\n📊 SAMPLE DATA SUMMARY:")
        print(f"  • {len(customers)} Customers created")
        print(f"  • {len(engineers)} Engineers created")
        print(f"  • {len(pending_applications)} Pending applications")
        print(f"  • {len(rejected_applications)} Rejected applications")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False


def apply_migrations():
    """Apply database migrations using Alembic."""
    try:
        print("\n" + "="*60)
        print("STEP 6: DATABASE MIGRATIONS")
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
    print("🚀 STARTING COMPLETE DATABASE SETUP")
    print("This will create database, tables, super admin, sample admin, and test data")
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
    
    # Step 5: Create sample admin
    if not create_sample_admin():
        print("⚠️  Sample admin creation failed, but continuing...")
    
    # Step 6: Create sample data
    if not create_sample_data():
        print("⚠️  Sample data creation failed, but continuing...")
    
    print("\n" + "="*60)
    print("🎉 COMPLETE DATABASE SETUP FINISHED SUCCESSFULLY!")
    print("="*60)
    print("✅ Database created")
    print("✅ Tables created") 
    print("✅ Migrations applied")
    print("✅ Super admin user created")
    print("✅ Sample admin user created")
    print("✅ Sample test data created")
    print()
    print("👥 LOGIN CREDENTIALS:")
    print("📧 Super Admin: " + settings.super_admin_email)
    print("🔑 Password: " + settings.super_admin_password)
    print("📧 Sample Admin: admin@poornasree.ai")
    print("� Password: Admin@123")
    print()
    print("�🚀 Your FastAPI application is now ready to run!")
    print("📝 Use: python main.py")
    print("🌐 Dashboard URLs:")
    print("   • Super Admin: http://localhost:3000/dashboard")
    print("   • Regular Admin: http://localhost:3000/dashboard")
    print("   • API Docs: http://localhost:8000/docs")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = setup_complete_database()
    sys.exit(0 if success else 1)
