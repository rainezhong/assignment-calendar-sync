"""
Assignment CRUD endpoints.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.assignment import Assignment

router = APIRouter()


# Pydantic schemas
class AssignmentCreate(BaseModel):
    title: str
    description: str | None = None
    course_name: str
    assignment_type: str
    due_date: datetime


class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    course_name: str | None = None
    assignment_type: str | None = None
    due_date: datetime | None = None
    is_completed: bool | None = None
    completion_percentage: float | None = None
    actual_hours_spent: float | None = None
    difficulty_rating: int | None = None
    quality_score: float | None = None


class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: str | None
    course_name: str
    assignment_type: str
    due_date: datetime
    is_completed: bool
    completion_percentage: float
    complexity_score: float | None
    blooms_level: str | None
    estimated_hours: float | None
    actual_hours_spent: float
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new assignment.
    AI analysis will be triggered automatically.
    """
    assignment = Assignment(
        user_id=current_user.id,
        **assignment_data.model_dump()
    )

    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    # TODO: Trigger async AI analysis task
    # await analyze_assignment_intelligence(assignment.id)

    return assignment


@router.get("/", response_model=List[AssignmentResponse])
async def list_assignments(
    skip: int = 0,
    limit: int = 100,
    course_name: str | None = None,
    is_completed: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's assignments with optional filters.
    """
    query = select(Assignment).where(Assignment.user_id == current_user.id)

    if course_name:
        query = query.where(Assignment.course_name == course_name)

    if is_completed is not None:
        query = query.where(Assignment.is_completed == is_completed)

    query = query.order_by(Assignment.due_date.asc()).offset(skip).limit(limit)

    result = await db.execute(query)
    assignments = result.scalars().all()

    return assignments


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific assignment by ID.
    """
    result = await db.execute(
        select(Assignment).where(
            and_(
                Assignment.id == assignment_id,
                Assignment.user_id == current_user.id
            )
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    return assignment


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing assignment.
    """
    result = await db.execute(
        select(Assignment).where(
            and_(
                Assignment.id == assignment_id,
                Assignment.user_id == current_user.id
            )
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    # Update fields
    update_data = assignment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)

    # Mark completion timestamp
    if assignment_data.is_completed and not assignment.completed_at:
        assignment.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(assignment)

    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an assignment.
    """
    result = await db.execute(
        select(Assignment).where(
            and_(
                Assignment.id == assignment_id,
                Assignment.user_id == current_user.id
            )
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    await db.delete(assignment)
    await db.commit()

    return None
