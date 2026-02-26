"""
Enums and constants used across the application.
"""
from enum import Enum


class CancerType(str, Enum):
    LUNG = "lung"
    BRAIN = "brain"
    BLOOD = "blood"
    BONE = "bone"
    SKIN = "skin"
    BREAST = "breast"


class ScanType(str, Enum):
    CT = "ct"
    MRI = "mri"
    XRAY = "xray"
    PATHOLOGY = "pathology"  # blood slide


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def risk_level_from_score(score: float) -> RiskLevel:
    if score >= 75:
        return RiskLevel.CRITICAL
    elif score >= 50:
        return RiskLevel.HIGH
    elif score >= 25:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


# ── Default class labels per model ───────────────────────
LUNG_CLASSES = ["benign", "malignant"]
BLOOD_CLASSES = ["normal", "leukemia"]
BRAIN_CLASSES = ["no_tumor", "glioma", "meningioma", "pituitary"]
CT_CLASSES = ["normal", "nodule_benign", "nodule_malignant"]
XRAY_CLASSES = ["normal", "abnormal"]

# ── Image input sizes per model ──────────────────────────
MODEL_INPUT_SIZES = {
    CancerType.LUNG: (224, 224),
    CancerType.BRAIN: (224, 224),
    CancerType.BLOOD: (224, 224),
    CancerType.BONE: (224, 224),
    CancerType.SKIN: (224, 224),
    CancerType.BREAST: (224, 224),
}
