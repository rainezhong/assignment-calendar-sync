"""
Admin endpoints for database management.
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine
from app.db.session import Base
from app.core.config import settings

# Import all models
from app.models import (
    User,
    Assignment,
    CalendarEvent,
    Prediction,
    PerformanceMetric,
    JobApplication,
    Resume
)

router = APIRouter()


@router.post("/init-db")
async def initialize_database():
    """
    Initialize database schema by creating all tables.
    This should only be run once during initial setup.
    """
    try:
        # Use sync engine for schema creation
        engine = create_engine(str(settings.DATABASE_URL).replace("+asyncpg", ""))

        # Create all tables
        Base.metadata.create_all(bind=engine)

        tables = list(Base.metadata.tables.keys())

        return {
            "status": "success",
            "message": "Database initialized successfully",
            "tables_created": tables
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
