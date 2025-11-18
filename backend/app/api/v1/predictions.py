"""
Predictive assistant endpoints - Wraps predictive_assistant.py Phase 4 agent.
"""
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.assignment import Assignment
from app.models.analytics import Prediction

router = APIRouter()


# Pydantic schemas
class RiskAssessment(BaseModel):
    assignment_id: int
    risk_level: str  # low, medium, high, critical
    probability: float  # 0-1
    confidence: float  # 0-1
    risk_factors: List[Dict[str, Any]]
    suggested_actions: List[str]


class WorkloadOptimization(BaseModel):
    recommended_schedule: List[Dict[str, Any]]
    total_hours: float
    daily_breakdown: Dict[str, float]
    conflicts: List[str]
    optimization_score: float  # 0-1


class ProactiveSuggestion(BaseModel):
    type: str  # reminder, adjustment, resource, break
    priority: str  # low, medium, high
    title: str
    description: str
    action_url: str | None = None
    due_by: datetime | None = None


@router.get("/risk/{assignment_id}", response_model=RiskAssessment)
async def assess_risk(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assess risk of missing deadline for an assignment.

    Uses predictive_assistant.py to analyze:
    - Time pressure (days until due)
    - Historical completion rate
    - Current workload stress
    - Assignment complexity
    """
    # Get assignment
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

    # TODO: Use actual predictive_assistant.py agent
    # from app.services.predictions import PredictiveAssistant
    # predictor = PredictiveAssistant()
    # risk = await predictor.predict_risk(assignment_id)

    # Calculate risk factors (mock)
    days_until_due = (assignment.due_date - datetime.utcnow()).days
    time_pressure = max(0, 1 - (days_until_due / 14))

    risk_factors = [
        {
            "factor": "time_pressure",
            "score": time_pressure,
            "description": f"Only {days_until_due} days until due date"
        },
        {
            "factor": "complexity",
            "score": assignment.complexity_score or 0.5,
            "description": f"High complexity assignment ({assignment.blooms_level})"
        }
    ]

    # Overall risk calculation
    risk_score = (time_pressure * 0.5 + (assignment.complexity_score or 0.5) * 0.3)

    if risk_score > 0.7:
        risk_level = "critical"
    elif risk_score > 0.5:
        risk_level = "high"
    elif risk_score > 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"

    suggested_actions = [
        "Start working on this assignment today",
        "Break down into smaller tasks",
        "Schedule focused work sessions"
    ]

    # Store prediction
    prediction = Prediction(
        user_id=current_user.id,
        assignment_id=assignment_id,
        prediction_type="risk",
        predicted_value=risk_score,
        confidence_score=0.85,
        risk_level=risk_level,
        risk_factors=risk_factors,
        suggestions=suggested_actions
    )
    db.add(prediction)
    await db.commit()

    return RiskAssessment(
        assignment_id=assignment_id,
        risk_level=risk_level,
        probability=risk_score,
        confidence=0.85,
        risk_factors=risk_factors,
        suggested_actions=suggested_actions
    )


@router.post("/optimize-workload", response_model=WorkloadOptimization)
async def optimize_workload(
    max_hours_per_day: float = 8.0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate optimized study schedule for all pending assignments.

    Uses constraint satisfaction algorithm from predictive_assistant.py to:
    - Balance workload across days
    - Respect deadlines and priorities
    - Account for assignment complexity
    - Minimize stress and maximize success probability
    """
    # Get all pending assignments
    result = await db.execute(
        select(Assignment).where(
            and_(
                Assignment.user_id == current_user.id,
                Assignment.is_completed == False
            )
        ).order_by(Assignment.due_date.asc())
    )
    assignments = result.scalars().all()

    # TODO: Use actual predictive_assistant.py optimization
    # from app.services.predictions import PredictiveAssistant
    # predictor = PredictiveAssistant()
    # schedule = await predictor.optimize_schedule(assignments, max_hours_per_day)

    # Mock optimization
    total_hours = sum((a.estimated_hours or 5.0) for a in assignments)

    return WorkloadOptimization(
        recommended_schedule=[
            {
                "date": "2025-10-29",
                "assignments": [
                    {
                        "id": assignments[0].id if assignments else 1,
                        "title": assignments[0].title if assignments else "Sample",
                        "hours": 3.0
                    }
                ]
            }
        ] if assignments else [],
        total_hours=total_hours,
        daily_breakdown={
            "Monday": 6.5,
            "Tuesday": 7.0,
            "Wednesday": 5.5
        },
        conflicts=[],
        optimization_score=0.87
    )


@router.get("/suggestions", response_model=List[ProactiveSuggestion])
async def get_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get proactive AI-powered suggestions.

    Analyzes current state and provides:
    - Upcoming deadline reminders
    - Schedule adjustments
    - Resource recommendations
    - Break suggestions based on productivity patterns
    """
    # TODO: Use predictive_assistant.py for intelligent suggestions
    # from app.services.predictions import PredictiveAssistant
    # predictor = PredictiveAssistant()
    # suggestions = await predictor.generate_suggestions(current_user.id)

    # Mock suggestions
    return [
        ProactiveSuggestion(
            type="reminder",
            priority="high",
            title="Assignment Due Soon",
            description="'Research Paper' is due in 2 days. You've completed 40%.",
            due_by=datetime.utcnow()
        ),
        ProactiveSuggestion(
            type="break",
            priority="medium",
            title="Take a Break",
            description="You've been working for 2 hours. A 10-minute break will boost productivity.",
            due_by=None
        )
    ]
