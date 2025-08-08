# =============================================================================
# POORNASREE AI - DATABASE ROUTER
# =============================================================================

"""
Database health check and monitoring endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from ..auth.dependencies import get_current_active_user, require_admin_or_above
from ..database.models import User
from ..database.database import check_database_health, get_database_stats
from ..api.schemas import get_current_timestamp

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/database",
    tags=["Database"],
    responses={404: {"description": "Not found"}}
)


@router.get("/health", response_model=Dict[str, Any])
async def check_database_status():
    """
    ## 🗄️ Database Health Check
    
    Check the MySQL database connection and health status.
    
    **Public endpoint** - No authentication required for basic health monitoring.
    
    **Returns comprehensive database status including:**
    - Connection status and database information
    - MySQL version and uptime information
    - Active connections and performance metrics
    - Error details if any issues are detected
    
    **Example Response:**
    ```json
    {
      "service": "MySQL Database",
      "connected": true,
      "database_name": "poornasree_ai",
      "version": "8.0.33",
      "uptime": "5d 12h 30m",
      "total_connections": 8,
      "timestamp": "2025-08-08T10:30:00Z"
    }
    ```
    """
    try:
        health_status = await check_database_health()
        return health_status
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database health check failed: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_database_statistics(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## 📊 Database Statistics
    
    Get detailed database statistics and table information.
    
    **Admin Only Endpoint** - Only users with ADMIN or SUPER_ADMIN roles can access.
    
    **Returns:**
    - Total number of tables and rows
    - Database size information
    - Individual table statistics
    - Performance metrics
    
    **Example Response:**
    ```json
    {
      "total_tables": 8,
      "total_rows": 1250,
      "total_size_mb": 15.7,
      "tables": [
        {
          "name": "users",
          "rows": 45,
          "size_bytes": 1048576,
          "size_mb": 1.0
        }
      ],
      "timestamp": "2025-08-08T10:30:00Z",
      "requested_by": "John Doe"
    }
    ```
    """
    try:
        stats = get_database_stats()
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get database statistics: {stats['error']}"
            )
        
        # Add metadata
        stats.update({
            "timestamp": get_current_timestamp(),
            "requested_by": f"{current_user.first_name} {current_user.last_name}"
        })
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database statistics: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_database_detailed_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    ## 🔍 Detailed Database Status
    
    Get comprehensive database status including health check and basic statistics.
    
    **Authenticated endpoint** - Requires valid user session.
    
    **Returns:**
    - Database health and connection status
    - Basic table count and size information
    - Version and uptime details
    - Combined health and stats overview
    
    **Example Response:**
    ```json
    {
      "health": {
        "service": "MySQL Database",
        "connected": true,
        "version": "8.0.33"
      },
      "summary": {
        "total_tables": 8,
        "total_rows": 1250,
        "total_size_mb": 15.7
      },
      "status": "healthy",
      "timestamp": "2025-08-08T10:30:00Z"
    }
    ```
    """
    try:
        # Get health status
        health_status = await check_database_health()
        
        # Get basic stats (without admin restriction for summary)
        basic_stats = {
            "total_tables": 0,
            "total_rows": 0,
            "total_size_mb": 0
        }
        
        try:
            stats = get_database_stats()
            if "error" not in stats:
                basic_stats = {
                    "total_tables": stats.get("total_tables", 0),
                    "total_rows": stats.get("total_rows", 0),
                    "total_size_mb": stats.get("total_size_mb", 0)
                }
        except Exception as e:
            logger.warning(f"Could not get basic stats: {e}")
        
        # Determine overall status
        overall_status = "healthy"
        if not health_status.get("connected"):
            overall_status = "unhealthy"
        elif health_status.get("error"):
            overall_status = "degraded"
        
        return {
            "health": health_status,
            "summary": basic_stats,
            "status": overall_status,
            "timestamp": get_current_timestamp(),
            "checked_by": f"{current_user.first_name} {current_user.last_name}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get detailed database status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database status: {str(e)}"
        )


@router.get("/config", response_model=Dict[str, Any])
async def get_database_configuration(
    current_user: User = Depends(require_admin_or_above)
):
    """
    ## ⚙️ Database Configuration
    
    Get database configuration information (without sensitive data).
    
    **Admin Only Endpoint** - Only users with ADMIN or SUPER_ADMIN roles can access.
    
    **Returns:**
    - Database connection configuration (sanitized)
    - Connection pool settings
    - Environment information
    
    **Security Note:** Passwords and sensitive credentials are not included.
    """
    try:
        from ..config import settings
        
        # Parse database URL to extract components (without password)
        db_url = settings.database_url
        config_info = {
            "database_url_configured": bool(db_url),
            "debug_mode": settings.debug,
            "timestamp": get_current_timestamp(),
            "requested_by": f"{current_user.first_name} {current_user.last_name}"
        }
        
        # Extract database info safely
        if db_url:
            try:
                # Remove password from URL for security
                if '@' in db_url:
                    protocol_part = db_url.split('://')[0]
                    rest_part = db_url.split('://')[1]
                    if '@' in rest_part:
                        credentials_part, host_part = rest_part.split('@', 1)
                        username = credentials_part.split(':')[0] if ':' in credentials_part else credentials_part
                        sanitized_url = f"{protocol_part}://{username}:***@{host_part}"
                        config_info["database_url_sanitized"] = sanitized_url
                        
                        # Extract host and database name
                        if '/' in host_part:
                            host_info, db_name = host_part.rsplit('/', 1)
                            config_info["host"] = host_info
                            config_info["database_name"] = db_name
                            config_info["username"] = username
            except Exception:
                config_info["database_url_sanitized"] = "Error parsing URL"
        
        return config_info
        
    except Exception as e:
        logger.error(f"Failed to get database configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database configuration: {str(e)}"
        )
