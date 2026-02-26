"""
Radiology Service — orchestrates image upload → model inference → GradCAM → save prediction.
"""
import os
import uuid
import time
import asyncio
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.core.logging import logger
from app.core.constants import CancerType, ScanType, risk_level_from_score
from app.models.prediction import Prediction
from app.ai_models.explainability.gradcam import save_heatmap


async def analyze_image(
    image: Image.Image,
    cancer_type: str,
    scan_type: str,
    patient_info: dict,
    db: AsyncSession,
    user_id: int = None,
) -> dict:
    """
    Full radiology analysis pipeline:
    1. Select model based on cancer_type
    2. Run inference
    3. Generate GradCAM heatmap
    4. Save prediction to DB
    5. Return result
    """
    t0 = time.time()

    # Save uploaded image
    img_id = str(uuid.uuid4())[:8]
    img_filename = f"{cancer_type}_{img_id}.png"
    img_path = os.path.join(settings.UPLOAD_DIR, img_filename)
    image.save(img_path)

    # Run inference in a thread so it doesn't block the async event loop
    t1 = time.time()
    result = await asyncio.to_thread(_run_inference, image, cancer_type)
    logger.info(f"⏱️ Inference took {time.time()-t1:.2f}s")

    # Generate GradCAM heatmap (also in a thread)
    heatmap_path = None
    try:
        model = _get_model(cancer_type)
        if model is not None:
            heatmap_filename = f"heatmap_{cancer_type}_{img_id}.png"
            heatmap_path = os.path.join(settings.UPLOAD_DIR, heatmap_filename)
            t2 = time.time()
            await asyncio.to_thread(save_heatmap, image, model, heatmap_path)
            logger.info(f"⏱️ GradCAM took {time.time()-t2:.2f}s")
    except Exception as e:
        logger.warning(f"GradCAM failed: {e}")

    # Calculate risk
    risk_score = result.get("risk_score", result.get("confidence", 0))
    risk_level = risk_level_from_score(risk_score)

    # Save to DB
    prediction = Prediction(
        user_id=user_id,
        patient_id=patient_info.get("patient_id"),
        patient_name=patient_info.get("patient_name"),
        patient_age=patient_info.get("patient_age"),
        cancer_type=cancer_type,
        scan_type=scan_type,
        image_path=img_filename,
        predicted_class=result["predicted_class"],
        confidence=result["confidence"],
        risk_score=risk_score,
        risk_level=risk_level.value,
        probabilities=result.get("probabilities"),
        heatmap_path=heatmap_filename if heatmap_path else None,
    )
    db.add(prediction)
    await db.flush()
    await db.refresh(prediction)

    logger.info(f"✅ Radiology analysis complete in {time.time()-t0:.2f}s: {cancer_type}/{result['predicted_class']} ({result['confidence']}%)")

    return {
        "id": prediction.id,
        "cancer_type": cancer_type,
        "scan_type": scan_type,
        "predicted_class": result["predicted_class"],
        "confidence": result["confidence"],
        "risk_score": risk_score,
        "risk_level": risk_level.value,
        "probabilities": result.get("probabilities"),
        "heatmap_path": heatmap_filename if heatmap_path else None,
        "image_path": img_filename,
        "patient_id": patient_info.get("patient_id"),
        "patient_name": patient_info.get("patient_name"),
        "patient_age": patient_info.get("patient_age"),
        "created_at": prediction.created_at,
    }


def _run_inference(image: Image.Image, cancer_type: str) -> dict:
    """Route to the correct model inference."""
    if cancer_type == "lung":
        from app.ai_models.radiology.lung_cancer.inference import predict
        return predict(image)
    elif cancer_type == "brain":
        from app.ai_models.radiology.brain_tumor.inference import predict
        return predict(image)
    elif cancer_type == "ct" or cancer_type == "bone":
        from app.ai_models.radiology.ct_analysis.inference import predict
        return predict(image)
    else:
        # Generic fallback
        from app.ai_models.radiology.lung_cancer.inference import predict
        return predict(image)


def _get_model(cancer_type: str):
    """Get the loaded PyTorch model for GradCAM."""
    try:
        if cancer_type == "lung":
            from app.ai_models.radiology.lung_cancer.model import get_model
            return get_model()
        elif cancer_type == "brain":
            from app.ai_models.radiology.brain_tumor.mri_model import get_model
            return get_model()
        elif cancer_type in ("ct", "bone"):
            from app.ai_models.radiology.ct_analysis.ct_model import get_model
            return get_model()
    except Exception:
        return None
    return None


async def get_history(db: AsyncSession, user_id: int = None, limit: int = 20) -> list:
    """Get prediction history."""
    query = select(Prediction).where(
        Prediction.scan_type != "pathology"
    ).order_by(Prediction.created_at.desc()).limit(limit)
    if user_id:
        query = query.where(Prediction.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()
