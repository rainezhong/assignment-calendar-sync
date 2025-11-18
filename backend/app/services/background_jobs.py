"""
Background job scheduler for automated job search and application preparation.
Runs daily to scrape jobs, match, and prepare applications.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import asyncio
from typing import List

from app.models.career import UserProfile, JobListing, JobMatch, JobApplication
from app.models.user import User
from app.services.job_scraper import scrape_jobs_for_user
from app.services.job_matcher import JobMatcher, create_matches_for_user
from app.services.application_preparer import ApplicationPreparer
from app.db.session import AsyncSessionLocal


class BackgroundJobScheduler:
    """Manages background jobs for automated job search."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """Start the background scheduler."""
        if self.is_running:
            return

        # Daily job search at 8 AM
        self.scheduler.add_job(
            self.daily_job_search,
            CronTrigger(hour=8, minute=0),
            id='daily_job_search',
            name='Daily Job Search',
            replace_existing=True
        )

        # Prepare applications every 2 hours (9 AM - 9 PM)
        self.scheduler.add_job(
            self.prepare_pending_applications,
            CronTrigger(hour='9-21/2', minute=0),
            id='prepare_applications',
            name='Prepare Applications',
            replace_existing=True
        )

        # Check for application updates (responses) every 4 hours
        self.scheduler.add_job(
            self.check_application_status,
            CronTrigger(hour='*/4', minute=0),
            id='check_status',
            name='Check Application Status',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        print("✅ Background job scheduler started!")

    def stop(self):
        """Stop the background scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("❌ Background job scheduler stopped")

    async def daily_job_search(self):
        """
        Daily job: Search for new jobs for all active users.
        Runs at 8 AM every day.
        """
        print(f"🔍 [Daily Job Search] Starting at {datetime.now()}")

        async with AsyncSessionLocal() as db:
            # Get all users with active profiles
            result = await db.execute(
                select(UserProfile).where(
                    and_(
                        UserProfile.email_notifications == True,
                        UserProfile.desired_roles.isnot(None)
                    )
                )
            )
            profiles = result.scalars().all()

            print(f"📊 Found {len(profiles)} active users")

            for profile in profiles:
                try:
                    await self._search_jobs_for_user(profile, db)
                except Exception as e:
                    print(f"❌ Error searching jobs for user {profile.user_id}: {e}")

        print(f"✅ [Daily Job Search] Completed at {datetime.now()}")

    async def _search_jobs_for_user(self, profile: UserProfile, db: AsyncSession):
        """Search and match jobs for a single user."""
        print(f"🔎 Searching jobs for user {profile.user_id}")

        # Scrape jobs
        jobs_data = await scrape_jobs_for_user(
            keywords=profile.desired_roles,
            locations=profile.desired_locations,
            job_type=profile.job_type,
            max_per_search=profile.daily_match_limit or 10
        )

        if not jobs_data:
            print(f"   No new jobs found")
            return

        # Save jobs to database
        job_ids = []
        new_count = 0

        for job_data in jobs_data:
            # Check if job already exists
            result = await db.execute(
                select(JobListing).where(JobListing.external_id == job_data['external_id'])
            )
            existing = result.scalar_one_or_none()

            if existing:
                job_ids.append(existing.id)
                continue

            # Create new job listing
            job = JobListing(**job_data)
            db.add(job)
            await db.flush()
            job_ids.append(job.id)
            new_count += 1

        await db.commit()
        print(f"   Found {new_count} new jobs")

        # Create matches
        if job_ids:
            matches = await create_matches_for_user(profile.user_id, job_ids, db)
            high_matches = [m for m in matches if m.match_score >= 0.7]
            print(f"   Created {len(high_matches)} high-quality matches (>70%)")

            # TODO: Send notification to user
            if high_matches:
                await self._notify_user_new_matches(profile.user_id, len(high_matches))

    async def prepare_pending_applications(self):
        """
        Prepare applications for top matches.
        Runs every 2 hours during business hours.
        """
        print(f"🔧 [Prepare Applications] Starting at {datetime.now()}")

        async with AsyncSessionLocal() as db:
            # Get all high-score matches that haven't been applied to
            result = await db.execute(
                select(JobMatch).where(
                    and_(
                        JobMatch.match_score >= 0.7,  # Only top matches
                        JobMatch.status == 'new',  # Not yet processed
                    )
                ).limit(50)  # Process max 50 at a time
            )
            matches = result.scalars().all()

            print(f"📊 Found {len(matches)} matches to prepare")

            preparer = ApplicationPreparer()

            for match in matches:
                try:
                    # Get user profile
                    profile_result = await db.execute(
                        select(UserProfile).where(UserProfile.user_id == match.user_id)
                    )
                    profile = profile_result.scalar_one()

                    # Get job
                    job = await db.get(JobListing, match.job_id)

                    # Prepare application
                    prepared = await preparer.prepare_application(profile, job, db)

                    if prepared:
                        # Mark match as "ready"
                        match.status = 'ready_to_submit'
                        print(f"   ✅ Prepared application for: {job.title} at {job.company}")

                except Exception as e:
                    print(f"   ❌ Error preparing application: {e}")

            await db.commit()

        print(f"✅ [Prepare Applications] Completed at {datetime.now()}")

    async def check_application_status(self):
        """
        Check for updates on submitted applications.
        Runs every 4 hours.
        """
        print(f"📧 [Check Status] Starting at {datetime.now()}")

        async with AsyncSessionLocal() as db:
            # Get applications submitted in last 30 days, not yet responded
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            result = await db.execute(
                select(JobApplication).where(
                    and_(
                        JobApplication.status == 'submitted',
                        JobApplication.application_date >= cutoff_date
                    )
                )
            )
            applications = result.scalars().all()

            print(f"📊 Checking {len(applications)} pending applications")

            # TODO: Implement email checking or API integration
            # For now, just check if follow-up is due
            for app in applications:
                if app.next_follow_up and app.next_follow_up <= datetime.utcnow():
                    # Send reminder to user
                    await self._notify_follow_up_due(app)

        print(f"✅ [Check Status] Completed at {datetime.now()}")

    async def _notify_user_new_matches(self, user_id: int, count: int):
        """Send notification to user about new matches."""
        # TODO: Implement push notification or email
        print(f"   📬 Notify user {user_id}: {count} new job matches")

    async def _notify_follow_up_due(self, application: JobApplication):
        """Send follow-up reminder to user."""
        # TODO: Implement notification
        print(f"   📬 Follow-up reminder for: {application.job.title}")


# Global scheduler instance
scheduler = BackgroundJobScheduler()


def start_background_jobs():
    """Start background job scheduler (call on app startup)."""
    scheduler.start()


def stop_background_jobs():
    """Stop background job scheduler (call on app shutdown)."""
    scheduler.stop()
