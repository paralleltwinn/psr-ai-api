# =============================================================================
# POORNASREE AI - AUTHENTICATION DEPENDENCIES
# =============================================================================

"""
Authentication dependencies for FastAPI routes.
Handles role-based access control and user authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Union

from ..database.database import get_db
from ..database.models import User
from ..core.constants import UserRole, UserStatus
from .auth import verify_token
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        email = verify_token(token)
        
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user."""
    if current_user.status not in [UserStatus.ACTIVE, UserStatus.APPROVED]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account approval required"
        )
    return current_user


async def require_super_admin(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require Super Admin role."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    return current_user


async def require_admin_or_above(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require Admin or Super Admin role."""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_engineer_or_above(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require Engineer, Admin, or Super Admin role."""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineer access required"
        )
    return current_user


async def require_role(role: UserRole):
    """Factory function to create role-specific dependencies."""
    async def role_dependency(
        current_user: User = Depends(get_current_verified_user)
    ) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role.value} access required"
            )
        return current_user
    
    return role_dependency


async def require_any_role(roles: list[UserRole]):
    """Factory function to require any of the specified roles."""
    async def role_dependency(
        current_user: User = Depends(get_current_verified_user)
    ) -> User:
        if current_user.role not in roles:
            role_names = [role.value for role in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {', '.join(role_names)}"
            )
        return current_user
    
    return role_dependency


async def optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        email = verify_token(token)
        
        user = db.query(User).filter(User.email == email).first()
        if user and user.is_active:
            return user
        
        return None
        
    except Exception:
        return None


class RoleChecker:
    """Role-based access control checker."""
    
    def __init__(self, allowed_roles: Union[UserRole, list[UserRole]]):
        if isinstance(allowed_roles, UserRole):
            self.allowed_roles = [allowed_roles]
        else:
            self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_verified_user)) -> User:
        if current_user.role not in self.allowed_roles:
            role_names = [role.value for role in self.allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(role_names)}"
            )
        return current_user


# Predefined role checkers for common use cases
require_customer = RoleChecker(UserRole.CUSTOMER)
require_engineer = RoleChecker(UserRole.ENGINEER)
require_admin = RoleChecker(UserRole.ADMIN)
require_super_admin_role = RoleChecker(UserRole.SUPER_ADMIN)

# Multi-role checkers
require_staff = RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.ENGINEER])
require_management = RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN])


def check_permission(user: User, required_roles: Union[UserRole, list[UserRole]]) -> bool:
    """Check if user has required permissions."""
    if isinstance(required_roles, UserRole):
        required_roles = [required_roles]
    
    return user.role in required_roles


def check_resource_ownership(user: User, resource_user_id: int) -> bool:
    """Check if user owns the resource or has admin privileges."""
    return (user.id == resource_user_id or 
            user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN])


async def verify_resource_access(
    resource_user_id: int,
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Verify user can access resource (owns it or has admin privileges)."""
    if not check_resource_ownership(current_user, resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
    return current_user
