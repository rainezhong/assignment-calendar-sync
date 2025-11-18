"""
Analytics and prediction models for performance tracking.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.session import Base


class PerformanceMetric(Base):
    """Time series performance metrics."""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Metric type
    metric_type = Column(String, nullable=False, index=True)  # health_score, completion_rate, etc.
    metric_value = Column(Float, nullable=False)

    # Dimensions
    course_name = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True)  # academic, time_management, stress

    # Context
    metadata = Column(JSON, default=dict)
    notes = Column(String, nullable=True)

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="analytics")

    def __repr__(self):
        return f"<Metric {self.metric_type}={self.metric_value} at {self.recorded_at}>"


class Prediction(Base):
    """AI predictions for risk and optimization."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True, index=True)

    # Prediction details
    prediction_type = Column(String, nullable=False)  # risk, workload, deadline
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0-1

    # Risk assessment
    risk_level = Column(String, nullable=True)  # low, medium, high, critical
    risk_factors = Column(JSON, default=list)  # Contributing factors

    # Recommendations
    suggestions = Column(JSON, default=list)  # Action items

    # Validation (for learning)
    actual_value = Column(Float, nullable=True)
    was_accurate = Column(Boolean, nullable=True)

    # Timestamps
    predicted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction {self.prediction_type}={self.predicted_value}>"
