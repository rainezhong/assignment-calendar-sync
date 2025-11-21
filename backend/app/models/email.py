"""
Email model for aggregated academic emails.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Email(Base):
    """Academic email aggregation model."""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Email details
    subject = Column(String(500), nullable=True)
    sender = Column(String(255), nullable=True)
    sender_email = Column(String(255), nullable=True, index=True)
    body = Column(Text, nullable=True)
    html_body = Column(Text, nullable=True)

    # Attachments (stored as JSON array)
    attachments = Column(JSON, default=list)  # [{"filename": "...", "url": "...", "size": 123}]

    # Gmail-specific fields
    gmail_message_id = Column(String(255), unique=True, nullable=True, index=True)
    gmail_thread_id = Column(String(255), nullable=True, index=True)
    gmail_labels = Column(JSON, default=list)  # ["INBOX", "UNREAD", "IMPORTANT"]

    # Classification
    is_academic = Column(Boolean, default=False, index=True)
    category = Column(String(50), nullable=True, index=True)  # "assignment", "grade", "announcement", "course_update", "other"
    confidence_score = Column(Float, nullable=True)  # 0-1, how confident we are in the classification

    # Extracted information (using AI/NLP)
    extracted_dates = Column(JSON, default=list)  # [{"date": "2025-12-15", "context": "assignment due"}]
    extracted_action_items = Column(JSON, default=list)  # ["Submit homework", "Join Zoom meeting"]
    keywords = Column(JSON, default=list)  # ["midterm", "project", "deadline"]

    # Relations to other entities
    related_course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)
    related_assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True, index=True)

    # Approval workflow
    approved = Column(Boolean, default=False, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Timestamps
    received_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="emails")
    course = relationship("Course", back_populates="emails")
    assignment = relationship("Assignment")

    def __repr__(self):
        return f"<Email from={self.sender_email} subject={self.subject[:50]}>"
