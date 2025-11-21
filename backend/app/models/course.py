"""
Course model for tracking academic courses.
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Course(Base):
    """Academic course model."""

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Course information
    name = Column(String, nullable=False)  # "Database Systems"
    code = Column(String, nullable=True, index=True)  # "CS 440"
    semester = Column(String, nullable=True)  # "Fall 2025"
    instructor = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Integration tracking
    source = Column(String, nullable=False, default="manual", index=True)  # "canvas", "gradescope", "manual"
    source_id = Column(String, nullable=True, index=True)  # ID in the source system
    source_url = Column(String, nullable=True)  # Link to course in source system

    # Status
    is_active = Column(Boolean, default=True)
    approved = Column(Boolean, default=False)  # User approval flag
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_synced = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="courses")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="course")

    def __repr__(self):
        return f"<Course {self.code or self.name}>"
