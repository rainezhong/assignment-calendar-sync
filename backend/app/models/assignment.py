"""
Assignment model with intelligence metadata.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.session import Base


class Assignment(Base):
    """Assignment with AI-powered analysis."""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)  # Link to Course table

    # Basic info
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    course_name = Column(String, nullable=False, index=True)  # Kept for backward compatibility
    assignment_type = Column(String, nullable=False)  # essay, project, exam, etc.

    # Dates
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)

    # AI Analysis (from assignment_intelligence.py)
    complexity_score = Column(Float, nullable=True)  # 0-1
    blooms_level = Column(String, nullable=True)  # remember, understand, apply, etc.
    cognitive_score = Column(Float, nullable=True)
    estimated_hours = Column(Float, nullable=True)

    # Skills and metadata (JSON fields)
    required_skills = Column(JSON, default=list)  # ["critical thinking", "research"]
    recommended_resources = Column(JSON, default=list)  # [{"title": "...", "url": "..."}]
    complexity_factors = Column(JSON, default=dict)  # Detailed breakdown

    # Performance tracking
    actual_hours_spent = Column(Float, default=0.0)
    difficulty_rating = Column(Integer, nullable=True)  # 1-5 user rating
    quality_score = Column(Float, nullable=True)  # Grade received

    # External IDs
    calendar_event_id = Column(String, nullable=True)
    email_thread_id = Column(String, nullable=True)

    # Integration tracking (for web scraping)
    source = Column(String, nullable=False, default="manual", index=True)  # "canvas", "gradescope", "gmail", "manual"
    source_id = Column(String, nullable=True, index=True)  # External ID in source system
    source_url = Column(String, nullable=True)  # Link to assignment in source system

    # Approval workflow
    approved = Column(Boolean, default=True, index=True)  # Manual entries auto-approved, scraped need approval
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Grading (from Canvas/Gradescope)
    points_possible = Column(Float, nullable=True)
    points_earned = Column(Float, nullable=True)
    grade_percentage = Column(Float, nullable=True)
    submission_status = Column(String, nullable=True)  # "submitted", "graded", "late", "missing", "not_submitted"
    submission_url = Column(String, nullable=True)
    graded_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="assignments")
    course = relationship("Course", back_populates="assignments")

    def __repr__(self):
        return f"<Assignment {self.title} - {self.course_name}>"
