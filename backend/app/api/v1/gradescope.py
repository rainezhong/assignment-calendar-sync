"""
Gradescope integration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.credential import Credential
from app.models.course import Course
from app.models.assignment import Assignment
from app.models.scrape_job import ScrapeJob
from app.models.task import Task
from app.services.gradescope_service import GradescopeService
from app.services.encryption_service import encryption_service
from app.services.task_generation_service import TaskGenerationService

router = APIRouter()


# Pydantic schemas
class GradescopeConnectRequest(BaseModel):
    email: str
    password: str


class GradescopeConnectionResponse(BaseModel):
    status: str
    message: str


class GradescopeStatus(BaseModel):
    connected: bool
    email: Optional[str] = None
    last_synced: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    last_error: Optional[str] = None
    courses_count: Optional[int] = None
    assignments_count: Optional[int] = None


class SyncGradescopeResponse(BaseModel):
    status: str
    message: str
    courses_found: int
    courses_new: int
    assignments_found: int
    assignments_new: int


@router.post("/connect", response_model=GradescopeConnectionResponse)
async def connect_gradescope(
    request: GradescopeConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Connect Gradescope account by storing encrypted credentials.
    """
    # Test connection first
    try:
        async with GradescopeService(request.email, request.password) as gradescope:
            await gradescope.initialize()
            is_valid = await gradescope.test_connection()

            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Gradescope credentials. Please check your email and password.",
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to Gradescope: {str(e)}",
        )

    # Encrypt credentials
    credentials_data = {
        "email": request.email,
        "password": request.password,
    }
    encrypted_data = encryption_service.encrypt_credentials(credentials_data)

    # Check if credential already exists
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id,
            Credential.service == "gradescope"
        )
    )
    existing_credential = result.scalar_one_or_none()

    if existing_credential:
        # Update existing
        existing_credential.encrypted_data = encrypted_data
        existing_credential.institution_url = GradescopeService.BASE_URL
        existing_credential.is_active = True
        existing_credential.last_error = None
    else:
        # Create new
        credential = Credential(
            user_id=current_user.id,
            service="gradescope",
            encrypted_data=encrypted_data,
            institution_url=GradescopeService.BASE_URL,
            is_active=True,
        )
        db.add(credential)

    await db.commit()

    return GradescopeConnectionResponse(
        status="success",
        message="Gradescope account connected successfully",
    )


