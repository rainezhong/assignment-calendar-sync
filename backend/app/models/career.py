"""
Career and job application models.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.session import Base


class UserProfile(Base):
    """User career profile with resume and job preferences."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Resume data
    resume_text = Column(Text, nullable=True)
    resume_pdf_url = Column(String, nullable=True)

    # Extracted information
    skills = Column(JSON, default=list)  # ["Python", "React", "Machine Learning"]
    education = Column(JSON, default=list)  # [{"school": "...", "degree": "...", "gpa": 3.8}]
    experience = Column(JSON, default=list)  # [{"company": "...", "role": "...", "duration": "..."}]

    # Contact info
    phone = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)

    # Job preferences
    desired_roles = Column(JSON, default=list)  # ["Software Engineer", "Data Analyst"]
    desired_locations = Column(JSON, default=list)  # ["New York", "Remote", "San Francisco"]
    desired_companies = Column(JSON, default=list)  # ["Google", "Microsoft", "Startup"]
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    job_type = Column(String, default="internship")  # "internship", "full-time", "part-time", "co-op"

    # Work authorization
    work_authorization = Column(String, nullable=True)  # "US Citizen", "F-1 Visa", etc.
    requires_sponsorship = Column(Boolean, default=False)

    # Notifications
    email_notifications = Column(Boolean, default=True)
    daily_match_limit = Column(Integer, default=10)

    # Usage limits (for cost control)
    cover_letters_generated = Column(Integer, default=0)
    cover_letter_limit = Column(Integer, default=10)  # Free tier: 10 per month
    usage_reset_date = Column(DateTime(timezone=True), server_default=func.now())

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="career_profile")
    applications = relationship("JobApplication", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id}>"


class JobListing(Base):
    """Cached job listings from various sources."""

    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False, index=True)  # LinkedIn job ID, Indeed job ID
    source = Column(String, nullable=False, index=True)  # "linkedin", "indeed", "handshake", "glassdoor"

    # Job details
    title = Column(String, nullable=False)
    company = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    remote_type = Column(String, nullable=True)  # "remote", "hybrid", "onsite"

    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String, default="USD")

    # Job metadata
    job_type = Column(String, nullable=False)  # "internship", "full-time", "part-time", "contract"
    experience_level = Column(String, nullable=True)  # "entry", "mid", "senior"

    # Content
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)

    # Application details
    application_method = Column(String, nullable=True)  # "easy_apply", "external", "email"
    application_url = Column(String, nullable=False)
    company_logo_url = Column(String, nullable=True)

    # Extracted data
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)

    # Metadata
    posted_date = Column(DateTime(timezone=True), nullable=True)
    expires_date = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, default=0)
    applicant_count = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    last_checked = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job")

    def __repr__(self):
        return f"<JobListing {self.title} at {self.company}>"


class JobMatch(Base):
    """AI-generated job matches for users."""

    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_listings.id"), nullable=False, index=True)

    # Match scoring
    match_score = Column(Float, nullable=False)  # 0.0-1.0
    match_reasons = Column(JSON, default=list)  # ["Skills match: 90%", "Location match", "Salary fits"]

    # Breakdown scores
    skill_match_score = Column(Float, nullable=True)
    location_match_score = Column(Float, nullable=True)
    salary_match_score = Column(Float, nullable=True)
    company_match_score = Column(Float, nullable=True)

    # Status
    status = Column(String, default="new", index=True)  # "new", "viewed", "saved", "dismissed", "applied"
    viewed_at = Column(DateTime(timezone=True), nullable=True)

    # User feedback (for learning)
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_feedback = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    job = relationship("JobListing", back_populates="matches")

    def __repr__(self):
        return f"<JobMatch user={self.user_id} job={self.job_id} score={self.match_score}>"


class JobApplication(Base):
    """Job applications submitted by users."""

    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_listings.id"), nullable=False, index=True)

    # Application materials
    resume_version = Column(String, nullable=True)  # Which resume was used
    resume_url = Column(String, nullable=True)
    cover_letter = Column(Text, nullable=True)

    # Application details
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    confirmation_number = Column(String, nullable=True)

    # Status tracking
    status = Column(String, default="submitted", index=True)
    # Statuses: submitted, viewed, phone_screen, interviewing, offer, rejected, withdrawn, accepted

    status_history = Column(JSON, default=list)
    # [{"status": "submitted", "date": "2024-01-01", "notes": "..."}]

    # Interview tracking
    interview_dates = Column(JSON, default=list)
    # [{"type": "phone", "date": "2024-01-15", "interviewer": "..."}]

    next_interview_date = Column(DateTime(timezone=True), nullable=True)

    # Offer details
    offer_amount = Column(Integer, nullable=True)
    offer_currency = Column(String, default="USD")
    offer_deadline = Column(DateTime(timezone=True), nullable=True)
    offer_accepted = Column(Boolean, nullable=True)

    # Follow-up
    last_follow_up = Column(DateTime(timezone=True), nullable=True)
    next_follow_up = Column(DateTime(timezone=True), nullable=True)
    follow_up_count = Column(Integer, default=0)

    # Contact information
    recruiter_name = Column(String, nullable=True)
    recruiter_email = Column(String, nullable=True)
    recruiter_phone = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Metadata
    applied_via = Column(String, nullable=True)  # "mobile_app", "linkedin", "indeed"
    referral_name = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    profile = relationship("UserProfile", back_populates="applications")
    job = relationship("JobListing", back_populates="applications")

    def __repr__(self):
        return f"<JobApplication {self.job.title} at {self.job.company} - {self.status}>"


class CoverLetterTemplate(Base):
    """User's cover letter templates."""

    __tablename__ = "cover_letter_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    # Template with placeholders: {{company}}, {{role}}, {{your_name}}, etc.

    is_default = Column(Boolean, default=False)

    # Usage stats
    use_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<CoverLetterTemplate {self.name}>"
