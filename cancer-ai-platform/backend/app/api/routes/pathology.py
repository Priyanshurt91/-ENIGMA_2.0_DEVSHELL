"""
Pathology API routes — blood slide upload, analysis, history.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
import io
import json

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import pathology_service
from app.schemas.prediction import PredictionResponse

router = APIRouter(prefix="/pathology", tags=["pathology"])


@router.post("/analyze", response_model=PredictionResponse)
async def analyze(
    file: UploadFile = File(...),
    patient_id: str = Form(None),
    patient_name: str = Form(None),
    patient_age: int = Form(None),
    wbc: float = Form(None),
    blast: float = Form(None),
    hgb: float = Form(None),
    plt: float = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Upload a blood slide image and run blood cancer analysis."""
    content = await file.read()
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    patient_info = {
        "patient_id": patient_id,
        "name": patient_name,
        "age": patient_age,
    }

    biomarkers = None
    if any(v is not None for v in [wbc, blast, hgb, plt]):
        biomarkers = {
            "wbc": wbc,
            "blast": blast,
            "hgb": hgb,
            "plt": plt,
        }

    result = await pathology_service.analyze_blood_slide(
        image=image,
        patient_info=patient_info,
        biomarkers=biomarkers,
        db=db,
        user_id=user.id if user else None,
    )

    return result


@router.get("/history")
async def history(
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    predictions = await pathology_service.get_history(db, user_id=user.id if user else None)
    return [PredictionResponse.model_validate(p) for p in predictions]
