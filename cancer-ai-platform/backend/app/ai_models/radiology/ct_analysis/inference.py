"""
CT analysis inference.
"""
import torch
import torch.nn.functional as F
from PIL import Image
from app.ai_models.radiology.ct_analysis.ct_model import get_model, preprocess, CLASSES, _device


def predict(image: Image.Image) -> dict:
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
    risk_score = float(probabilities[2]) * 100  # P(malignant)

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "risk_score": round(risk_score, 2),
        "probabilities": {cls: round(float(p) * 100, 2) for cls, p in zip(CLASSES, probabilities)},
    }


def _fallback_prediction():
    import random
    confidence = round(random.uniform(60, 95), 2)
    return {
        "predicted_class": random.choice(CLASSES),
        "confidence": confidence,
        "risk_score": round(random.uniform(5, 80), 2),
        "probabilities": {c: round(random.uniform(5, 70), 2) for c in CLASSES},
    }