@router.post("/disconnect")
async def disconnect_gradescope(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disconnect Gradescope account (delete credentials).
    """
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id,
            Credential.service == "gradescope"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gradescope account not connected",
        )

    await db.delete(credential)
    await db.commit()

    return {"status": "success", "message": "Gradescope account disconnected"}


@router.get("/status", response_model=GradescopeStatus)
async def get_gradescope_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check Gradescope connection status.
    """
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id,
            Credential.service == "gradescope"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        return GradescopeStatus(connected=False)

    # Decrypt to get email
    try:
        creds = encryption_service.decrypt_credentials(credential.encrypted_data)
        email = creds.get('email')
    except Exception:
        email = None

    # Count courses and assignments
    result = await db.execute(
        select(Course).where(
            Course.user_id == current_user.id,
            Course.source == "gradescope"
        )
    )
    courses = result.scalars().all()
    courses_count = len(courses)

    result = await db.execute(
        select(Assignment).where(
            Assignment.user_id == current_user.id,
            Assignment.source == "gradescope"
        )
    )
    assignments = result.scalars().all()
    assignments_count = len(assignments)

    return GradescopeStatus(
        connected=True,
        email=email,
        last_synced=credential.last_synced,
        last_sync_status=credential.last_sync_status,
        last_error=credential.last_error,
        courses_count=courses_count,
        assignments_count=assignments_count,
    )


@router.post("/sync", response_model=SyncGradescopeResponse)
async def sync_gradescope(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync courses and assignments from Gradescope.
    """
    # Get Gradescope credentials
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id,
            Credential.service == "gradescope"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gradescope not connected. Please connect Gradescope first.",
        )

    # Create scrape job
    scrape_job = ScrapeJob(
        user_id=current_user.id,
        credential_id=credential.id,
        service="gradescope",
        job_type="full_sync",
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(scrape_job)
    await db.commit()
    await db.refresh(scrape_job)

    try:
        # Decrypt credentials
        creds = encryption_service.decrypt_credentials(credential.encrypted_data)

        # Initialize Gradescope service
        async with GradescopeService(creds["email"], creds["password"]) as gradescope:
            await gradescope.initialize()

            # Login
            login_success = await gradescope.login()
            if not login_success:
                raise Exception("Failed to login to Gradescope")

            # Scrape all data
            data = await gradescope.scrape_all_data()

            courses_new = 0
            courses_found = len(data['courses'])

            # Map to store gradescope_id -> database course_id
            course_id_map = {}

            # Process courses
            for gradescope_course in data['courses']:
                gradescope_course_id = gradescope_course['course_id']

                # Check if course already exists
                result = await db.execute(
                    select(Course).where(
                        Course.user_id == current_user.id,
                        Course.source == "gradescope",
                        Course.source_id == gradescope_course_id,
                    )
                )
                existing_course = result.scalar_one_or_none()

                if existing_course:
                    # Update existing course
                    course_data = gradescope.parse_course(gradescope_course)
                    for key, value in course_data.items():
                        if key not in ["source", "source_id"]:
                            setattr(existing_course, key, value)
                    existing_course.last_synced = datetime.utcnow()
                    course_id_map[gradescope_course_id] = existing_course.id
                else:
                    # Create new course
                    course_data = gradescope.parse_course(gradescope_course)
                    course_data["user_id"] = current_user.id
                    course_data["course_name"] = course_data["name"]
                    new_course = Course(**course_data)
                    db.add(new_course)
                    await db.flush()
                    course_id_map[gradescope_course_id] = new_course.id
                    courses_new += 1

            await db.commit()

            # Process assignments
            assignments_new = 0
            assignments_found = 0

            for gradescope_course_id, assignments in data['assignments'].items():
                if gradescope_course_id not in course_id_map:
                    continue

                db_course_id = course_id_map[gradescope_course_id]

                # Get course name
                result = await db.execute(
                    select(Course).where(Course.id == db_course_id)
                )
                course = result.scalar_one()

                for gradescope_assignment in assignments:
                    assignments_found += 1
                    gradescope_assignment_id = gradescope_assignment.get('assignment_id')

                    if not gradescope_assignment_id:
                        continue

                    # Check if assignment exists
                    result = await db.execute(
                        select(Assignment).where(
                            Assignment.user_id == current_user.id,
                            Assignment.source == "gradescope",
                            Assignment.source_id == gradescope_assignment_id,
                        )
                    )
                    existing_assignment = result.scalar_one_or_none()

                    assignment_data = gradescope.parse_assignment(
                        gradescope_assignment, db_course_id
                    )
                    assignment_data["user_id"] = current_user.id
                    assignment_data["course_name"] = course.name

                    if existing_assignment:
                        # Update existing
                        for key, value in assignment_data.items():
                            if key not in ["source", "source_id", "user_id"]:
                                setattr(existing_assignment, key, value)
                    else:
                        # Create new
                        new_assignment = Assignment(**assignment_data)
                        db.add(new_assignment)
                        assignments_new += 1

            await db.commit()

            # Auto-generate tasks for new assignments
            if assignments_new > 0:
                task_service = TaskGenerationService()
                result = await db.execute(
                    select(Assignment).where(
                        Assignment.user_id == current_user.id,
                        Assignment.tasks_generated == False
                    )
                )
                assignments_without_tasks = result.scalars().all()

                for assignment in assignments_without_tasks:
                    try:
                        # Generate tasks
                        tasks = await task_service.generate_tasks_for_assignment(assignment)
                        for task in tasks:
                            db.add(task)

                        # Mark as generated
                        assignment.tasks_generated = True
                        assignment.tasks_generated_at = datetime.utcnow()

                    except Exception as e:
                        # Don't fail sync if task generation fails
                        print(f"Failed to generate tasks for assignment {assignment.id}: {e}")
                        continue

                await db.commit()

            # Update scrape job
            scrape_job.status = "completed"
            scrape_job.completed_at = datetime.utcnow()
            scrape_job.items_found = courses_found + assignments_found
            scrape_job.items_new = courses_new + assignments_new
            scrape_job.results_summary = {
                "courses": courses_found,
                "assignments": assignments_found,
            }

            # Update credential
            credential.last_synced = datetime.utcnow()
            credential.last_sync_status = "success"
            credential.sync_count = (credential.sync_count or 0) + 1

            await db.commit()

            return SyncGradescopeResponse(
                status="success",
                message=f"Successfully synced {courses_found} courses and {assignments_found} assignments",
                courses_found=courses_found,
                courses_new=courses_new,
                assignments_found=assignments_found,
                assignments_new=assignments_new,
            )

    except Exception as e:
        # Update scrape job with error
        scrape_job.status = "failed"
        scrape_job.completed_at = datetime.utcnow()
        scrape_job.error_message = str(e)

        credential.last_sync_status = "failed"
        credential.last_error = str(e)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync Gradescope data: {str(e)}",
        )
