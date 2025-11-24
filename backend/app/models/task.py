"""
Task model for assignment breakdown.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Task(Base):
    """Task represents a single actionable item from an assignment."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, index=True)

    # Task details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Priority (1 = highest/urgent, 2 = medium, 3 = low)
    priority = Column(Integer, default=2, nullable=False)

    # Dates
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_completed = Column(Boolean, default=False, index=True)

    # Order in task list
    order = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assignment = relationship("Assignment", back_populates="tasks")
    user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task {self.title} - Priority {self.priority}>"
