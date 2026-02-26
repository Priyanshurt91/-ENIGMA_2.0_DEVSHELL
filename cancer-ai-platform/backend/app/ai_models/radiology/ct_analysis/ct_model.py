"""
CT Analysis model loader — PyTorch .pt model.
"""
import torch
import torch.nn as nn
from torchvision import transforms, models
from pathlib import Path
from app.core.logging import logger

_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSES = ["normal", "nodule_benign", "nodule_malignant"]
INPUT_SIZE = (224, 224)

preprocess = transforms.Compose([
    transforms.Resize(INPUT_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def load_model(model_path: str):
    global _model
    path = Path(model_path)
    if not path.exists():
        logger.warning(f"CT model not found at {model_path}. Using fallback.")
        _model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        _model.fc = nn.Linear(_model.fc.in_features, len(CLASSES))
        _model.eval()
    else:
        try:
            _model = torch.load(model_path, map_location=_device, weights_only=False)
            if isinstance(_model, dict):
                base = models.resnet50(weights=None)
                base.fc = nn.Linear(base.fc.in_features, len(CLASSES))
                base.load_state_dict(_model)
                _model = base
            _model.eval()
            logger.info(f"CT model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load CT model: {e}")
            _model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            _model.fc = nn.Linear(_model.fc.in_features, len(CLASSES))
            _model.eval()
    _model.to(_device)
    return _model


def get_model():
    return _model
