"""
Report Service — generates and manages clinical reports using LLM pipeline.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.prediction import Prediction
from app.models.report import Report
from app.services import llm_service
from app.core.logging import logger


async def generate_report(prediction_id: int, db: AsyncSession, user_id: int = None) -> dict:
    """
    Generate a clinical report from a prediction using RAG → Gemini pipeline.
    """
    # Fetch the prediction
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise ValueError(f"Prediction {prediction_id} not found")

    # Build prediction data dict
    prediction_data = {
        "cancer_type": prediction.cancer_type,
        "scan_type": prediction.scan_type,
        "predicted_class": prediction.predicted_class,
        "confidence": prediction.confidence,
        "risk_score": prediction.risk_score,
        "probabilities": prediction.probabilities,
    }
    patient_info = {
        "patient_id": prediction.patient_id,
        "name": prediction.patient_name,
        "age": prediction.patient_age,
        "biomarkers": prediction.biomarkers,
    }

    # Generate report via LLM pipeline (RAG → Gemini / rule-based)
    llm_result = await llm_service.generate_report(prediction_data, patient_info)

    # Build full text from sections
    sections = llm_result["sections"]
    full_text = "\n\n".join(
        f"**{key.upper().replace('_', ' ')}**\n{value}"
        for key, value in sections.items()
    )

    # Save report to DB
    report = Report(
        user_id=user_id,
        prediction_id=prediction_id,
        patient_id=prediction.patient_id,
        patient_name=prediction.patient_name,
        report_type="radiology" if prediction.scan_type != "pathology" else "pathology",
        sections=sections,
        full_text=full_text,
        generated_by=llm_result["generated_by"],
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    logger.info(f"Report #{report.id} generated for prediction #{prediction_id} via {llm_result['generated_by']}")

    return {
        "id": report.id,
        "prediction_id": prediction_id,
        "patient_id": prediction.patient_id,
        "patient_name": prediction.patient_name,
        "report_type": report.report_type,
        "sections": sections,
        "full_text": full_text,
        "generated_by": llm_result["generated_by"],
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


async def get_reports(db: AsyncSession, user_id: int = None, limit: int = 20) -> list:
    query = select(Report).order_by(Report.created_at.desc()).limit(limit)
    if user_id:
        query = query.where(Report.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()


async def get_report(report_id: int, db: AsyncSession) -> Report | None:
    result = await db.execute(select(Report).where(Report.id == report_id))
    return result.scalar_one_or_none()
