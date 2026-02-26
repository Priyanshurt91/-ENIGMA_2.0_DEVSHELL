"""
Pydantic schemas for Prediction endpoints.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PredictionRequest(BaseModel):
    cancer_type: str
    scan_type: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    biomarkers: Optional[dict] = None  # {wbc, blast, hgb, plt}


class PredictionResponse(BaseModel):
    id: int
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    cancer_type: str
    scan_type: str
    predicted_class: str
    confidence: float
    risk_score: float
    risk_level: str
    probabilities: Optional[dict] = None
    heatmap_path: Optional[str] = None
    image_path: Optional[str] = None
    biomarkers: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RiskAssessment(BaseModel):
    overall_risk: float
    risk_level: str
    cancer_scores: list[dict]  # [{name, score, grade, color}]
    recommendations: list[dict]  # [{icon, title, desc, color}]
