# =============================================================================
# POORNASREE AI - USER SERVICE
# =============================================================================

"""
User service for managing user accounts, profiles, and business logic.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..database.models import User, EngineerApplication, Notification, AuditLog
from ..database.database import get_db
from ..core.constants import UserRole, UserStatus, NotificationType, ApplicationStatus
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
                hashed_password=get_password_hash(user_data.password) if user_data.password else None,
                role=user_data.role or UserRole.CUSTOMER,
                otp_secret=generate_otp_secret(),
                is_active=True,
                status=UserStatus.PENDING  # New users start as pending
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            # Log user creation (non-critical, don't fail if this errors)
            try:
                self._log_user_activity(db_user, "User account created")
            except Exception as log_error:
                logger.warning(f"Failed to log user creation activity: {log_error}")
            
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
            
            user.status = UserStatus.ACTIVE  # Mark as active/verified
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
        status: Optional[UserStatus] = None,
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
            
            # Status filter
            if status is not None:
                db_query = db_query.filter(User.status == status)
            
            return db_query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get comprehensive user statistics for super admin dashboard."""
        try:
            # Total users
            total_users = self.db.query(func.count(User.id)).scalar() or 0
            
            # Users by role
            total_admins = self.db.query(func.count(User.id)).filter(
                User.role == UserRole.ADMIN
            ).scalar() or 0
            
            total_engineers = self.db.query(func.count(User.id)).filter(
                User.role == UserRole.ENGINEER
            ).scalar() or 0
            
            total_customers = self.db.query(func.count(User.id)).filter(
                User.role == UserRole.CUSTOMER
            ).scalar() or 0
            
            # Active/Inactive users
            active_users = self.db.query(func.count(User.id)).filter(
                User.is_active == True
            ).scalar() or 0
            
            inactive_users = total_users - active_users
            
            # Engineer-specific stats
            approved_engineers = self.db.query(func.count(User.id)).filter(
                and_(
                    User.role == UserRole.ENGINEER,
                    User.status == UserStatus.APPROVED
                )
            ).scalar() or 0
            
            # Customer-specific stats
            active_customers = self.db.query(func.count(User.id)).filter(
                and_(
                    User.role == UserRole.CUSTOMER,
                    User.is_active == True
                )
            ).scalar() or 0
            
            # Engineer applications
            pending_engineers = self.db.query(func.count(EngineerApplication.id)).filter(
                EngineerApplication.status == UserStatus.PENDING
            ).scalar() or 0
            
            rejected_engineers = self.db.query(func.count(EngineerApplication.id)).filter(
                EngineerApplication.status == UserStatus.REJECTED
            ).scalar() or 0
            
            # Recent registrations (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_registrations = (
                self.db.query(func.count(User.id))
                .filter(User.created_at >= week_ago)
                .scalar() or 0
            )
            
            return {
                "total_users": total_users,
                "total_admins": total_admins,
                "total_engineers": total_engineers,
                "total_customers": total_customers,
                "pending_engineers": pending_engineers,
                "approved_engineers": approved_engineers,
                "rejected_engineers": rejected_engineers,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "active_customers": active_customers,
                "recent_registrations": recent_registrations,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user statistics"
            )
    
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
                entity_type="User",  # Required field
                entity_id=str(user.id),  # Required field
                details=details,
                ip_address="system",  # Could be enhanced to track actual IP
                user_agent="system"
            )
            
            # Use a separate session to avoid interfering with main transaction
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=self.db.bind)
            with Session() as log_session:
                log_session.add(log_entry)
                log_session.commit()
            
        except Exception as e:
            logger.error(f"Error logging user activity: {e}")
            # Don't re-raise the exception to avoid breaking the main flow
    
    def get_admin_stats(self) -> Dict[str, Any]:
        """Get limited statistics for regular admin dashboard."""
        try:
            # Engineers
            total_engineers = self.db.query(func.count(User.id)).filter(
                User.role == UserRole.ENGINEER
            ).scalar() or 0
            
            approved_engineers = self.db.query(func.count(User.id)).filter(
                and_(
                    User.role == UserRole.ENGINEER,
                    User.status == UserStatus.APPROVED
                )
            ).scalar() or 0
            
            # Customers
            total_customers = self.db.query(func.count(User.id)).filter(
                User.role == UserRole.CUSTOMER
            ).scalar() or 0
            
            active_customers = self.db.query(func.count(User.id)).filter(
                and_(
                    User.role == UserRole.CUSTOMER,
                    User.is_active == True
                )
            ).scalar() or 0
            
            # Engineer applications
            pending_engineers = self.db.query(func.count(EngineerApplication.id)).filter(
                EngineerApplication.status == UserStatus.PENDING
            ).scalar() or 0
            
            rejected_engineers = self.db.query(func.count(EngineerApplication.id)).filter(
                EngineerApplication.status == UserStatus.REJECTED
            ).scalar() or 0
            
            return {
                "total_engineers": total_engineers,
                "approved_engineers": approved_engineers,
                "total_customers": total_customers,
                "active_customers": active_customers,
                "pending_engineers": pending_engineers,
                "rejected_engineers": rejected_engineers,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting admin stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve admin statistics"
            )
    
    def create_admin_user(self, email: str, password: str, first_name: str, 
                         last_name: str, phone_number: str = None, 
                         department: str = None) -> User:
        """Create a new admin user (Super Admin only)."""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create admin user
            hashed_password = get_password_hash(password)
            admin_user = User(
                email=email.lower(),
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                department=department,
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                is_active=True
            )
            
            self.db.add(admin_user)
            self.db.commit()
            self.db.refresh(admin_user)
            
            logger.info(f"Admin user created: {email}")
            return admin_user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating admin user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create admin user"
            )
    
    def get_all_admins(self) -> List[User]:
        """Get all admin users (Super Admin only)."""
        try:
            admins = self.db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
            ).order_by(User.created_at.desc()).all()
            
            return admins
            
        except Exception as e:
            logger.error(f"Error getting admin users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve admin users"
            )
    
    def deactivate_admin(self, admin_id: int, current_user_id: int) -> User:
        """Deactivate an admin user (Super Admin only)."""
        try:
            admin = self.db.query(User).filter(
                and_(
                    User.id == admin_id,
                    User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
                )
            ).first()
            
            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Admin user not found"
                )
            
            # Prevent self-deactivation
            if admin.id == current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate your own account"
                )
            
            admin.is_active = False
            admin.status = UserStatus.INACTIVE
            self.db.commit()
            self.db.refresh(admin)
            
            logger.info(f"Admin user deactivated: {admin.email}")
            return admin
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating admin: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate admin user"
            )
    
    def get_pending_engineer_applications(self, skip: int = 0, limit: int = 100) -> List[EngineerApplication]:
        """Get pending engineer applications with user details."""
        try:
            applications = (
                self.db.query(EngineerApplication)
                .filter(EngineerApplication.status == UserStatus.PENDING)
                .options(joinedload(EngineerApplication.user))
                .order_by(EngineerApplication.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            return applications
            
        except Exception as e:
            logger.error(f"Error getting pending engineer applications: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve pending engineer applications"
            )
    
    def approve_engineer_application(self, application_id: int, reviewer_id: int) -> EngineerApplication:
        """Approve engineer application and update user role."""
        try:
            application = self.db.query(EngineerApplication).filter(
                EngineerApplication.id == application_id
            ).first()
            
            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Engineer application not found"
                )
            
            if application.status != UserStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Application is not pending"
                )
            
            # Update application
            application.status = UserStatus.APPROVED
            application.reviewer_id = reviewer_id
            application.reviewed_at = datetime.utcnow()
            
            # Update user role
            user = application.user
            user.role = UserRole.ENGINEER
            user.status = UserStatus.APPROVED
            
            self.db.commit()
            self.db.refresh(application)
            
            # Log activity
            self._log_user_activity(user, "Engineer application approved", f"Application ID: {application_id}")
            
            logger.info(f"Engineer application approved: {application_id} for user {user.email}")
            return application
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error approving engineer application: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve engineer application"
            )
    
    def reject_engineer_application(self, application_id: int, reviewer_id: int, reason: str = None) -> EngineerApplication:
        """Reject engineer application."""
        try:
            application = self.db.query(EngineerApplication).filter(
                EngineerApplication.id == application_id
            ).first()
            
            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Engineer application not found"
                )
            
            if application.status != UserStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Application is not pending"
                )
            
            # Update application
            application.status = UserStatus.REJECTED
            application.reviewer_id = reviewer_id
            application.reviewed_at = datetime.utcnow()
            if reason:
                application.review_notes = reason
            
            self.db.commit()
            self.db.refresh(application)
            
            # Log activity
            user = application.user
            self._log_user_activity(user, "Engineer application rejected", f"Application ID: {application_id}, Reason: {reason}")
            
            logger.info(f"Engineer application rejected: {application_id} for user {user.email}")
            return application
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error rejecting engineer application: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reject engineer application"
            )


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
    status: Optional[UserStatus] = None,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """Search users."""
    service = UserService(db)
    return service.search_users(query, role, is_active, status, skip, limit)
