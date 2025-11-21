"""
Canvas integration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.credential import Credential
from app.models.course import Course
from app.models.assignment import Assignment
from app.models.scrape_job import ScrapeJob
from app.services.canvas_service import CanvasService
from app.services.encryption_service import encryption_service

router = APIRouter()


# Pydantic schemas
class CanvasConnectRequest(BaseModel):
    api_token: str
    base_url: str  # e.g., "umich.instructure.com" or "https://umich.instructure.com"


class CanvasConnectionResponse(BaseModel):
    status: str
    message: str
    canvas_user: Optional[dict] = None


class SyncResponse(BaseModel):
    status: str
    message: str
    courses_found: int
    courses_new: int
    assignments_found: int
    assignments_new: int


@router.post("/connect", response_model=CanvasConnectionResponse)
async def connect_canvas(
    request: CanvasConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Connect user's Canvas account by storing encrypted credentials.
    """
    # Test connection first
    canvas_service = CanvasService(request.api_token, request.base_url)

    is_valid = await canvas_service.test_connection()
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Canvas credentials or URL. Please check your API token and institution URL.",
        )

    # Get Canvas user info
    canvas_user = await canvas_service.get_current_user()

    # Encrypt credentials
    credentials_data = {
        "api_token": request.api_token,
        "base_url": canvas_service.base_url,  # Normalized URL
    }
    encrypted_data = encryption_service.encrypt_credentials(credentials_data)

    # Check if credential already exists
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id, Credential.service == "canvas"
        )
    )
    existing_credential = result.scalar_one_or_none()

    if existing_credential:
        # Update existing
        existing_credential.encrypted_data = encrypted_data
        existing_credential.institution_url = canvas_service.base_url
        existing_credential.is_active = True
        existing_credential.last_error = None
    else:
        # Create new
        credential = Credential(
            user_id=current_user.id,
            service="canvas",
            encrypted_data=encrypted_data,
            institution_url=canvas_service.base_url,
            is_active=True,
        )
        db.add(credential)

    await db.commit()

    return CanvasConnectionResponse(
        status="success",
        message="Canvas account connected successfully",
        canvas_user=canvas_user,
    )


@router.post("/disconnect")
async def disconnect_canvas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disconnect Canvas account (delete credentials).
    """
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id, Credential.service == "canvas"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas account not connected",
        )

    await db.delete(credential)
    await db.commit()

    return {"status": "success", "message": "Canvas account disconnected"}


@router.get("/status")
async def get_canvas_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if Canvas is connected and get connection status.
    """
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id, Credential.service == "canvas"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        return {
            "connected": False,
            "message": "Canvas not connected",
        }

    return {
        "connected": True,
        "institution_url": credential.institution_url,
        "last_synced": credential.last_synced,
        "last_sync_status": credential.last_sync_status,
        "last_error": credential.last_error,
    }


@router.post("/sync", response_model=SyncResponse)
async def sync_canvas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync courses and assignments from Canvas.
    """
    # Get Canvas credentials
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id, Credential.service == "canvas"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not connected. Please connect Canvas first.",
        )

    # Create scrape job
    scrape_job = ScrapeJob(
        user_id=current_user.id,
        credential_id=credential.id,
        service="canvas",
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

        # Initialize Canvas service
        canvas_service = CanvasService(creds["api_token"], creds["base_url"])

        # Fetch courses
        canvas_courses = await canvas_service.get_courses()

        courses_new = 0
        courses_found = len(canvas_courses)

        # Map to store canvas_id -> database course_id
        course_id_map = {}

        # Process courses
        for canvas_course in canvas_courses:
            canvas_id = str(canvas_course.get("id"))

            # Check if course already exists
            result = await db.execute(
                select(Course).where(
                    Course.user_id == current_user.id,
                    Course.source == "canvas",
                    Course.source_id == canvas_id,
                )
            )
            existing_course = result.scalar_one_or_none()

            if existing_course:
                # Update existing course
                course_data = canvas_service.parse_course(canvas_course)
                for key, value in course_data.items():
                    if key not in ["source", "source_id"]:  # Don't update these
                        setattr(existing_course, key, value)
                existing_course.last_synced = datetime.utcnow()
                course_id_map[canvas_id] = existing_course.id
            else:
                # Create new course
                course_data = canvas_service.parse_course(canvas_course)
                course_data["user_id"] = current_user.id
                course_data["course_name"] = course_data["name"]  # For backward compat
                new_course = Course(**course_data)
                db.add(new_course)
                await db.flush()
                course_id_map[canvas_id] = new_course.id
                courses_new += 1

        await db.commit()

        # Fetch all assignments
        all_assignments = await canvas_service.get_all_assignments()

        assignments_new = 0
        assignments_found = 0

        # Process assignments
        for canvas_course_id, canvas_assignments in all_assignments.items():
            canvas_course_id_str = str(canvas_course_id)

            if canvas_course_id_str not in course_id_map:
                continue  # Skip if course not in our database

            db_course_id = course_id_map[canvas_course_id_str]

            # Get course name for backward compat
            result = await db.execute(
                select(Course).where(Course.id == db_course_id)
            )
            course = result.scalar_one()

            for canvas_assignment in canvas_assignments:
                assignments_found += 1
                canvas_assignment_id = str(canvas_assignment.get("id"))

                # Check if assignment exists
                result = await db.execute(
                    select(Assignment).where(
                        Assignment.user_id == current_user.id,
                        Assignment.source == "canvas",
                        Assignment.source_id == canvas_assignment_id,
                    )
                )
                existing_assignment = result.scalar_one_or_none()

                assignment_data = canvas_service.parse_assignment(
                    canvas_assignment, db_course_id
                )
                assignment_data["user_id"] = current_user.id
                assignment_data["course_name"] = course.name  # For backward compat

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

        # Update scrape job
        scrape_job.status = "completed"
        scrape_job.completed_at = datetime.utcnow()
        scrape_job.items_found = courses_found + assignments_found
        scrape_job.items_new = courses_new + assignments_new
        scrape_job.results_summary = {
            "courses": courses_found,
            "assignments": assignments_found,
        }

        # Update credential last_synced
        credential.last_synced = datetime.utcnow()
        credential.last_sync_status = "success"
        credential.sync_count = (credential.sync_count or 0) + 1

        await db.commit()

        return SyncResponse(
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
            detail=f"Failed to sync Canvas data: {str(e)}",
        )
