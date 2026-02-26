"""
Radiology API routes — image upload, analysis, history.
"""
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
import io

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import radiology_service
from app.schemas.prediction import PredictionResponse

router = APIRouter(prefix="/radiology", tags=["radiology"])


@router.post("/analyze", response_model=PredictionResponse)
async def analyze(
    file: UploadFile = File(...),
    cancer_type: str = Form("lung"),
    scan_type: str = Form("ct"),
    patient_id: str = Form(None),
    patient_name: str = Form(None),
    patient_age: int = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Upload a medical image and run AI analysis."""
    if not file.content_type or not file.content_type.startswith("image"):
        # Allow non-image types for DICOM/NIfTI (they don't have image/ MIME types)
        pass

    content = await file.read()
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    patient_info = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "patient_age": patient_age,
    }

    result = await radiology_service.analyze_image(
        image=image,
        cancer_type=cancer_type,
        scan_type=scan_type,
        patient_info=patient_info,
        db=db,
        user_id=user.id if user else None,
    )

    return result


@router.get("/history")
async def history(
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Get radiology prediction history."""
    predictions = await radiology_service.get_history(db, user_id=user.id if user else None)
    return [PredictionResponse.model_validate(p) for p in predictions]
