"""
Initialize database schema.
Run this once to create all tables.
"""
import asyncio
from sqlalchemy import create_engine
from app.db.session import Base
from app.core.config import settings

# Import all models to ensure they're registered with Base
from app.models import (
    User,
    Assignment,
    Prediction,
    PerformanceMetric,
    UserProfile,
    JobListing,
    JobMatch,
    JobApplication,
    CoverLetterTemplate
)


def init_db():
    """Create all database tables."""
    print("🔧 Initializing database...")

    # Use sync engine for schema creation
    engine = create_engine(str(settings.DATABASE_URL).replace("+asyncpg", ""))

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("✅ Database initialized successfully!")
    print(f"📊 Created tables: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    init_db()
