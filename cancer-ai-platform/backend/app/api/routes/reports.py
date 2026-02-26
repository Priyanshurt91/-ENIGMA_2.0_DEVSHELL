"""
Report API routes — generate and fetch clinical reports.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import report_service
from app.schemas.report import ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate/{prediction_id}")
async def generate_report(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Generate a clinical report from a prediction (RAG → Gemini pipeline)."""
    try:
        result = await report_service.generate_report(
            prediction_id=prediction_id,
            db=db,
            user_id=user.id if user else None,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=list[ReportResponse])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    reports = await report_service.get_reports(db, user_id=user.id if user else None)
    return [ReportResponse.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    report = await report_service.get_report(report_id, db)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.model_validate(report)
