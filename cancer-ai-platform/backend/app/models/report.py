"""
Report ORM model — stores generated clinical reports.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.database.base import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    prediction_id = Column(Integer, nullable=False, index=True)

    patient_id = Column(String(50), nullable=True)
    patient_name = Column(String(255), nullable=True)

    report_type = Column(String(50), default="radiology")  # radiology | pathology
    sections = Column(JSON, nullable=True)  # {indication, technique, findings, impression, recommendation}
    full_text = Column(Text, nullable=True)
    generated_by = Column(String(50), default="gemini")  # gemini | rule_based

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
