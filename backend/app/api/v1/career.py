"""
Career and job search endpoints - Assisted Apply system.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.career import UserProfile, JobListing, JobMatch, JobApplication, CoverLetterTemplate
from app.services.resume_parser import parse_resume_from_bytes
from app.services.job_scraper import scrape_jobs_for_user
from app.services.job_matcher import JobMatcher, create_matches_for_user

router = APIRouter()


# ==================== Pydantic Schemas ====================

class ProfileCreate(BaseModel):
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None


class ProfilePreferences(BaseModel):
    desired_roles: List[str]
    desired_locations: List[str]
    desired_companies: List[str] | None = None
    min_salary: int | None = None
    max_salary: int | None = None
    job_type: str = "internship"  # internship, full-time, part-time
    work_authorization: str | None = None
    requires_sponsorship: bool = False


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    skills: List[str]
    education: List[dict]
    experience: List[dict]
    desired_roles: List[str]
    desired_locations: List[str]
    job_type: str

    class Config:
        from_attributes = True


class JobListingResponse(BaseModel):
    id: int
    external_id: str
    source: str
    title: str
    company: str
    location: str
    salary_min: int | None
    salary_max: int | None
    job_type: str
    application_url: str
    posted_date: datetime | None
    scraped_at: datetime

    class Config:
        from_attributes = True


class JobMatchResponse(BaseModel):
    id: int
    job: JobListingResponse
    match_score: float
    match_reasons: List[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: str | None = None
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    interview_date: datetime | None = None
    offer_amount: int | None = None


class ApplicationResponse(BaseModel):
    id: int
    job: JobListingResponse
    status: str
    application_date: datetime
    cover_letter: str | None
    notes: str | None
    status_history: List[dict]

    class Config:
        from_attributes = True


# ==================== Profile Endpoints ====================

@router.post("/profile/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload resume PDF and auto-extract information.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file
    pdf_content = await file.read()

    # Parse resume
    parsed = parse_resume_from_bytes(pdf_content)

    # Get or create profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update profile with parsed data
    profile.resume_text = parsed['text']
    profile.skills = parsed['skills']
    profile.education = parsed['education']
    profile.experience = parsed['experience']

    # Extract contact info
    links = parsed.get('links', {})
    profile.linkedin_url = links.get('linkedin')
    profile.github_url = links.get('github')
    profile.portfolio_url = links.get('portfolio')
    profile.phone = parsed.get('phone')

    # TODO: Upload PDF to storage (S3, etc.) and store URL
    # profile.resume_pdf_url = uploaded_url

    await db.commit()
    await db.refresh(profile)

    return {
        "message": "Resume uploaded successfully",
        "profile": profile,
        "extracted": {
            "skills": parsed['skills'],
            "education": parsed['education'],
            "experience": parsed['experience']
        }
    }


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's career profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Upload resume first.")

    return profile


@router.post("/profile/preferences")
async def set_preferences(
    preferences: ProfilePreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set job search preferences."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update preferences
    profile.desired_roles = preferences.desired_roles
    profile.desired_locations = preferences.desired_locations
    profile.desired_companies = preferences.desired_companies or []
    profile.min_salary = preferences.min_salary
    profile.max_salary = preferences.max_salary
    profile.job_type = preferences.job_type
    profile.work_authorization = preferences.work_authorization
    profile.requires_sponsorship = preferences.requires_sponsorship

    await db.commit()

    return {"message": "Preferences updated successfully"}


# ==================== Job Search & Matching ====================

@router.post("/jobs/search")
async def search_jobs(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for jobs based on user preferences.
    This runs in the background and returns immediately.
    """
    # Get user profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile or not profile.desired_roles:
        raise HTTPException(
            status_code=400,
            detail="Please set your job preferences first"
        )

    # Start background job search
    background_tasks.add_task(
        run_job_search,
        profile=profile,
        db=db
    )

    return {
        "message": "Job search started! We'll notify you when matches are found.",
        "searching_for": {
            "roles": profile.desired_roles,
            "locations": profile.desired_locations,
            "job_type": profile.job_type
        }
    }


