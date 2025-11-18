#!/usr/bin/env python3
"""
Seed test data for development and testing.
Creates sample users, jobs, and applications.

Usage:
    python seed_test_data.py
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.user import User
from app.models.career import UserProfile, JobListing, JobMatch, JobApplication
from app.core.security import get_password_hash


async def seed_test_data():
    """Seed database with test data."""
    print("🌱 Seeding test data...\n")

    async with async_session_maker() as db:
        # Create test user
        print("Creating test user...")
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpass123"),
            full_name="Test User",
            is_active=True
        )
        db.add(test_user)
        await db.flush()
        print(f"✓ Created user: {test_user.email} (password: testpass123)")

        # Create user profile
        print("\nCreating user profile...")
        profile = UserProfile(
            user_id=test_user.id,
            resume_text="Sample resume text for testing",
            skills=["Python", "JavaScript", "React", "SQL", "Machine Learning"],
            education=[{
                "school": "Test University",
                "degree": "Bachelor of Science",
                "major": "Computer Science",
                "gpa": 3.8,
                "graduation_year": 2025
            }],
            experience=[{
                "company": "Tech Startup Inc",
                "title": "Software Engineering Intern",
                "duration": "Summer 2024",
                "description": "Built web applications"
            }],
            phone="555-0123",
            linkedin_url="https://linkedin.com/in/testuser",
            github_url="https://github.com/testuser",
            desired_roles=["Software Engineer Intern", "Data Analyst Intern"],
            desired_locations=["Remote", "New York", "San Francisco"],
            desired_companies=["Google", "Microsoft", "Startup"],
            min_salary=60000,
            max_salary=100000,
            job_type="internship",
            work_authorization="US Citizen",
            requires_sponsorship=False,
            cover_letters_generated=0,
            cover_letter_limit=10
        )
        db.add(profile)
        print("✓ Created profile with skills and preferences")

        # Create sample job listings
        print("\nCreating sample jobs...")
        jobs = [
            JobListing(
                external_id="linkedin_123456",
                source="linkedin",
                title="Software Engineer Intern",
                company="Google",
                location="Mountain View, CA (Remote)",
                remote_type="remote",
                salary_min=75000,
                salary_max=95000,
                job_type="internship",
                description="Build innovative products used by millions...",
                requirements="Python, JavaScript, strong CS fundamentals",
                application_method="easy_apply",
                application_url="https://careers.google.com/jobs/123456",
                required_skills=["Python", "JavaScript", "SQL"],
                posted_date=datetime.utcnow() - timedelta(days=2)
            ),
            JobListing(
                external_id="indeed_789012",
                source="indeed",
                title="Data Analyst Intern",
                company="Microsoft",
                location="Seattle, WA",
                remote_type="hybrid",
                salary_min=70000,
                salary_max=85000,
                job_type="internship",
                description="Analyze data to drive business decisions...",
                requirements="Python, SQL, Excel, statistics",
                application_method="external",
                application_url="https://careers.microsoft.com/jobs/789012",
                required_skills=["Python", "SQL", "Excel"],
                posted_date=datetime.utcnow() - timedelta(days=1)
            ),
            JobListing(
                external_id="linkedin_345678",
                source="linkedin",
                title="Frontend Developer Intern",
                company="Startup XYZ",
                location="New York, NY (Remote)",
                remote_type="remote",
                salary_min=60000,
                salary_max=75000,
                job_type="internship",
                description="Build beautiful user interfaces...",
                requirements="React, JavaScript, CSS",
                application_method="easy_apply",
                application_url="https://startupxyz.com/careers",
                required_skills=["React", "JavaScript", "CSS"],
                posted_date=datetime.utcnow() - timedelta(hours=12)
            )
        ]

        for job in jobs:
            db.add(job)
        await db.flush()
        print(f"✓ Created {len(jobs)} sample jobs")

        # Create job matches
        print("\nCreating job matches...")
        for i, job in enumerate(jobs):
            match = JobMatch(
                user_id=test_user.id,
                job_id=job.id,
                match_score=0.85 - (i * 0.05),  # 85%, 80%, 75%
                match_reasons=[
                    f"Strong skills match: {', '.join(job.required_skills[:2])}",
                    f"Location preference: {job.location}",
                    "Salary matches expectations"
                ],
                status="new"
            )
            db.add(match)
        print(f"✓ Created {len(jobs)} job matches")

        # Create one prepared application
        print("\nCreating prepared application...")
        prepared_app = JobApplication(
            user_id=test_user.id,
            profile_id=profile.id,
            job_id=jobs[0].id,
            status="prepared",
            cover_letter="""Dear Hiring Manager,

I am excited to apply for the Software Engineer Intern position at Google. As a Computer Science student at Test University with experience in Python, JavaScript, and React, I am confident I would be a great addition to your team.

Through my coursework and internship at Tech Startup Inc, I have developed strong skills in Python, JavaScript, React, SQL, Machine Learning. I am particularly drawn to Google because of your innovative work and commitment to excellence. I am eager to contribute my skills and learn from your experienced team.

I would welcome the opportunity to discuss how my background and enthusiasm would benefit Google. Thank you for considering my application.

Best regards,
Test User""",
            notes='{"why_company": "Admire innovative work", "salary_expectation": "$60,000 - $100,000"}',
            status_history=[{
                "status": "prepared",
                "date": datetime.utcnow().isoformat(),
                "notes": "Auto-prepared by system"
            }]
        )
        db.add(prepared_app)
        print("✓ Created prepared application (ready to submit)")

        await db.commit()

        print("\n" + "="*60)
        print("✅ Test data seeded successfully!")
        print("="*60)
        print("\nYou can now:")
        print("1. Login with: test@example.com / testpass123")
        print("2. See 3 job matches in Career Hub")
        print("3. See 1 ready-to-submit application")
        print("\nAPI endpoints to test:")
        print("  POST /api/v1/auth/login")
        print("  GET  /api/v1/career/profile")
        print("  GET  /api/v1/career/jobs/matches")
        print("  GET  /api/v1/career/queue/ready")
        print("")


if __name__ == "__main__":
    asyncio.run(seed_test_data())
