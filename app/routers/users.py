from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import from reorganized modules
from ..api import schemas
from ..services import user_service
from ..database.models import User
from ..database.database import get_db
from ..auth.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.get("/notifications", response_model=List[schemas.NotificationResponse])
async def get_user_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    notifications = await user_service.get_user_notifications(db, current_user.id)
    return notifications


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    success = await user_service.mark_notification_read(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification marked as read"}