async def run_job_search(profile: UserProfile, db: AsyncSession):
    """Background task to scrape and match jobs."""
    try:
        # Scrape jobs
        jobs_data = await scrape_jobs_for_user(
            keywords=profile.desired_roles,
            locations=profile.desired_locations,
            job_type=profile.job_type,
            max_per_search=10
        )

        # Save jobs to database
        job_ids = []
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

        await db.commit()

        # Create matches
        await create_matches_for_user(profile.user_id, job_ids, db)

        # TODO: Send notification to user
        print(f"Found {len(job_ids)} new jobs for user {profile.user_id}")

    except Exception as e:
        print(f"Error in job search: {e}")


@router.get("/jobs/matches", response_model=List[JobMatchResponse])
async def get_matches(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get job matches for user.
    """
    query = select(JobMatch).where(JobMatch.user_id == current_user.id)

    if status:
        query = query.where(JobMatch.status == status)

    query = query.order_by(desc(JobMatch.match_score)).limit(limit)

    result = await db.execute(query)
    matches = result.scalars().all()

    # Load job details
    response = []
    for match in matches:
        job_result = await db.execute(
            select(JobListing).where(JobListing.id == match.job_id)
        )
        job = job_result.scalar_one()

        response.append(JobMatchResponse(
            id=match.id,
            job=JobListingResponse.from_orm(job),
            match_score=match.match_score,
            match_reasons=match.match_reasons,
            status=match.status,
            created_at=match.created_at
        ))

    return response


@router.patch("/jobs/matches/{match_id}/status")
async def update_match_status(
    match_id: int,
    status: str,  # viewed, saved, dismissed
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update match status (mark as viewed, saved, etc.)."""
    result = await db.execute(
        select(JobMatch).where(
            and_(
                JobMatch.id == match_id,
                JobMatch.user_id == current_user.id
            )
        )
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.status = status
    if status == "viewed":
        match.viewed_at = datetime.utcnow()

    await db.commit()

    return {"message": f"Match marked as {status}"}


# ==================== Applications ====================

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a job application.
    User applies manually via job board, then records it here for tracking.
    """
    # Get user profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    # Get job
    job = await db.get(JobListing, application_data.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Create application
    application = JobApplication(
        user_id=current_user.id,
        profile_id=profile.id,
        job_id=application_data.job_id,
        cover_letter=application_data.cover_letter,
        notes=application_data.notes,
        status="submitted",
        status_history=[{
            "status": "submitted",
            "date": datetime.utcnow().isoformat(),
            "notes": "Application submitted"
        }],
        applied_via="mobile_app"
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    # Update match status if exists
    result = await db.execute(
        select(JobMatch).where(
            and_(
                JobMatch.user_id == current_user.id,
                JobMatch.job_id == application_data.job_id
            )
        )
    )
    match = result.scalar_one_or_none()
    if match:
        match.status = "applied"
        await db.commit()

    return ApplicationResponse(
        id=application.id,
        job=JobListingResponse.from_orm(job),
        status=application.status,
        application_date=application.application_date,
        cover_letter=application.cover_letter,
        notes=application.notes,
        status_history=application.status_history
    )


@router.get("/applications", response_model=List[ApplicationResponse])
async def list_applications(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all job applications."""
    query = select(JobApplication).where(JobApplication.user_id == current_user.id)

    if status:
        query = query.where(JobApplication.status == status)

    query = query.order_by(desc(JobApplication.application_date))

    result = await db.execute(query)
    applications = result.scalars().all()

    # Load job details
    response = []
    for app in applications:
        job = await db.get(JobListing, app.job_id)
        response.append(ApplicationResponse(
            id=app.id,
            job=JobListingResponse.from_orm(job),
            status=app.status,
            application_date=app.application_date,
            cover_letter=app.cover_letter,
            notes=app.notes,
            status_history=app.status_history
        ))

    return response


@router.patch("/applications/{application_id}")
async def update_application(
    application_id: int,
    update_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update application status (e.g., interviewing, rejected, offer)."""
    application = await db.get(JobApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update status
    if update_data.status:
        application.status = update_data.status

        # Add to history
        history = application.status_history or []
        history.append({
            "status": update_data.status,
            "date": datetime.utcnow().isoformat(),
            "notes": update_data.notes or ""
        })
        application.status_history = history

    # Update other fields
    if update_data.notes:
        application.notes = update_data.notes
    if update_data.interview_date:
        application.next_interview_date = update_data.interview_date
    if update_data.offer_amount:
        application.offer_amount = update_data.offer_amount

    await db.commit()

    return {"message": "Application updated"}


@router.get("/applications/stats")
async def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get application statistics."""
    result = await db.execute(
        select(JobApplication).where(JobApplication.user_id == current_user.id)
    )
    applications = result.scalars().all()

    # Count by status
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    return {
        "total": len(applications),
        "by_status": status_counts,
        "recent_applications": len([a for a in applications if (datetime.utcnow() - a.application_date).days <= 7])
    }


# ==================== Cover Letter Generation ====================

@router.post("/cover-letter/generate")
async def generate_cover_letter(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI cover letter for a specific job.
    TODO: Integrate with OpenAI/Anthropic API.
    """
    # Get user profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    # Get job
    job = await db.get(JobListing, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # TODO: Call AI service to generate cover letter
    # For now, return template
    cover_letter = f"""Dear Hiring Manager,

I am writing to express my interest in the {job.title} position at {job.company}. As a student with experience in {', '.join(profile.skills[:3])}, I am excited about the opportunity to contribute to your team.

Through my education at {profile.education[0]['school'] if profile.education else 'my university'}, I have developed strong skills in {', '.join(profile.skills[:5])}. I am particularly drawn to this role because it aligns with my career goals in {profile.desired_roles[0] if profile.desired_roles else 'technology'}.

I would welcome the opportunity to discuss how my background and skills would be a great fit for {job.company}.

Thank you for your consideration.

Best regards,
{current_user.full_name or current_user.email}
"""

    return {"cover_letter": cover_letter}


# ==================== Auto-Prep Queue ====================

@router.get("/queue/ready")
async def get_ready_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get applications that are ready to submit.
    These have been automatically prepared by background jobs.
    """
    from app.services.application_preparer import get_prepared_applications

    prepared_apps = await get_prepared_applications(current_user.id, db)

    # Load job details for each
    response = []
    for app in prepared_apps:
        job = await db.get(JobListing, app.job_id)
        response.append({
            "id": app.id,
            "job": JobListingResponse.from_orm(job),
            "cover_letter": app.cover_letter,
            "prepared_answers": app.notes,  # JSON string with all answers
            "created_at": app.created_at,
            "status": "ready_to_submit"
        })

    return response


@router.post("/queue/{application_id}/approve")
async def approve_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a prepared application and mark as submitted.
    User has reviewed and clicked "Submit" in the app.
    """
    application = await db.get(JobApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status != "prepared":
        raise HTTPException(status_code=400, detail="Application not in prepared state")

    # Mark as submitted
    application.status = "submitted"
    application.application_date = datetime.utcnow()

    # Add to history
    history = application.status_history or []
    history.append({
        "status": "submitted",
        "date": datetime.utcnow().isoformat(),
        "notes": "Approved and submitted via mobile app"
    })
    application.status_history = history

    # Update match status
    result = await db.execute(
        select(JobMatch).where(
            and_(
                JobMatch.user_id == current_user.id,
                JobMatch.job_id == application.job_id
            )
        )
    )
    match = result.scalar_one_or_none()
    if match:
        match.status = "applied"

    await db.commit()

    return {
        "message": "Application submitted successfully!",
        "application_id": application.id
    }


@router.delete("/queue/{application_id}/dismiss")
async def dismiss_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Dismiss a prepared application (don't want to apply).
    """
    application = await db.get(JobApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    # Delete the prepared application
    await db.delete(application)

    # Update match status to dismissed
    result = await db.execute(
        select(JobMatch).where(
            and_(
                JobMatch.user_id == current_user.id,
                JobMatch.job_id == application.job_id
            )
        )
    )
    match = result.scalar_one_or_none()
    if match:
        match.status = "dismissed"

    await db.commit()

    return {"message": "Application dismissed"}
