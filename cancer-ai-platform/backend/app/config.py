"""
Application configuration — loads from .env file.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # cancer-ai-platform/


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "ChronoScan"
    APP_VERSION: str = "2.1"
    DEBUG: bool = True

    # ── Auth ─────────────────────────────────────────────
    SECRET_KEY: str = "chronoscan-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'chronoscan.db'}"

    # ── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # ── Model Paths ──────────────────────────────────────
    MODELS_DIR: str = str(BASE_DIR / "models_storage")
    LUNG_MODEL_PATH: str = str(BASE_DIR / "models_storage" / "lung" / "lung_cancer.pt")
    BLOOD_MODEL_PATH: str = str(BASE_DIR / "models_storage" / "pathology" / "blood_cancer_classifier.h5")
    BRAIN_MODEL_PATH: str = str(BASE_DIR / "models_storage" / "brain" / "mri.pth")
    CT_MODEL_PATH: str = str(BASE_DIR / "models_storage" / "ct" / "ct.pth")
    XRAY_MODEL_PATH: str = str(BASE_DIR / "models_storage" / "xray" / "xray.pth")

    # ── Upload ───────────────────────────────────────────
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # ── Gemini ───────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ── RAG ───────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "chroma_db")
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5

    class Config:
        env_file = str(BASE_DIR / ".env")
        extra = "ignore"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
for d in ["lung", "brain", "ct", "pathology", "xray"]:
    os.makedirs(os.path.join(settings.MODELS_DIR, d), exist_ok=True)
