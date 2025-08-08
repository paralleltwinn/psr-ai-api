# =============================================================================
# POORNASREE AI - DATABASE CONNECTION SETUP
# =============================================================================

"""
Database connection and session management.
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from datetime import datetime
import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Create database instance for async operations
database = Database(settings.database_url)

# Create metadata and base class
metadata = MetaData()
Base = declarative_base(metadata=metadata)


async def get_database():
    """Get database connection for async operations."""
    return database


def get_db():
    """Get database session for sync operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def check_database_health():
    """Check database connection and health status."""
    health_status = {
        "service": "MySQL Database",
        "connected": False,
        "database_name": settings.database_url.split('/')[-1] if '/' in settings.database_url else "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "error": None,
        "version": None,
        "uptime": None,
        "total_connections": None
    }
    
    try:
        # Test basic connection
        db = SessionLocal()
        
        # Execute a simple query to test connectivity
        result = db.execute(text("SELECT 1 as health_check"))
        health_check_result = result.scalar()
        
        if health_check_result == 1:
            health_status["connected"] = True
            
            # Get MySQL version
            try:
                version_result = db.execute(text("SELECT VERSION() as version"))
                version = version_result.scalar()
                health_status["version"] = version
            except Exception as e:
                logger.warning(f"Could not get MySQL version: {e}")
            
            # Get MySQL uptime
            try:
                uptime_result = db.execute(text("SHOW STATUS LIKE 'Uptime'"))
                uptime_row = uptime_result.fetchone()
                if uptime_row:
                    uptime_seconds = int(uptime_row[1])
                    uptime_days = uptime_seconds // 86400
                    uptime_hours = (uptime_seconds % 86400) // 3600
                    uptime_minutes = (uptime_seconds % 3600) // 60
                    health_status["uptime"] = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m"
            except Exception as e:
                logger.warning(f"Could not get MySQL uptime: {e}")
            
            # Get connection count
            try:
                connections_result = db.execute(text("SHOW STATUS LIKE 'Threads_connected'"))
                connections_row = connections_result.fetchone()
                if connections_row:
                    health_status["total_connections"] = int(connections_row[1])
            except Exception as e:
                logger.warning(f"Could not get MySQL connection count: {e}")
        
        db.close()
        
    except Exception as e:
        health_status["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_status


def get_database_stats():
    """Get database statistics and table information."""
    try:
        db = SessionLocal()
        
        # Get table information
        tables_result = db.execute(text("""
            SELECT table_name, table_rows, data_length, index_length
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            ORDER BY table_name
        """))
        
        tables_info = []
        total_rows = 0
        total_size = 0
        
        for row in tables_result:
            table_name, table_rows, data_length, index_length = row
            table_rows = table_rows or 0
            data_length = data_length or 0
            index_length = index_length or 0
            table_size = data_length + index_length
            
            tables_info.append({
                "name": table_name,
                "rows": table_rows,
                "size_bytes": table_size,
                "size_mb": round(table_size / 1024 / 1024, 2)
            })
            
            total_rows += table_rows
            total_size += table_size
        
        db.close()
        
        return {
            "total_tables": len(tables_info),
            "total_rows": total_rows,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "tables": tables_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {"error": str(e)}


async def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


async def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
