"""
Pydantic schemas for Report endpoints.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReportCreate(BaseModel):
    prediction_id: int
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    prediction_id: int
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    report_type: str
    sections: Optional[dict] = None
    full_text: Optional[str] = None
    generated_by: str
    created_at: datetime

    class Config:
        from_attributes = True
