"""
Assignment intelligence endpoints - Wraps assignment_intelligence.py Phase 4 agent.
"""
from typing import List, Dict, Any
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
class ComplexityAnalysis(BaseModel):
    complexity_score: float
    blooms_level: str
    cognitive_score: float
    estimated_hours: float
    factors: Dict[str, Any]
    required_skills: List[str]


class ResourceRecommendation(BaseModel):
    title: str
    type: str  # video, article, tool, course
    url: str | None = None
    relevance_score: float
    description: str | None = None


class IntelligenceResponse(BaseModel):
    assignment_id: int
    complexity: ComplexityAnalysis
    resources: List[ResourceRecommendation]
    similar_assignments: List[int]  # IDs of similar past assignments


@router.post("/{assignment_id}/analyze", response_model=IntelligenceResponse)
async def analyze_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run AI analysis on an assignment using Phase 4 intelligence agent.

    This endpoint wraps the assignment_intelligence.py agent and provides:
    - Bloom's Taxonomy cognitive level classification
    - Multi-dimensional complexity scoring
    - Estimated time requirements
    - Required skills identification
    - Resource recommendations
    - Similar assignment matching
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

    # TODO: Import and use the actual assignment_intelligence.py agent
    # from app.services.intelligence import AssignmentIntelligence
    # intelligence = AssignmentIntelligence()
    # analysis = await intelligence.analyze(assignment)

    # Mock response for now
    complexity = ComplexityAnalysis(
        complexity_score=0.75,
        blooms_level="apply",
        cognitive_score=0.68,
        estimated_hours=8.5,
        factors={
            "length": 0.8,
            "technical": 0.7,
            "research": 0.6
        },
        required_skills=["critical thinking", "research", "writing"]
    )

    resources = [
        ResourceRecommendation(
            title="How to Write a Research Paper",
            type="article",
            url="https://example.com/guide",
            relevance_score=0.92,
            description="Comprehensive guide for academic writing"
        )
    ]

    # Update assignment with analysis
    assignment.complexity_score = complexity.complexity_score
    assignment.blooms_level = complexity.blooms_level
    assignment.cognitive_score = complexity.cognitive_score
    assignment.estimated_hours = complexity.estimated_hours
    assignment.required_skills = complexity.required_skills
    assignment.complexity_factors = complexity.factors
    assignment.recommended_resources = [r.model_dump() for r in resources]

    await db.commit()

    return IntelligenceResponse(
        assignment_id=assignment_id,
        complexity=complexity,
        resources=resources,
        similar_assignments=[]
    )


@router.get("/{assignment_id}/skills", response_model=List[str])
async def get_required_skills(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get required skills for an assignment.
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

    return assignment.required_skills or []


@router.get("/{assignment_id}/resources", response_model=List[ResourceRecommendation])
async def get_recommended_resources(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommended learning resources for an assignment.
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

    resources = assignment.recommended_resources or []
    return [ResourceRecommendation(**r) for r in resources]
