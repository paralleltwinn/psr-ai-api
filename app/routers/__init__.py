# =============================================================================
# POORNASREE AI - ROUTERS MODULE
# =============================================================================

"""
API routers module for organizing FastAPI endpoints.
Contains authentication, user management, and admin routes.
"""

from .auth import router as auth_router
from .users import router as users_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router", 
    "admin_router"
]
