"""
Credential model for storing encrypted third-party service credentials.
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Credential(Base):
    """Encrypted credential storage for third-party integrations."""

    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Service identification
    service = Column(String(50), nullable=False, index=True)  # "canvas", "gradescope", "gmail"

    # Encrypted credential data (stores JSON with service-specific fields)
    # Canvas: {"api_token": "...", "base_url": "..."}
    # Gradescope: {"email": "...", "password": "..."}
    # Gmail: {"access_token": "...", "refresh_token": "...", "token_uri": "..."}
    encrypted_data = Column(Text, nullable=False)

    # Service-specific metadata
    institution_name = Column(String, nullable=True)  # e.g., "University of Michigan"
    institution_url = Column(String, nullable=True)  # e.g., "umich.instructure.com"

    # Status tracking
    is_active = Column(Boolean, default=True)
    last_synced = Column(DateTime(timezone=True), nullable=True)
    last_sync_status = Column(String, nullable=True)  # "success", "failed"
    last_error = Column(Text, nullable=True)
    sync_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="credentials")
    scrape_jobs = relationship("ScrapeJob", back_populates="credential")

    # Ensure one credential per service per user
    __table_args__ = (
        UniqueConstraint('user_id', 'service', name='uix_user_service'),
    )

    def __repr__(self):
        return f"<Credential user_id={self.user_id} service={self.service}>"
