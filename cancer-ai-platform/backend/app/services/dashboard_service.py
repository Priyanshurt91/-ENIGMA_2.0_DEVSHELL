from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.prediction import Prediction
from app.models.report import Report
from app.models.user import User


async def get_stats(db: AsyncSession) -> dict:
    """Get overview dashboard statistics."""
    total_scans = (await db.execute(select(func.count(Prediction.id)))).scalar() or 0
    total_reports = (await db.execute(select(func.count(Report.id)))).scalar() or 0
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0

 
    avg_confidence = (await db.execute(select(func.avg(Prediction.confidence)))).scalar() or 0


    risk_dist = {}
    for level in ["LOW", "MODERATE", "HIGH", "CRITICAL"]:
        count = (await db.execute(
            select(func.count(Prediction.id)).where(Prediction.risk_level == level)
        )).scalar() or 0
        risk_dist[level] = count

    cancer_stats = []
    for ct in ["lung", "brain", "blood", "bone", "skin", "breast"]:
        count = (await db.execute(
            select(func.count(Prediction.id)).where(Prediction.cancer_type == ct)
        )).scalar() or 0
        avg_risk = (await db.execute(
            select(func.avg(Prediction.risk_score)).where(Prediction.cancer_type == ct)
        )).scalar() or 0
        cancer_stats.append({"cancer_type": ct, "count": count, "avg_risk": round(float(avg_risk), 1)})

    return {
        "total_scans": total_scans,
        "total_reports": total_reports,
        "total_users": total_users,
        "avg_confidence": round(float(avg_confidence), 1),
        "risk_distribution": risk_dist,
        "cancer_stats": cancer_stats,
    }


async def get_recent_predictions(db: AsyncSession, limit: int = 10) -> list:
    """Get most recent predictions as patient worklist."""
    result = await db.execute(
        select(Prediction).order_by(Prediction.created_at.desc()).limit(limit)
    )
    predictions = result.scalars().all()
    return [
        {
            "id": p.id,
            "patient_id": p.patient_id,
            "patient_name": p.patient_name,
            "patient_age": p.patient_age,
            "cancer_type": p.cancer_type,
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "predicted_class": p.predicted_class,
            "confidence": p.confidence,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in predictions
    ]
