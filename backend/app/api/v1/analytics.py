"""
Performance analytics endpoints - Wraps performance_analytics.py Phase 4 agent.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.analytics import PerformanceMetric

router = APIRouter()


# Pydantic schemas
class HealthScore(BaseModel):
    overall_score: float  # 0-100
    completion_rate: float
    time_management_score: float
    stress_level: float
    productivity_score: float
    trend: str  # improving, stable, declining


class TrendData(BaseModel):
    metric: str
    values: List[float]
    timestamps: List[datetime]
    slope: float
    direction: str  # up, down, stable


class AnalyticsSummary(BaseModel):
    health_score: HealthScore
    trends: List[TrendData]
    insights: List[str]
    recommendations: List[str]


@router.get("/health", response_model=HealthScore)
async def get_health_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current academic health score.

    This wraps the performance_analytics.py agent to provide:
    - Overall health score (0-100)
    - Completion rate tracking
    - Time management assessment
    - Stress level indicators
    - Productivity metrics
    """
    # TODO: Import actual performance_analytics.py agent
    # from app.services.analytics import PerformanceAnalytics
    # analytics = PerformanceAnalytics()
    # health = await analytics.calculate_health_score(current_user.id)

    # Mock response
    return HealthScore(
        overall_score=78.5,
        completion_rate=0.85,
        time_management_score=72.0,
        stress_level=0.42,
        productivity_score=81.0,
        trend="improving"
    )


@router.get("/trends", response_model=List[TrendData])
async def get_performance_trends(
    days: int = Query(default=30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance trends over time.

    Analyzes time series data to identify:
    - Completion rate trends
    - Productivity patterns
    - Stress level changes
    - Study hour patterns
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get metrics from database
    result = await db.execute(
        select(PerformanceMetric)
        .where(
            and_(
                PerformanceMetric.user_id == current_user.id,
                PerformanceMetric.recorded_at >= cutoff_date
            )
        )
        .order_by(PerformanceMetric.recorded_at.asc())
    )
    metrics = result.scalars().all()

    # TODO: Use performance_analytics.py for trend analysis
    # Group by metric type and calculate trends

    # Mock response
    return [
        TrendData(
            metric="completion_rate",
            values=[0.75, 0.78, 0.82, 0.85],
            timestamps=[
                datetime.utcnow() - timedelta(days=21),
                datetime.utcnow() - timedelta(days=14),
                datetime.utcnow() - timedelta(days=7),
                datetime.utcnow()
            ],
            slope=0.033,
            direction="up"
        )
    ]


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive analytics summary with AI insights.
    """
    # Get health score
    health = HealthScore(
        overall_score=78.5,
        completion_rate=0.85,
        time_management_score=72.0,
        stress_level=0.42,
        productivity_score=81.0,
        trend="improving"
    )

    # Get trends
    trends = [
        TrendData(
            metric="completion_rate",
            values=[0.75, 0.78, 0.82, 0.85],
            timestamps=[
                datetime.utcnow() - timedelta(days=21),
                datetime.utcnow() - timedelta(days=14),
                datetime.utcnow() - timedelta(days=7),
                datetime.utcnow()
            ],
            slope=0.033,
            direction="up"
        )
    ]

    # AI-generated insights
    insights = [
        "Your completion rate has improved by 10% over the last month",
        "You're most productive on Tuesday and Wednesday mornings",
        "Stress levels are highest during midterm weeks"
    ]

    recommendations = [
        "Consider starting assignments earlier to reduce last-minute stress",
        "Schedule complex tasks during your peak productivity hours",
        "Take breaks every 50 minutes for optimal focus"
    ]

    return AnalyticsSummary(
        health_score=health,
        trends=trends,
        insights=insights,
        recommendations=recommendations
    )


@router.post("/record", status_code=status.HTTP_201_CREATED)
async def record_metric(
    metric_type: str,
    value: float,
    course_name: str | None = None,
    metadata: Dict[str, Any] | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a performance metric.
    """
    metric = PerformanceMetric(
        user_id=current_user.id,
        metric_type=metric_type,
        metric_value=value,
        course_name=course_name,
        metadata=metadata or {}
    )

    db.add(metric)
    await db.commit()

    return {"status": "recorded"}
