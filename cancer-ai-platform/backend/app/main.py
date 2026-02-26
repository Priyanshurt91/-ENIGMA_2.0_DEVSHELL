"""
ChronoScan v2.1 — FastAPI Application Entry Point
AI-Powered Early Cancer Detection System
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.logging import logger
from app.database.session import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Log GPU info
    _log_gpu_info()

    # Load AI models
    _load_models()
    logger.info("✅ AI models loaded")

    # Initialize RAG
    try:
        from app.services.rag_service import initialize as init_rag
        init_rag()
        logger.info("✅ RAG service initialized")
    except Exception as e:
        logger.warning(f"⚠️  RAG init skipped: {e}")

    # Initialize Gemini
    try:
        from app.services.gemini_service import initialize as init_gemini
        init_gemini()
        logger.info("✅ Gemini service initialized")
    except Exception as e:
        logger.warning(f"⚠️  Gemini init skipped: {e}")

    logger.info(f"🟢 {settings.APP_NAME} is ready!")
    yield

    logger.info(f"🔴 {settings.APP_NAME} shutting down.")


def _log_gpu_info():
    """Log GPU availability for both PyTorch and TensorFlow."""
    logger.info("─── GPU Diagnostics ───")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            logger.info(f"🟢 PyTorch CUDA: {gpu_name} ({vram:.1f} GB VRAM)")
        else:
            logger.warning("🔴 PyTorch CUDA: NOT available — running on CPU")
    except Exception as e:
        logger.warning(f"PyTorch GPU check failed: {e}")

    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"🟢 TensorFlow GPUs: {[g.name for g in gpus]}")
        else:
            logger.warning("🔴 TensorFlow: No GPU detected — running on CPU")
    except Exception as e:
        logger.warning(f"TensorFlow GPU check failed: {e}")
    logger.info("───────────────────────")


def _load_models():
    """Load all AI models at startup."""
    try:
        from app.ai_models.radiology.lung_cancer.model import load_model as load_lung
        load_lung(settings.LUNG_MODEL_PATH)
    except Exception as e:
        logger.warning(f"Lung model: {e}")

    try:
        from app.ai_models.pathology.blood_cancer_model import load_model as load_blood
        load_blood(settings.BLOOD_MODEL_PATH)
    except Exception as e:
        logger.warning(f"Blood model: {e}")

    try:
        from app.ai_models.radiology.brain_tumor.mri_model import load_model as load_brain
        load_brain(settings.BRAIN_MODEL_PATH)
    except Exception as e:
        logger.warning(f"Brain model: {e}")

    try:
        from app.ai_models.radiology.ct_analysis.ct_model import load_model as load_ct
        load_ct(settings.CT_MODEL_PATH)
    except Exception as e:
        logger.warning(f"CT model: {e}")


# ── Create App ───────────────────────────────────────────
app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="AI-Powered Early Cancer Detection System",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (uploaded images, heatmaps) ─────────────
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routes ───────────────────────────────────────────────
app.include_router(api_router)


# ── Health check ─────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
