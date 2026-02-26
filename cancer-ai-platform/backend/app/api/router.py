"""
API Router — combines all route modules under /api/v1/.
"""
from fastapi import APIRouter

from app.api.routes import auth, radiology, pathology, dashboard, reports

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(radiology.router)
api_router.include_router(pathology.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
