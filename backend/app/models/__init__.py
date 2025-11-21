"""
Database models.
"""
from app.models.user import User
from app.models.assignment import Assignment
from app.models.analytics import PerformanceMetric, Prediction
from app.models.career import UserProfile, JobListing, JobMatch, JobApplication, CoverLetterTemplate
from app.models.course import Course
from app.models.credential import Credential
from app.models.email import Email
from app.models.scrape_job import ScrapeJob

__all__ = [
    "User",
    "Assignment",
    "PerformanceMetric",
    "Prediction",
    "UserProfile",
    "JobListing",
    "JobMatch",
    "JobApplication",
    "CoverLetterTemplate",
    "Course",
    "Credential",
    "Email",
    "ScrapeJob",
]
