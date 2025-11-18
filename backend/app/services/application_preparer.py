"""
Application preparation service - Pre-fills ALL application data.
Creates a "ready to submit" application that user just needs to approve.
"""
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI
import json

from app.models.career import UserProfile, JobListing, JobApplication
from app.core.config import settings


class ApplicationPreparer:
    """Prepares complete applications ready for one-tap submission."""

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def prepare_application(
        self,
        profile: UserProfile,
        job: JobListing,
        db: AsyncSession
    ) -> Optional[Dict]:
        """
        Prepare a complete application with all fields filled.

        Returns:
            Dictionary with all prepared data, or None if preparation fails
        """
        # Check if already applied
        result = await db.execute(
            select(JobApplication).where(
                JobApplication.user_id == profile.user_id,
                JobApplication.job_id == job.id
            )
        )
        if result.scalar_one_or_none():
            return None  # Already applied

        # Check usage limits (reset monthly)
        await self._check_and_reset_usage(profile, db)

        # Check if user has hit cover letter limit
        if profile.cover_letters_generated >= profile.cover_letter_limit:
            print(f"User {profile.user_id} hit cover letter limit ({profile.cover_letter_limit})")
            # Still prepare application, but skip AI cover letter generation
            use_ai_cover_letter = False
        else:
            use_ai_cover_letter = True

        # Prepare all application fields
        prepared_data = {
            # Basic info (from profile)
            'personal_info': self._prepare_personal_info(profile),

            # Resume & documents
            'resume_url': profile.resume_pdf_url,
            'resume_text': profile.resume_text,

            # Cover letter (use AI if within limits, else template)
            'cover_letter': await self._generate_cover_letter(profile, job, use_ai=use_ai_cover_letter),

            # Common application questions
            'answers': await self._prepare_common_answers(profile, job),

            # Job-specific data
            'job_id': job.id,
            'job_url': job.application_url,
            'job_title': job.title,
            'company': job.company,

            # Status
            'status': 'prepared',
            'prepared_at': None,
        }

        # Increment usage counter if AI was used
        if use_ai_cover_letter and self.openai_client and prepared_data['cover_letter'] != '':
            profile.cover_letters_generated += 1
            print(f"User {profile.user_id} used {profile.cover_letters_generated}/{profile.cover_letter_limit} cover letters this month")

        # Create draft application (not submitted yet)
        draft_application = JobApplication(
            user_id=profile.user_id,
            profile_id=profile.id,
            job_id=job.id,
            cover_letter=prepared_data['cover_letter'],
            status='prepared',  # Special status for pre-filled applications
            notes=json.dumps(prepared_data['answers']),  # Store prepared answers
        )

        db.add(draft_application)
        await db.commit()

        return prepared_data

    def _prepare_personal_info(self, profile: UserProfile) -> Dict:
        """Extract personal info for form filling."""
        # Get user's basic info
        education = profile.education[0] if profile.education else {}
        experience = profile.experience[0] if profile.experience else {}

        return {
            'email': profile.user.email,
            'phone': profile.phone,
            'linkedin': profile.linkedin_url,
            'github': profile.github_url,
            'portfolio': profile.portfolio_url,

            # Education (most recent)
            'school': education.get('school'),
            'degree': education.get('degree'),
            'major': education.get('major'),
            'gpa': education.get('gpa'),
            'graduation_year': education.get('graduation_year'),

            # Experience (most recent)
            'current_company': experience.get('company'),
            'current_title': experience.get('title'),

            # Work authorization
            'work_authorization': profile.work_authorization,
            'requires_sponsorship': profile.requires_sponsorship,

            # Location
            'location': profile.desired_locations[0] if profile.desired_locations else None,
        }

    async def _generate_cover_letter(self, profile: UserProfile, job: JobListing, use_ai: bool = True) -> str:
        """Generate AI-powered cover letter."""
        if not self.openai_client or not use_ai:
            return self._generate_template_cover_letter(profile, job)

        try:
            prompt = f"""Write a professional, enthusiastic cover letter for this job application.

Candidate Profile:
- Skills: {', '.join(profile.skills[:10])}
- Education: {profile.education[0]['school'] if profile.education else 'Current student'}
- Experience: {profile.experience[0]['title'] if profile.experience else 'Entry level'}

Job:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Description: {job.description[:500] if job.description else 'N/A'}

Instructions:
- Be concise (3 short paragraphs)
- Show genuine enthusiasm
- Highlight relevant skills
- No generic phrases
- Professional but conversational tone
- End with call to action

Cover Letter:"""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional career coach writing cover letters for students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating AI cover letter: {e}")
            return self._generate_template_cover_letter(profile, job)

    def _generate_template_cover_letter(self, profile: UserProfile, job: JobListing) -> str:
        """Fallback template cover letter."""
        education = profile.education[0] if profile.education else {}
        top_skills = ', '.join(profile.skills[:5]) if profile.skills else 'relevant skills'

        return f"""Dear Hiring Manager,

I am excited to apply for the {job.title} position at {job.company}. As a student at {education.get('school', 'my university')} with experience in {top_skills}, I am confident I would be a great addition to your team.

Through my coursework and projects, I have developed strong skills in {top_skills}. I am particularly drawn to {job.company} because of your innovative work and commitment to excellence. I am eager to contribute my skills and learn from your experienced team.

I would welcome the opportunity to discuss how my background and enthusiasm would benefit {job.company}. Thank you for considering my application.

Best regards,
{profile.user.full_name or profile.user.email}"""

    async def _prepare_common_answers(self, profile: UserProfile, job: JobListing) -> Dict[str, str]:
        """Prepare answers to common application questions."""
        answers = {}

        # Why this company?
        answers['why_company'] = await self._generate_why_company(job)

        # Why this role?
        answers['why_role'] = f"I'm interested in the {job.title} role because it aligns with my skills in {', '.join(profile.skills[:3])} and my career goals in {profile.desired_roles[0] if profile.desired_roles else 'technology'}."

        # Salary expectations
        if profile.min_salary:
            answers['salary_expectation'] = f"${profile.min_salary:,} - ${profile.max_salary:,}" if profile.max_salary else f"${profile.min_salary:,}+"

        # Availability
        answers['start_date'] = "Immediately" if profile.job_type == 'full-time' else "As per internship schedule"

        # Work authorization
        answers['work_authorization'] = profile.work_authorization or "Authorized to work in the US"
        answers['sponsorship'] = "Yes" if profile.requires_sponsorship else "No"

        # Location preference
        answers['location_preference'] = profile.desired_locations[0] if profile.desired_locations else "Flexible"

        # Remote preference
        if 'remote' in [loc.lower() for loc in profile.desired_locations]:
            answers['remote_preference'] = "Yes, I prefer remote work"
        else:
            answers['remote_preference'] = "Open to both remote and on-site"

        return answers

    async def _generate_why_company(self, job: JobListing) -> str:
        """Generate "Why this company?" answer."""
        if not self.openai_client:
            return f"I admire {job.company}'s innovative work and would love to contribute to the team."

        try:
            prompt = f"""Write a concise (2 sentences) answer to "Why do you want to work at {job.company}?"

Context:
- Company: {job.company}
- Role: {job.title}
- Description: {job.description[:300] if job.description else 'N/A'}

Make it genuine and specific. Show you've researched the company."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )

            return response.choices[0].message.content.strip()

        except:
            return f"I'm impressed by {job.company}'s work in {job.title.split()[0].lower()} and excited to contribute to your innovative projects."

    async def _check_and_reset_usage(self, profile: UserProfile, db: AsyncSession):
        """Check if usage needs to be reset (monthly reset)."""
        from datetime import datetime, timedelta

        if not profile.usage_reset_date:
            # First time, set reset date
            profile.usage_reset_date = datetime.utcnow()
            profile.cover_letters_generated = 0
            return

        # Check if 30 days have passed since last reset
        days_since_reset = (datetime.utcnow() - profile.usage_reset_date).days

        if days_since_reset >= 30:
            # Reset usage
            profile.cover_letters_generated = 0
            profile.usage_reset_date = datetime.utcnow()
            print(f"Reset usage for user {profile.user_id}")
            await db.commit()


# Helper function for API endpoints
async def get_prepared_applications(user_id: int, db: AsyncSession) -> list:
    """
    Get all prepared applications ready for submission.

    Returns list of applications with status='prepared'
    """
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.user_id == user_id,
            JobApplication.status == 'prepared'
        ).order_by(JobApplication.created_at.desc())
    )

    return result.scalars().all()
