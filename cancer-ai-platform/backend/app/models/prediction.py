"""
Prediction ORM model — stores each AI analysis result.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, JSON
from app.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    patient_id = Column(String(50), nullable=True)
    patient_name = Column(String(255), nullable=True)
    patient_age = Column(Integer, nullable=True)

    cancer_type = Column(String(50), nullable=False)  # lung, brain, blood, etc.
    scan_type = Column(String(50), nullable=False)     # ct, mri, xray, pathology
    image_path = Column(String(500), nullable=True)

    predicted_class = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    probabilities = Column(JSON, nullable=True)        # {class: prob, ...}
    heatmap_path = Column(String(500), nullable=True)  # GradCAM image path

    # Biomarkers (optional, for blood cancer)
    biomarkers = Column(JSON, nullable=True)           # {wbc: 4.5, blast: 0, ...}

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
