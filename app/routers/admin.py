# =============================================================================
# POORNASREE AI - ADMIN ROUTES
# =============================================================================

"""
Admin endpoints for user management and dashboard statistics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import from reorganized modules
from ..api import schemas
from ..services import user_service, email_service
from ..database.models import User, EngineerApplication, Notification
from ..database.database import get_db
from ..auth.dependencies import require_admin_or_above, get_current_active_user
from ..core.constants import UserRole, UserStatus

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
async def get_admin_dashboard(
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    # Get basic user stats
    service = user_service.UserService(db)
    stats = service.get_user_stats()
    
    return schemas.DashboardStats(
        total_users=stats.get("total_users", 0),
        pending_engineers=0,  # Will be calculated properly
        total_admins=stats.get("users_by_role", {}).get("admin", 0),
        total_engineers=stats.get("users_by_role", {}).get("engineer", 0),
        total_customers=stats.get("users_by_role", {}).get("customer", 0),
        active_users=stats.get("active_users", 0),
        inactive_users=stats.get("total_users", 0) - stats.get("active_users", 0)
    )


@router.post("/create-admin", response_model=schemas.UserResponse)
async def create_admin(
    admin_data: schemas.AdminCreation,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Create new admin user"""
    # Check if user already exists
    existing_user = user_service.get_user_by_email(db, admin_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create admin user
    user_data = schemas.UserCreate(
        email=admin_data.email,
        first_name=admin_data.first_name,
        last_name=admin_data.last_name,
        phone_number=admin_data.phone_number,
        role=UserRole.ADMIN
    )
    
    user = user_service.create_user_account(db, user_data)
    user.is_verified = True
    user.status = UserStatus.ACTIVE
    db.commit()
    
    return user


@router.get("/users", response_model=schemas.UserListResponse)
async def get_all_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    
    return schemas.UserListResponse(
        users=users,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/engineer-applications", response_model=schemas.EngineerApplicationListResponse)
async def get_engineer_applications(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Get engineer applications for review"""
    applications = db.query(EngineerApplication).offset(skip).limit(limit).all()
    total = db.query(EngineerApplication).count()
    pending_count = db.query(EngineerApplication).filter(
        EngineerApplication.status == UserStatus.PENDING
    ).count()
    
    return schemas.EngineerApplicationListResponse(
        applications=applications,
        total=total,
        pending_count=pending_count,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.put("/engineer-applications/{application_id}/review")
async def review_engineer_application(
    application_id: int,
    review_data: schemas.EngineerApplicationReview,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Review engineer application"""
    application = db.query(EngineerApplication).filter(
        EngineerApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update application
    application.status = review_data.status
    application.review_notes = review_data.review_notes
    application.reviewer_id = current_user.id
    
    # Update user status
    user = db.query(User).filter(User.id == application.user_id).first()
    if user:
        user.status = review_data.status
    
    db.commit()
    
    # Send notification email
    if review_data.status == UserStatus.APPROVED:
        await email_service.send_engineer_approval_notification(user)
    elif review_data.status == UserStatus.REJECTED:
        await email_service.send_engineer_rejection_notification(
            user, review_data.review_notes or ""
        )
    
    return {"message": "Application reviewed successfully"}


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Deactivate a user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    user.status = UserStatus.INACTIVE
    db.commit()
    
    return {"message": "User deactivated successfully"}
