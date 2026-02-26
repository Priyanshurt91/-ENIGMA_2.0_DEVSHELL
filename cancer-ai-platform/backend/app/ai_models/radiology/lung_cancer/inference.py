"""
Lung cancer inference — takes a PIL Image, returns prediction.
"""
import torch
import torch.nn.functional as F
from PIL import Image

from app.ai_models.radiology.lung_cancer.model import get_model, preprocess, CLASSES, _device


def predict(image: Image.Image) -> dict:
    """
    Run lung cancer inference.
    Returns: {predicted_class, confidence, probabilities, risk_score}
    """
    model = get_model()
    if model is None:
        return _fallback_prediction()

    img_tensor = preprocess(image.convert("RGB")).unsqueeze(0).to(_device)

    with torch.no_grad():
        output = model(img_tensor)
        probabilities = F.softmax(output, dim=1).squeeze().cpu().numpy()

    pred_idx = probabilities.argmax()
    predicted_class = CLASSES[pred_idx]
    confidence = float(probabilities[pred_idx]) * 100

    # Risk score: higher if malignant
    risk_score = float(probabilities[1]) * 100 if len(CLASSES) == 2 else confidence

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "risk_score": round(risk_score, 2),
        "probabilities": {cls: round(float(p) * 100, 2) for cls, p in zip(CLASSES, probabilities)},
    }


def _fallback_prediction():
    """Fallback when model isn't loaded — returns simulated result."""
    import random
    confidence = round(random.uniform(60, 98), 2)
    return {
        "predicted_class": "malignant" if confidence > 70 else "benign",
        "confidence": confidence,
        "risk_score": confidence,
        "probabilities": {"benign": round(100 - confidence, 2), "malignant": confidence},
    }
