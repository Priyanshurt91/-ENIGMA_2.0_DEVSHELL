"""
Pathology Service — handles blood cancer analysis from blood slide images.
"""
import os
import uuid
import asyncio
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.core.logging import logger
from app.core.constants import risk_level_from_score
from app.models.prediction import Prediction
from app.ai_models.pathology.inference import predict


async def analyze_blood_slide(
    image: Image.Image,
    patient_info: dict,
    biomarkers: dict = None,
    db: AsyncSession = None,
    user_id: int = None,
) -> dict:
    """
    Analyze a blood slide image for blood cancer detection.
    Optionally incorporates biomarker data (CBC values).
    """
    # Save image
    img_id = str(uuid.uuid4())[:8]
    img_filename = f"blood_{img_id}.png"
    img_path = os.path.join(settings.UPLOAD_DIR, img_filename)
    image.save(img_path)

    # Run blood cancer inference in a thread to avoid blocking
    result = await asyncio.to_thread(predict, image)

    # Incorporate biomarkers into risk scoring
    risk_score = result.get("risk_score", 0)
    if biomarkers:
        risk_score = _adjust_risk_with_biomarkers(risk_score, biomarkers)

    risk_level = risk_level_from_score(risk_score)

    # Save to DB
    prediction = Prediction(
        user_id=user_id,
        patient_id=patient_info.get("patient_id"),
        patient_name=patient_info.get("name"),
        patient_age=patient_info.get("age"),
        cancer_type="blood",
        scan_type="pathology",
        image_path=img_filename,
        predicted_class=result["predicted_class"],
        confidence=result["confidence"],
        risk_score=risk_score,
        risk_level=risk_level.value,
        probabilities=result.get("probabilities"),
        biomarkers=biomarkers,
    )
    db.add(prediction)
    await db.flush()
    await db.refresh(prediction)

    logger.info(f"Pathology analysis complete: {result['predicted_class']} ({result['confidence']}%)")

    return {
        "id": prediction.id,
        "cancer_type": "blood",
        "scan_type": "pathology",
        "predicted_class": result["predicted_class"],
        "confidence": result["confidence"],
        "risk_score": risk_score,
        "risk_level": risk_level.value,
        "probabilities": result.get("probabilities"),
        "biomarkers": biomarkers,
        "image_path": img_filename,
        "patient_id": patient_info.get("patient_id"),
        "patient_name": patient_info.get("name"),
        "created_at": prediction.created_at,
    }


def _adjust_risk_with_biomarkers(base_risk: float, biomarkers: dict) -> float:
    """Adjust risk score based on CBC biomarker values."""
    risk = base_risk
    wbc = biomarkers.get("wbc")
    blast = biomarkers.get("blast")
    hgb = biomarkers.get("hgb")
    plt = biomarkers.get("plt")

    if wbc and float(wbc) > 11:
        risk = min(risk + 10, 100)
    if blast and float(blast) > 5:
        risk = min(risk + 20, 100)
    if hgb and float(hgb) < 10:
        risk = min(risk + 10, 100)
    if plt and float(plt) < 100:
        risk = min(risk + 10, 100)

    return round(risk, 2)


async def get_history(db: AsyncSession, user_id: int = None, limit: int = 20) -> list:
    query = select(Prediction).where(
        Prediction.scan_type == "pathology"
    ).order_by(Prediction.created_at.desc()).limit(limit)
    if user_id:
        query = query.where(Prediction.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()
