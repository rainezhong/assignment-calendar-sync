"""
Job scraping and matching endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.job_listing import JobListing
from app.models.job_match import JobMatch
from app.services.linkedin_service import LinkedInService
from app.services.job_matching_service import JobMatchingService

router = APIRouter()


# Pydantic schemas
class ScrapeJobsRequest(BaseModel):
    search_url: str
    max_jobs: int = 25


class ScrapeJobsResponse(BaseModel):
    status: str
    message: str
    jobs_found: int
    jobs_new: int


class JobListingResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    remote_type: str
    job_type: str
    description: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    application_url: str
    source: str
    posted_date: Optional[datetime]
    skills: List[str]
    match_score: Optional[float] = None
    matched_skills: Optional[List[str]] = None

    class Config:
        from_attributes = True


class JobMatchDetailResponse(BaseModel):
    match_score: float
    skill_match_score: float
    course_relevance_score: float
    recency_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    match_reasons: List[str]


class ApplyToJobRequest(BaseModel):
    notes: Optional[str] = None


@router.post("/scrape", response_model=ScrapeJobsResponse)
async def scrape_jobs(
    request: ScrapeJobsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Scrape job listings from LinkedIn search URL.
    """
    try:
        # Validate URL
        if 'linkedin.com' not in request.search_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a valid LinkedIn jobs search URL"
            )

        # Scrape jobs
        async with LinkedInService() as linkedin:
            await linkedin.initialize()
            scraped_jobs = await linkedin.scrape_job_search(
                request.search_url,
                max_jobs=request.max_jobs
            )

        jobs_new = 0
        jobs_found = len(scraped_jobs)

        # Process each job
        for job_data in scraped_jobs:
            # Extract skills from snippet
            skills = []
            if job_data.get('snippet'):
                linkedin_service = LinkedInService()
                skills = linkedin_service.extract_skills(job_data['snippet'])

            # Infer job type and remote type
            linkedin_service = LinkedInService()
            job_type = linkedin_service.infer_job_type(
                job_data['title'],
                job_data.get('snippet')
            )
            remote_type = linkedin_service.infer_remote_type(
                job_data.get('location', ''),
                job_data.get('snippet')
            )

            # Check if job already exists (by URL or title+company)
            result = await db.execute(
                select(JobListing).where(
                    JobListing.application_url == job_data.get('job_url')
                )
            )
            existing_job = result.scalar_one_or_none()

            if not existing_job:
                # Create new job listing
                new_job = JobListing(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    remote_type=remote_type,
                    job_type=job_type,
                    description=job_data.get('snippet'),
                    application_url=job_data.get('job_url') or request.search_url,
                    source='linkedin',
                    posted_date=job_data.get('posted_date'),
                    skills=skills,
                )
                db.add(new_job)
                await db.flush()

                # Calculate match score for this user
                matching_service = JobMatchingService(current_user.id, db)
                match_data = await matching_service.calculate_match_score(new_job)

                # Create job match
                job_match = JobMatch(
                    job_id=new_job.id,
                    user_id=current_user.id,
                    match_score=match_data['match_score'],
                    skill_match_score=match_data['skill_match_score'],
                    course_relevance_score=match_data['course_relevance_score'],
                    matched_skills=match_data['matched_skills'],
                    match_reasons=match_data['match_reasons'],
                    missing_skills=match_data['missing_skills'],
                    status='saved',
                )
                db.add(job_match)

                jobs_new += 1

        await db.commit()

        return ScrapeJobsResponse(
            status="success",
            message=f"Successfully scraped {jobs_found} jobs ({jobs_new} new)",
            jobs_found=jobs_found,
            jobs_new=jobs_new,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape jobs: {str(e)}"
        )


@router.get("/", response_model=List[JobListingResponse])
async def get_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sort_by: str = Query("match_score", regex="^(match_score|posted_date|title)$"),
    job_type: Optional[str] = None,
    remote_type: Optional[str] = None,
):
    """
    Get all job listings with match scores, sorted by match score.
    """
    # Get user's job matches
    query = select(JobMatch).where(JobMatch.user_id == current_user.id)

    # Apply filters
    if job_type:
        query = query.join(JobListing).where(JobListing.job_type == job_type)
    if remote_type:
        query = query.join(JobListing).where(JobListing.remote_type == remote_type)

    # Apply sorting
    if sort_by == "match_score":
        query = query.order_by(desc(JobMatch.match_score))
    elif sort_by == "posted_date":
        query = query.join(JobListing).order_by(desc(JobListing.posted_date))
    elif sort_by == "title":
        query = query.join(JobListing).order_by(JobListing.title)

    result = await db.execute(query)
    job_matches = result.scalars().all()

    # Build response with job details and match info
    jobs_response = []
    for match in job_matches:
        # Get job listing
        result = await db.execute(
            select(JobListing).where(JobListing.id == match.job_id)
        )
        job = result.scalar_one()

        jobs_response.append(JobListingResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            remote_type=job.remote_type,
            job_type=job.job_type,
            description=job.description,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            application_url=job.application_url,
            source=job.source,
            posted_date=job.posted_date,
            skills=job.skills or [],
            match_score=match.match_score,
            matched_skills=match.matched_skills or [],
        ))

    return jobs_response


@router.get("/{job_id}", response_model=JobListingResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get single job listing details.
    """
    result = await db.execute(
        select(JobListing).where(JobListing.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Get match info if exists
    result = await db.execute(
        select(JobMatch).where(
            JobMatch.job_id == job_id,
            JobMatch.user_id == current_user.id
        )
    )
    match = result.scalar_one_or_none()

    return JobListingResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        remote_type=job.remote_type,
        job_type=job.job_type,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        application_url=job.application_url,
        source=job.source,
        posted_date=job.posted_date,
        skills=job.skills or [],
        match_score=match.match_score if match else None,
        matched_skills=match.matched_skills if match else [],
    )


@router.get("/{job_id}/match", response_model=JobMatchDetailResponse)
async def get_job_match(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed match breakdown for a job.
    """
    result = await db.execute(
        select(JobMatch).where(
            JobMatch.job_id == job_id,
            JobMatch.user_id == current_user.id
        )
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found for this job"
        )

    return JobMatchDetailResponse(
        match_score=match.match_score,
        skill_match_score=match.skill_match_score or 0,
        course_relevance_score=match.course_relevance_score or 0,
        recency_score=0,  # Not stored separately
        matched_skills=match.matched_skills or [],
        missing_skills=match.missing_skills or [],
        match_reasons=match.match_reasons or [],
    )


@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: int,
    request: ApplyToJobRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark job as applied.
    """
    result = await db.execute(
        select(JobMatch).where(
            JobMatch.job_id == job_id,
            JobMatch.user_id == current_user.id
        )
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job match not found"
        )

    # Update match status
    match.status = 'applied'
    match.applied_date = datetime.utcnow()
    if request.notes:
        match.notes = request.notes

    await db.commit()

    return {
        "status": "success",
        "message": "Job marked as applied",
        "job_id": job_id
    }


@router.put("/matches/{match_id}")
async def update_job_match(
    match_id: int,
    status: str = Query(..., regex="^(saved|applied|interviewing|offer|rejected)$"),
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update job application status.
    """
    result = await db.execute(
        select(JobMatch).where(
            JobMatch.id == match_id,
            JobMatch.user_id == current_user.id
        )
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job match not found"
        )

    match.status = status
    if notes:
        match.notes = notes

    await db.commit()

    return {
        "status": "success",
        "message": f"Status updated to {status}"
    }
