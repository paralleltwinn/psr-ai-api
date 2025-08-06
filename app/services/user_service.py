# =============================================================================
# POORNASREE AI - USER SERVICE
# =============================================================================

"""
User service for managing user accounts, profiles, and business logic.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..database.models import User, EngineerApplication, Notification, AuditLog
from ..database.database import get_db
from ..core.constants import UserRole, NotificationType, ApplicationStatus
from ..auth.auth import get_password_hash, generate_otp_secret
from ..api.schemas import UserCreate, UserUpdate

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..database.models import User, EngineerApplication, Notification, AuditLog
from ..database.database import get_db
from ..core.constants import UserRole, NotificationType, UserStatus
from ..auth.auth import get_password_hash, generate_otp_secret
from ..api.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user account."""
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == user_data.email.lower()).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            db_user = User(
                email=user_data.email.lower(),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone_number=user_data.phone_number,
                hashed_password=get_password_hash(user_data.password),
                role=user_data.role or UserRole.CUSTOMER,
                otp_secret=generate_otp_secret(),
                is_active=True,
                is_verified=False
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            # Log user creation
            self._log_user_activity(db_user, "User account created")
            
            logger.info(f"User created successfully: {db_user.email}")
            return db_user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user account"
            )
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            return self.db.query(User).filter(User.email == email.lower()).first()
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {e}")
            return None
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user profile."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            # Log user update
            self._log_user_activity(user, f"User profile updated: {list(update_data.keys())}")
            
            logger.info(f"User updated successfully: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user profile"
            )
    
    def verify_user_email(self, user_id: int) -> User:
        """Mark user email as verified."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user.is_verified = True
            user.email_verified_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            # Log verification
            self._log_user_activity(user, "Email verified")
            
            logger.info(f"User email verified: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error verifying user email {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying email"
            )
    
    def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            # Log deactivation
            self._log_user_activity(user, "User account deactivated")
            
            logger.info(f"User deactivated: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deactivating user"
            )
    
    def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role."""
        try:
            return (
                self.db.query(User)
                .filter(User.role == role)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Error fetching users by role {role}: {e}")
            return []
    
    def search_users(
        self, 
        query: str, 
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Search users with filters."""
        try:
            db_query = self.db.query(User)
            
            # Text search
            if query:
                search_filter = or_(
                    User.first_name.ilike(f"%{query}%"),
                    User.last_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%")
                )
                db_query = db_query.filter(search_filter)
            
            # Role filter
            if role:
                db_query = db_query.filter(User.role == role)
            
            # Active filter
            if is_active is not None:
                db_query = db_query.filter(User.is_active == is_active)
            
            # Verified filter
            if is_verified is not None:
                db_query = db_query.filter(User.is_verified == is_verified)
            
            return db_query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            total_users = self.db.query(func.count(User.id)).scalar()
            active_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar()
            verified_users = self.db.query(func.count(User.id)).filter(User.is_verified == True).scalar()
            
            # Users by role
            role_stats = {}
            for role in UserRole:
                count = self.db.query(func.count(User.id)).filter(User.role == role).scalar()
                role_stats[role.value] = count
            
            # Recent registrations (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_registrations = (
                self.db.query(func.count(User.id))
                .filter(User.created_at >= week_ago)
                .scalar()
            )
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "users_by_role": role_stats,
                "recent_registrations": recent_registrations
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def create_engineer_application(self, user_id: int) -> EngineerApplication:
        """Create engineer role application."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if application already exists
            existing_app = (
                self.db.query(EngineerApplication)
                .filter(EngineerApplication.user_id == user_id)
                .filter(EngineerApplication.status == UserStatus.PENDING)
                .first()
            )
            
            if existing_app:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Engineer application already pending"
                )
            
            # Create application
            application = EngineerApplication(
                user_id=user_id,
                status=UserStatus.PENDING
            )
            
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            
            # Log application
            self._log_user_activity(user, "Engineer application submitted")
            
            logger.info(f"Engineer application created for user {user_id}")
            return application
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating engineer application for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating engineer application"
            )
    
    def _log_user_activity(self, user: User, action: str, details: Optional[str] = None):
        """Log user activity."""
        try:
            log_entry = AuditLog(
                user_id=user.id,
                action=action,
                details=details,
                ip_address="system",  # Could be enhanced to track actual IP
                user_agent="system"
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error logging user activity: {e}")


# Service functions for easy access
def create_user_account(db: Session, user_data: UserCreate) -> User:
    """Create a new user account."""
    service = UserService(db)
    return service.create_user(user_data)


def verify_user_email(db: Session, user_id: int) -> User:
    """Verify user email."""
    service = UserService(db)
    return service.verify_user_email(user_id)


def update_user_profile(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """Update user profile."""
    service = UserService(db)
    return service.update_user(user_id, user_data)


def deactivate_user_account(db: Session, user_id: int) -> User:
    """Deactivate user account."""
    service = UserService(db)
    return service.deactivate_user(user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    service = UserService(db)
    return service.get_user_by_email(email)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    service = UserService(db)
    return service.get_user_by_id(user_id)


def get_users_by_role(db: Session, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
    """Get users by role."""
    service = UserService(db)
    return service.get_users_by_role(role, skip, limit)


def search_users(
    db: Session,
    query: str,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """Search users."""
    service = UserService(db)
    return service.search_users(query, role, is_active, is_verified, skip, limit)
