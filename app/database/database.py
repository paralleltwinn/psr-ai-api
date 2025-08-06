# =============================================================================
# POORNASREE AI - DATABASE CONNECTION SETUP
# =============================================================================

"""
Database connection and session management.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from ..config import settings

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


async def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


async def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
