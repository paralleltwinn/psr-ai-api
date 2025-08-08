# =============================================================================
# POORNASREE AI - ADMIN ROUTES
# =============================================================================

"""
Admin endpoints for user management and dashboard statistics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

# Import from reorganized modules
from ..api import schemas
from ..api.schemas import (
    SuperAdminDashboardResponse, AdminDashboardResponse, SuperAdminStatsResponse, 
    AdminStatsResponse, AdminCreateRequest, ApplicationReviewRequest, 
    EngineerApplicationResponse, UserResponse, AdminListResponse
)
from ..services import user_service, email_service
from ..services.user_service import UserService
from ..database.models import User, EngineerApplication, Notification
from ..database.database import get_db
from ..auth.dependencies import require_admin_or_above, require_super_admin, get_current_active_user
from ..auth.auth import get_password_hash, verify_password
from ..core.constants import UserRole, UserStatus

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=SuperAdminDashboardResponse)
async def get_super_admin_dashboard(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get super admin dashboard statistics (Super Admin only)"""
    try:
        service = UserService(db)
        stats = service.get_user_stats()
        
        return SuperAdminDashboardResponse(
            success=True,
            message="Super admin dashboard statistics retrieved successfully",
            stats=SuperAdminStatsResponse(**stats)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard statistics: {str(e)}"
        )


@router.get("/stats", response_model=AdminDashboardResponse)
async def get_admin_stats(
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics (limited access for regular admins)"""
    try:
        service = UserService(db)
        stats = service.get_admin_stats()
        
        return AdminDashboardResponse(
            success=True,
            message="Admin dashboard statistics retrieved successfully",
            stats=AdminStatsResponse(**stats)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve admin statistics: {str(e)}"
        )


@router.get("/engineers/pending", response_model=List[EngineerApplicationResponse])
async def get_pending_engineers(
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of applications to retrieve"),
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Get pending engineer applications for admin review"""
    try:
        service = UserService(db)
        applications = service.get_pending_engineer_applications(skip=skip, limit=limit)
        
        return [EngineerApplicationResponse.from_orm(app) for app in applications]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pending engineers: {str(e)}"
        )


@router.put("/engineers/{engineer_id}/approve", response_model=EngineerApplicationResponse)
async def approve_engineer(
    engineer_id: int,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Approve engineer application"""
    try:
        service = UserService(db)
        approved_application = service.approve_engineer_application(
            application_id=engineer_id,
            reviewer_id=current_user.id
        )
        
        # Send approval email
        try:
            await email_service.send_engineer_approval_notification(approved_application.user)
        except Exception as email_error:
            print(f"Failed to send approval email: {email_error}")
        
        return EngineerApplicationResponse.from_orm(approved_application)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve engineer: {str(e)}"
        )


@router.put("/engineers/{engineer_id}/reject", response_model=EngineerApplicationResponse)
async def reject_engineer(
    engineer_id: int,
    review_data: ApplicationReviewRequest,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Reject engineer application"""
    try:
        service = UserService(db)
        rejected_application = service.reject_engineer_application(
            application_id=engineer_id,
            reviewer_id=current_user.id,
            reason=review_data.reason
        )
        
        # Send rejection email
        try:
            await email_service.send_engineer_rejection_notification(
                rejected_application.user, review_data.reason or "Application reviewed and rejected by admin"
            )
        except Exception as email_error:
            print(f"Failed to send rejection email: {email_error}")
        
        return EngineerApplicationResponse.from_orm(rejected_application)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject engineer: {str(e)}"
        )
@router.post("/create-admin", response_model=UserResponse)
async def create_admin(
    admin_data: AdminCreateRequest,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Create new admin user (Super Admin only)"""
    try:
        service = UserService(db)
        new_admin = service.create_admin_user(
            email=admin_data.email,
            password=admin_data.password,
            first_name=admin_data.first_name,
            last_name=admin_data.last_name,
            phone_number=admin_data.phone_number,
            department=admin_data.department
        )
        
        # Send welcome email
        try:
            await email_service.send_welcome_email(new_admin.email, new_admin.first_name)
        except Exception as email_error:
            print(f"Failed to send welcome email: {email_error}")
        
        return UserResponse.from_orm(new_admin)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin user"
        )


@router.put("/profile", response_model=schemas.ProfileUpdateResponse)
async def update_super_admin_profile(
    profile_data: schemas.SuperAdminProfileUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Update super admin profile (Super Admin only)"""
    try:
        # Verify current password
        if not verify_password(profile_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Current password is incorrect",
                    "error_code": "INVALID_PASSWORD"
                }
            )
        
        # Check if new email is already taken (if email is being updated)
        if profile_data.email and profile_data.email != current_user.email:
            existing_user = user_service.get_user_by_email(db, profile_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "message": "Email already registered",
                        "error_code": "EMAIL_EXISTS"
                    }
                )
            current_user.email = profile_data.email
        
        # Update password if provided
        if profile_data.new_password:
            current_user.hashed_password = get_password_hash(profile_data.new_password)
        
        # Update other fields if provided
        if profile_data.first_name:
            current_user.first_name = profile_data.first_name
        if profile_data.last_name:
            current_user.last_name = profile_data.last_name
        if profile_data.phone_number:
            current_user.phone_number = profile_data.phone_number
        
        db.commit()
        db.refresh(current_user)
        
        return schemas.ProfileUpdateResponse(
            success=True,
            message="Profile updated successfully",
            user=schemas.UserResponse.from_orm(current_user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to update profile",
                "error_code": "UPDATE_FAILED"
            }
        )


@router.get("/admins", response_model=schemas.AdminListResponse)
async def get_all_admins(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get all admin users (Super Admin only)"""
    try:
        admins = db.query(User).filter(
            User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
        ).all()
        
        return schemas.AdminListResponse(
            success=True,
            message="Admin users retrieved successfully",
            admins=[schemas.UserResponse.from_orm(admin) for admin in admins],
            total_count=len(admins)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to retrieve admin users",
                "error_code": "FETCH_FAILED"
            }
        )


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


@router.delete("/users/{user_id}", response_model=schemas.APISuccessResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """Deactivate a user account"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND"
                }
            )
        
        # Prevent super admin from deactivating themselves
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Cannot deactivate your own account",
                    "error_code": "SELF_DEACTIVATION"
                }
            )
        
        user.is_active = False
        user.status = UserStatus.INACTIVE
        db.commit()
        
        return schemas.APISuccessResponse(
            success=True,
            message=f"User '{user.first_name} {user.last_name}' deactivated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to deactivate user",
                "error_code": "DEACTIVATION_FAILED"
            }
        )
