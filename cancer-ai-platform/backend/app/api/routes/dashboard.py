"""
Dashboard API routes — overview stats, risk distribution, recent predictions.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard overview statistics."""
    return await dashboard_service.get_stats(db)


@router.get("/recent")
async def get_recent(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get recent predictions (patient worklist)."""
    return await dashboard_service.get_recent_predictions(db, limit=limit)
