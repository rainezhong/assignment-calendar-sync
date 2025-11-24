"""
Task management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.assignment import Assignment
from app.models.task import Task
from app.services.task_generation_service import TaskGenerationService

router = APIRouter()


# Pydantic schemas
class TaskResponse(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    title: str
    description: Optional[str]
    priority: int
    due_date: datetime
    completed_at: Optional[datetime]
    is_completed: bool
    order: int
    created_at: datetime

    # Include assignment info for context
    assignment_title: Optional[str] = None
    assignment_course: Optional[str] = None

    class Config:
        from_attributes = True


class GenerateTasksRequest(BaseModel):
    regenerate: bool = False


class UpdateTaskRequest(BaseModel):
    is_completed: Optional[bool] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskCalendarEvent(BaseModel):
    """Task formatted as a calendar event."""
    id: int
    title: str
    start: datetime
    end: datetime
    priority: int
    is_completed: bool
    assignment_title: str
    assignment_id: int
    type: str = "task"


@router.post("/assignments/{assignment_id}/generate-tasks", response_model=List[TaskResponse])
async def generate_tasks(
    assignment_id: int,
    request: GenerateTasksRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered task breakdown for an assignment.
    """
    # Get assignment
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.user_id == current_user.id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check if tasks already exist
    result = await db.execute(
        select(Task).where(Task.assignment_id == assignment_id)
    )
    existing_tasks = result.scalars().all()

    if existing_tasks and not request.regenerate:
        raise HTTPException(
            status_code=400,
            detail="Tasks already exist. Set regenerate=true to recreate."
        )

    # Delete existing if regenerating
    if existing_tasks and request.regenerate:
        for task in existing_tasks:
            await db.delete(task)
        await db.commit()

    # Generate tasks using AI
    task_service = TaskGenerationService()
    tasks = await task_service.generate_tasks_for_assignment(assignment)

    # Save to database
    for task in tasks:
        db.add(task)

    # Update assignment
    assignment.tasks_generated = True
    assignment.tasks_generated_at = datetime.utcnow()

    await db.commit()

    # Refresh to get IDs and created_at
    for task in tasks:
        await db.refresh(task)

    # Add assignment info to response
    task_responses = []
    for task in tasks:
        task_dict = TaskResponse.model_validate(task).model_dump()
        task_dict['assignment_title'] = assignment.title
        task_dict['assignment_course'] = assignment.course_name
        task_responses.append(TaskResponse(**task_dict))

    return task_responses


@router.get("/assignments/{assignment_id}/tasks", response_model=List[TaskResponse])
async def get_assignment_tasks(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks for an assignment."""
    # Verify assignment belongs to user
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.user_id == current_user.id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Get tasks ordered by order field
    result = await db.execute(
        select(Task)
        .where(Task.assignment_id == assignment_id)
        .order_by(Task.order)
    )
    tasks = result.scalars().all()

    # Add assignment info to each task
    task_responses = []
    for task in tasks:
        task_dict = TaskResponse.model_validate(task).model_dump()
        task_dict['assignment_title'] = assignment.title
        task_dict['assignment_course'] = assignment.course_name
        task_responses.append(TaskResponse(**task_dict))

    return task_responses


@router.get("/tasks", response_model=List[TaskResponse])
async def get_all_tasks(
    status: Optional[str] = Query(None, regex="^(pending|completed)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tasks for current user, optionally filtered by status.
    Ordered by priority (1->3) then due date.
    """
    query = select(Task).where(Task.user_id == current_user.id)

    if status == "pending":
        query = query.where(Task.is_completed == False)
    elif status == "completed":
        query = query.where(Task.is_completed == True)

    # Order by priority (1=high, 2=medium, 3=low) then due date
    query = query.order_by(Task.priority, Task.due_date)

    result = await db.execute(query)
    tasks = result.scalars().all()

    # Get all assignments for this user to add context
    result = await db.execute(
        select(Assignment).where(Assignment.user_id == current_user.id)
    )
    assignments = {a.id: a for a in result.scalars().all()}

    # Add assignment info to each task
    task_responses = []
    for task in tasks:
        task_dict = TaskResponse.model_validate(task).model_dump()
        assignment = assignments.get(task.assignment_id)
        if assignment:
            task_dict['assignment_title'] = assignment.title
            task_dict['assignment_course'] = assignment.course_name
        task_responses.append(TaskResponse(**task_dict))

    return task_responses


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a task (mark complete, change priority, reschedule)."""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    if request.is_completed is not None:
        task.is_completed = request.is_completed
        if request.is_completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

    if request.priority is not None:
        task.priority = request.priority

    if request.due_date is not None:
        task.due_date = request.due_date

    await db.commit()
    await db.refresh(task)

    # Update assignment completion percentage
    await update_assignment_progress(task.assignment_id, db)

    # Get assignment for context
    result = await db.execute(
        select(Assignment).where(Assignment.id == task.assignment_id)
    )
    assignment = result.scalar_one_or_none()

    task_dict = TaskResponse.model_validate(task).model_dump()
    if assignment:
        task_dict['assignment_title'] = assignment.title
        task_dict['assignment_course'] = assignment.course_name

    return TaskResponse(**task_dict)


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a task as complete (convenience endpoint)."""
    return await update_task(
        task_id,
        UpdateTaskRequest(is_completed=True),
        current_user,
        db
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    assignment_id = task.assignment_id
    await db.delete(task)
    await db.commit()

    # Update assignment progress
    await update_assignment_progress(assignment_id, db)

    return {"status": "success", "message": "Task deleted"}


@router.get("/tasks/calendar", response_model=List[TaskCalendarEvent])
async def get_tasks_calendar(
    start_date: datetime = Query(..., description="Start of date range"),
    end_date: datetime = Query(..., description="End of date range"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get tasks formatted as calendar events for a date range.
    """
    result = await db.execute(
        select(Task).where(
            and_(
                Task.user_id == current_user.id,
                Task.due_date >= start_date,
                Task.due_date <= end_date
            )
        ).order_by(Task.due_date)
    )
    tasks = result.scalars().all()

    # Get assignments
    result = await db.execute(
        select(Assignment).where(Assignment.user_id == current_user.id)
    )
    assignments = {a.id: a for a in result.scalars().all()}

    # Format as calendar events
    events = []
    for task in tasks:
        assignment = assignments.get(task.assignment_id)
        event = TaskCalendarEvent(
            id=task.id,
            title=task.title,
            start=task.due_date,
            end=task.due_date,  # Tasks are point-in-time events
            priority=task.priority,
            is_completed=task.is_completed,
            assignment_title=assignment.title if assignment else "Unknown",
            assignment_id=task.assignment_id,
        )
        events.append(event)

    return events


async def update_assignment_progress(assignment_id: int, db: AsyncSession):
    """Recalculate assignment completion % based on tasks."""
    result = await db.execute(
        select(Task).where(Task.assignment_id == assignment_id)
    )
    tasks = result.scalars().all()

    if not tasks:
        return

    completed_count = sum(1 for t in tasks if t.is_completed)
    completion_percentage = (completed_count / len(tasks)) * 100

    await db.execute(
        update(Assignment)
        .where(Assignment.id == assignment_id)
        .values(completion_percentage=completion_percentage)
    )
    await db.commit()
