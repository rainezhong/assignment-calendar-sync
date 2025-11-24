"""
Job matching service - calculates match scores between jobs and users.
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.course import Course
from app.models.assignment import Assignment
from app.models.job_listing import JobListing


class JobMatchingService:
    """Service for calculating job match scores."""

    def __init__(self, user_id: int, db: AsyncSession):
        """
        Initialize job matching service.

        Args:
            user_id: User ID to calculate matches for
            db: Database session
        """
        self.user_id = user_id
        self.db = db
        self.user_profile = None

    async def get_user_profile(self) -> Dict:
        """
        Build user profile from courses and assignments.

        Returns:
            Dictionary with user skills, courses, and preferences
        """
        if self.user_profile:
            return self.user_profile

        # Get user's courses
        result = await self.db.execute(
            select(Course).where(
                Course.user_id == self.user_id,
                Course.approved == True
            )
        )
        courses = result.scalars().all()

        # Get user's assignments (to extract skills)
        result = await self.db.execute(
            select(Assignment).where(
                Assignment.user_id == self.user_id
            )
        )
        assignments = result.scalars().all()

        # Extract skills from courses and assignments
        user_skills = self._extract_user_skills(courses, assignments)

        # Build course map (code -> name)
        course_map = {course.code: course.name for course in courses if course.code}

        self.user_profile = {
            'skills': user_skills,
            'courses': courses,
            'course_map': course_map,
            'assignment_count': len(assignments),
        }

        return self.user_profile

    def _extract_user_skills(self, courses: List[Course], assignments: List[Assignment]) -> List[str]:
        """Extract skills from user's courses and assignments."""
        skills = set()

        # Map courses to skills
        course_skill_map = {
            'EECS 280': ['C++', 'Data Structures', 'Algorithms'],
            'EECS 281': ['C++', 'Data Structures', 'Algorithms', 'Problem Solving'],
            'EECS 370': ['C', 'Computer Architecture', 'Assembly'],
            'EECS 376': ['Algorithms', 'Theory', 'Mathematics'],
            'EECS 381': ['C++', 'Object-Oriented Programming'],
            'EECS 442': ['Python', 'Computer Vision', 'Machine Learning'],
            'EECS 445': ['Python', 'Machine Learning', 'Data Science'],
            'EECS 482': ['C', 'Operating Systems', 'Systems Programming'],
            'EECS 485': ['Python', 'Flask', 'JavaScript', 'React', 'Web Development', 'SQL'],
            'EECS 490': ['Programming Languages', 'Compilers'],
            'EECS 493': ['UI/UX', 'Design', 'JavaScript'],
            'EECS 494': ['Game Development', 'Unity', 'C#'],
        }

        # Add skills from courses
        for course in courses:
            if course.code in course_skill_map:
                skills.update(course_skill_map[course.code])

            # Also parse course name for keywords
            if course.name:
                name_lower = course.name.lower()
                if 'web' in name_lower:
                    skills.update(['Web Development', 'HTML', 'CSS', 'JavaScript'])
                if 'machine learning' in name_lower or 'ml' in name_lower:
                    skills.update(['Machine Learning', 'Python'])
                if 'data' in name_lower:
                    skills.update(['Data Science', 'Python', 'SQL'])
                if 'mobile' in name_lower:
                    skills.update(['Mobile Development'])

        # Add skills from assignment titles
        for assignment in assignments:
            title_lower = assignment.title.lower()

            # Programming languages
            if any(word in title_lower for word in ['python', 'py']):
                skills.add('Python')
            if any(word in title_lower for word in ['c++', 'cpp']):
                skills.add('C++')
            if any(word in title_lower for word in ['java']):
                skills.add('Java')
            if any(word in title_lower for word in ['javascript', 'js', 'react', 'node']):
                skills.add('JavaScript')
            if 'sql' in title_lower:
                skills.add('SQL')

            # Technologies
            if 'react' in title_lower:
                skills.add('React')
            if 'flask' in title_lower:
                skills.add('Flask')
            if 'django' in title_lower:
                skills.add('Django')
            if 'docker' in title_lower:
                skills.add('Docker')
            if 'aws' in title_lower:
                skills.add('AWS')

        return list(skills)

    async def calculate_match_score(self, job: JobListing) -> Dict:
        """
        Calculate comprehensive match score for a job.

        Args:
            job: Job listing to match against

        Returns:
            Dictionary with scores and match details
        """
        profile = await self.get_user_profile()

        # Extract job skills (from description or pre-extracted)
        job_skills = job.skills if job.skills else []

        # Calculate component scores
        skill_score = self._skill_match_score(job_skills, profile['skills'])
        course_score = self._course_relevance_score(job, profile['courses'])
        recency_score = self._recency_score(job)

        # Weighted total score (0-100)
        total_score = (
            skill_score * 0.50 +      # 50%: Skills match
            course_score * 0.35 +     # 35%: Course relevance
            recency_score * 0.15      # 15%: Recency
        )

        # Find matched and missing skills
        matched_skills = [skill for skill in job_skills if skill.lower() in [s.lower() for s in profile['skills']]]
        missing_skills = [skill for skill in job_skills if skill.lower() not in [s.lower() for s in profile['skills']]]

        # Generate match reasons
        match_reasons = self._generate_match_reasons(
            job, profile, matched_skills, skill_score, course_score
        )

        return {
            'match_score': round(total_score, 2),
            'skill_match_score': round(skill_score, 2),
            'course_relevance_score': round(course_score, 2),
            'recency_score': round(recency_score, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills[:5],  # Top 5 missing
            'match_reasons': match_reasons,
        }

    def _skill_match_score(self, job_skills: List[str], user_skills: List[str]) -> float:
        """
        Calculate skill overlap score (0-100).

        Args:
            job_skills: Skills required by job
            user_skills: Skills user has

        Returns:
            Score from 0-100
        """
        if not job_skills:
            return 50.0  # Neutral score if no skills listed

        # Case-insensitive matching
        job_skills_lower = [s.lower() for s in job_skills]
        user_skills_lower = [s.lower() for s in user_skills]

        # Count matches
        matches = sum(1 for skill in job_skills_lower if skill in user_skills_lower)

        # Calculate percentage
        match_percentage = (matches / len(job_skills)) * 100

        return match_percentage

    def _course_relevance_score(self, job: JobListing, courses: List[Course]) -> float:
        """
        Calculate course relevance score (0-100).

        Args:
            job: Job listing
            courses: User's courses

        Returns:
            Score from 0-100
        """
        if not courses:
            return 30.0  # Low but not zero if no courses

        job_text = (job.title + " " + (job.description or "")).lower()

        # Keywords that indicate job domain
        domain_keywords = {
            'software engineering': ['software', 'engineer', 'developer', 'programming', 'coding'],
            'data science': ['data', 'analytics', 'machine learning', 'ml', 'ai', 'statistics'],
            'web development': ['web', 'frontend', 'backend', 'full-stack', 'react', 'node'],
            'mobile': ['mobile', 'ios', 'android', 'app'],
            'systems': ['systems', 'infrastructure', 'devops', 'cloud', 'aws'],
            'security': ['security', 'cybersecurity', 'encryption'],
        }

        # Find job domain
        job_domains = []
        for domain, keywords in domain_keywords.items():
            if any(keyword in job_text for keyword in keywords):
                job_domains.append(domain)

        # Course relevance to domains
        relevant_courses = 0
        for course in courses:
            course_text = (course.code + " " + course.name).lower() if course.code and course.name else ""

            # Check if course is relevant to any job domain
            if 'software engineering' in job_domains:
                if any(code in course_text for code in ['280', '281', '370', '482', '485']):
                    relevant_courses += 1

            if 'data science' in job_domains:
                if any(word in course_text for word in ['445', 'data', 'machine learning', 'statistics']):
                    relevant_courses += 1

            if 'web development' in job_domains:
                if '485' in course_text or 'web' in course_text:
                    relevant_courses += 1

        # Score based on relevant courses
        if relevant_courses >= 3:
            return 90.0
        elif relevant_courses == 2:
            return 75.0
        elif relevant_courses == 1:
            return 60.0
        else:
            # Still give some score for having any technical courses
            return min(40.0 + len(courses) * 5, 50.0)

    def _recency_score(self, job: JobListing) -> float:
        """
        Calculate recency score (0-100).

        Args:
            job: Job listing

        Returns:
            Score from 0-100
        """
        if not job.posted_date:
            return 50.0  # Neutral if no date

        from datetime import datetime, timedelta

        now = datetime.utcnow()
        days_old = (now - job.posted_date).days

        if days_old <= 3:
            return 100.0
        elif days_old <= 7:
            return 85.0
        elif days_old <= 14:
            return 70.0
        elif days_old <= 30:
            return 50.0
        else:
            return 30.0

    def _generate_match_reasons(
        self,
        job: JobListing,
        profile: Dict,
        matched_skills: List[str],
        skill_score: float,
        course_score: float
    ) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []

        # Skill match reasons
        if skill_score >= 70:
            reasons.append(f"Strong skill match: You have {len(matched_skills)} of the required skills")
            if matched_skills:
                top_skills = matched_skills[:3]
                reasons.append(f"Matched skills: {', '.join(top_skills)}")
        elif skill_score >= 40:
            reasons.append(f"Moderate skill match: You have some of the required skills")

        # Course relevance reasons
        if course_score >= 70:
            reasons.append("Your coursework is highly relevant to this position")

        # Experience from assignments
        if profile['assignment_count'] > 10:
            reasons.append(f"You have completed {profile['assignment_count']} assignments demonstrating technical skills")

        # Location match (if implemented)
        # reasons.append("Location matches your preference")

        if not reasons:
            reasons.append("This position may help you develop new skills")

        return reasons[:5]  # Limit to top 5 reasons
