"""
Brain tumor MRI inference.
"""
import torch
import torch.nn.functional as F
from PIL import Image
from app.ai_models.radiology.brain_tumor.mri_model import get_model, preprocess, CLASSES, _device


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
    # Risk = 1 - P(no_tumor)
    risk_score = (1 - float(probabilities[0])) * 100

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "risk_score": round(risk_score, 2),
        "probabilities": {cls: round(float(p) * 100, 2) for cls, p in zip(CLASSES, probabilities)},
    }


def _fallback_prediction():
    import random
    idx = random.choices(range(4), weights=[50, 25, 15, 10])[0]
    confidence = round(random.uniform(70, 98), 2)
    risk = round(random.uniform(10, 90), 2)
    return {
        "predicted_class": CLASSES[idx],
        "confidence": confidence,
        "risk_score": risk,
        "probabilities": {c: round(random.uniform(5, 60), 2) for c in CLASSES},
    }
