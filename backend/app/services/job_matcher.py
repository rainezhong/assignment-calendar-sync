"""
AI-powered job matching service.
Matches user profiles with job listings using NLP and scoring algorithms.
"""
from typing import List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re
from collections import Counter

from app.models.career import UserProfile, JobListing, JobMatch


class JobMatcher:
    """Match jobs to user profiles using multiple scoring factors."""

    def __init__(self):
        pass

    async def match_jobs_for_user(
        self,
        user_profile: UserProfile,
        jobs: List[JobListing],
        db: AsyncSession
    ) -> List[JobMatch]:
        """
        Generate matches for a user across multiple jobs.

        Args:
            user_profile: User's career profile
            jobs: List of job listings to match against
            db: Database session

        Returns:
            List of JobMatch objects sorted by score
        """
        matches = []

        for job in jobs:
            # Calculate match score and reasons
            match_result = await self.calculate_match(user_profile, job)

            if match_result['overall_score'] >= 0.3:  # Minimum threshold
                match = JobMatch(
                    user_id=user_profile.user_id,
                    job_id=job.id,
                    match_score=match_result['overall_score'],
                    match_reasons=match_result['reasons'],
                    skill_match_score=match_result['skill_score'],
                    location_match_score=match_result['location_score'],
                    salary_match_score=match_result['salary_score'],
                    company_match_score=match_result['company_score'],
                    status='new'
                )
                matches.append(match)

        # Sort by match score
        matches.sort(key=lambda m: m.match_score, reverse=True)

        return matches

    async def calculate_match(
        self,
        profile: UserProfile,
        job: JobListing
    ) -> Dict:
        """
        Calculate comprehensive match score between user and job.

        Returns:
            Dictionary with overall_score, reasons, and breakdown scores
        """
        # Calculate individual scores
        skill_score = self._calculate_skill_match(profile, job)
        location_score = self._calculate_location_match(profile, job)
        salary_score = self._calculate_salary_match(profile, job)
        company_score = self._calculate_company_match(profile, job)
        role_score = self._calculate_role_match(profile, job)

        # Weighted overall score
        weights = {
            'skills': 0.35,
            'location': 0.20,
            'salary': 0.15,
            'company': 0.15,
            'role': 0.15,
        }

        overall_score = (
            skill_score * weights['skills'] +
            location_score * weights['location'] +
            salary_score * weights['salary'] +
            company_score * weights['company'] +
            role_score * weights['role']
        )

        # Generate human-readable reasons
        reasons = self._generate_match_reasons(
            profile, job,
            skill_score, location_score, salary_score, company_score, role_score
        )

        return {
            'overall_score': round(overall_score, 3),
            'skill_score': round(skill_score, 3),
            'location_score': round(location_score, 3),
            'salary_score': round(salary_score, 3),
            'company_score': round(company_score, 3),
            'role_score': round(role_score, 3),
            'reasons': reasons,
        }

    def _calculate_skill_match(self, profile: UserProfile, job: JobListing) -> float:
        """
        Calculate skill match score (0-1).

        Compares user's skills with job's required/preferred skills.
        """
        user_skills = set(s.lower() for s in (profile.skills or []))

        # Extract skills from job description if not already extracted
        job_skills = set(s.lower() for s in (job.required_skills or []))

        if not job_skills and job.description:
            job_skills = self._extract_skills_from_text(job.description.lower())

        if not job_skills:
            return 0.5  # Neutral score if we can't extract skills

        # Calculate overlap
        matching_skills = user_skills & job_skills
        if not job_skills:
            return 0.5

        match_percentage = len(matching_skills) / len(job_skills)

        # Bonus for having more skills than required
        extra_skills = user_skills - job_skills
        bonus = min(0.2, len(extra_skills) * 0.02)

        return min(1.0, match_percentage + bonus)

    def _calculate_location_match(self, profile: UserProfile, job: JobListing) -> float:
        """
        Calculate location match score (0-1).
        """
        desired_locations = [loc.lower() for loc in (profile.desired_locations or [])]
        job_location = job.location.lower()

        # Perfect match
        for desired in desired_locations:
            if desired in job_location or job_location in desired:
                return 1.0

        # Remote preference
        if 'remote' in desired_locations and ('remote' in job_location or job.remote_type == 'remote'):
            return 1.0

        # Partial match (same city or state)
        for desired in desired_locations:
            # Extract city/state
            desired_parts = set(desired.split(','))
            job_parts = set(job_location.split(','))

            if desired_parts & job_parts:
                return 0.7

        return 0.0  # No match

    def _calculate_salary_match(self, profile: UserProfile, job: JobListing) -> float:
        """
        Calculate salary match score (0-1).
        """
        if not profile.min_salary or not job.salary_min:
            return 0.5  # Neutral if salary not specified

        # Job meets minimum requirement
        if job.salary_min >= profile.min_salary:
            # Bonus for higher salaries
            if profile.max_salary:
                if job.salary_min >= profile.max_salary:
                    return 1.0
                else:
                    # Linear score between min and max
                    range_size = profile.max_salary - profile.min_salary
                    above_min = job.salary_min - profile.min_salary
                    return 0.7 + (above_min / range_size) * 0.3
            return 0.8

        # Job below minimum
        salary_ratio = job.salary_min / profile.min_salary
        return max(0.0, salary_ratio)

    def _calculate_company_match(self, profile: UserProfile, job: JobListing) -> float:
        """
        Calculate company match score (0-1).
        """
        desired_companies = [c.lower() for c in (profile.desired_companies or [])]
        job_company = job.company.lower()

        # Direct match
        if any(desired in job_company or job_company in desired for desired in desired_companies):
            return 1.0

        # No preference specified
        if not desired_companies:
            return 0.5

        return 0.0

    def _calculate_role_match(self, profile: UserProfile, job: JobListing) -> float:
        """
        Calculate role/title match score (0-1).
        """
        desired_roles = [r.lower() for r in (profile.desired_roles or [])]
        job_title = job.title.lower()

        # Direct match
        for desired in desired_roles:
            if desired in job_title or job_title in desired:
                return 1.0

        # Partial match (keywords)
        desired_keywords = set()
        for role in desired_roles:
            desired_keywords.update(role.split())

        job_keywords = set(job_title.split())

        matching_keywords = desired_keywords & job_keywords
        if matching_keywords:
            return len(matching_keywords) / max(len(desired_keywords), len(job_keywords))

        return 0.0

    def _generate_match_reasons(
        self,
        profile: UserProfile,
        job: JobListing,
        skill_score: float,
        location_score: float,
        salary_score: float,
        company_score: float,
        role_score: float
    ) -> List[str]:
        """
        Generate human-readable match reasons.
        """
        reasons = []

        # Skills
        if skill_score >= 0.8:
            user_skills = set(s.lower() for s in (profile.skills or []))
            job_skills = set(s.lower() for s in (job.required_skills or []))
            if job.description:
                job_skills.update(self._extract_skills_from_text(job.description.lower()))
            matching = user_skills & job_skills
            if matching:
                reasons.append(f"🎯 Strong skills match: {', '.join(list(matching)[:3])}")
        elif skill_score >= 0.5:
            reasons.append(f"✅ Good skills fit ({int(skill_score * 100)}% match)")

        # Location
        if location_score == 1.0:
            reasons.append(f"📍 Perfect location: {job.location}")
        elif location_score >= 0.7:
            reasons.append(f"📍 Location nearby: {job.location}")

        # Salary
        if salary_score >= 0.8 and job.salary_min:
            reasons.append(f"💰 Salary meets expectations: ${job.salary_min:,}+")

        # Company
        if company_score == 1.0:
            reasons.append(f"⭐ Target company: {job.company}")

        # Role
        if role_score >= 0.8:
            reasons.append(f"💼 Desired role: {job.title}")

        # Job type match
        if profile.job_type == job.job_type:
            reasons.append(f"✨ {job.job_type.capitalize()} position")

        return reasons

    def _extract_skills_from_text(self, text: str) -> set:
        """
        Extract common tech skills from text.
        """
        common_skills = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'machine learning', 'data analysis', 'git', 'agile', 'scrum'
        }

        found_skills = set()
        text_lower = text.lower()

        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.add(skill)

        return found_skills


# Helper function for API endpoints
async def create_matches_for_user(
    user_id: int,
    job_ids: List[int],
    db: AsyncSession
) -> List[JobMatch]:
    """
    Create job matches for a user.

    Args:
        user_id: User ID
        job_ids: List of job listing IDs to match
        db: Database session

    Returns:
        List of created matches
    """
    # Get user profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise ValueError("User profile not found")

    # Get jobs
    result = await db.execute(
        select(JobListing).where(JobListing.id.in_(job_ids))
    )
    jobs = result.scalars().all()

    # Create matches
    matcher = JobMatcher()
    matches = await matcher.match_jobs_for_user(profile, jobs, db)

    # Save to database
    for match in matches:
        db.add(match)

    await db.commit()

    return matches
