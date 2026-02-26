"""
User ORM model.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="doctor")  # doctor | admin | radiologist
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
