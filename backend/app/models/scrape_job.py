"""
ScrapeJob model for tracking web scraping operations.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class ScrapeJob(Base):
    """Track web scraping jobs and their status."""

    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id"), nullable=True, index=True)

    # Job configuration
    service = Column(String(50), nullable=False, index=True)  # "canvas", "gradescope", "gmail"
    job_type = Column(String(50), nullable=False)  # "courses", "assignments", "emails", "grades", "full_sync"

    # Status tracking
    status = Column(String(50), nullable=False, default="pending", index=True)
    # Statuses: "pending", "running", "completed", "failed", "cancelled"

    # Results
    items_found = Column(Integer, default=0)  # Total items discovered
    items_new = Column(Integer, default=0)  # New items added
    items_updated = Column(Integer, default=0)  # Existing items updated
    items_skipped = Column(Integer, default=0)  # Items skipped (duplicates, errors)

    # Detailed results (JSON)
    results_summary = Column(JSON, default=dict)
    # Example: {"courses": 5, "assignments": 23, "emails": 45}

    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, default=dict)  # Stack trace, specific errors
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Performance metrics
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Configuration (JSON)
    config = Column(JSON, default=dict)
    # Example: {"fetch_assignments": true, "since_date": "2025-01-01", "course_ids": [1,2,3]}

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)  # When job should run
    triggered_by = Column(String(50), default="manual")  # "manual", "scheduled", "webhook", "auto"

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="scrape_jobs")
    credential = relationship("Credential", back_populates="scrape_jobs")

    def __repr__(self):
        return f"<ScrapeJob {self.service} {self.job_type} - {self.status}>"
