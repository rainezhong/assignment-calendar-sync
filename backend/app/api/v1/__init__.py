"""
API v1 routes.
"""
from fastapi import APIRouter
from app.api.v1 import auth, assignments, intelligence, analytics, predictions, career

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(career.router, prefix="/career", tags=["career"])
