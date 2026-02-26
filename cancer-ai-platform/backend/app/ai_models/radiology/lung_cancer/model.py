"""
Lung Cancer model loader and preprocessing.
Loads a PyTorch .pt model for lung cancer classification.
The saved weights are a ResNet50 state_dict with 3-class output.
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


def _build_model(num_classes=len(CLASSES)):
    """Build a ResNet50 with the correct number of output classes."""
    base = models.resnet50(weights=None)
    base.fc = nn.Linear(base.fc.in_features, num_classes)
    return base


def load_model(model_path: str):
    """Load the lung cancer .pt model."""
    global _model
    path = Path(model_path)
    if not path.exists():
        logger.warning(f"Lung model not found at {model_path}. Using pretrained ResNet50 as fallback.")
        _model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        _model.fc = nn.Linear(_model.fc.in_features, len(CLASSES))
        _model.eval()
    else:
        try:
            checkpoint = torch.load(model_path, map_location=_device, weights_only=False)
            if isinstance(checkpoint, dict) and "fc.weight" in checkpoint:
                # It's a state_dict — determine num_classes from fc layer
                num_classes = checkpoint["fc.weight"].shape[0]
                _model = _build_model(num_classes)
                _model.load_state_dict(checkpoint, strict=True)
            elif isinstance(checkpoint, dict):
                # Try loading as state_dict with flexible matching
                _model = _build_model()
                _model.load_state_dict(checkpoint, strict=False)
            else:
                # It's a full model object
                _model = checkpoint
            _model.eval()
            logger.info(f"Lung cancer model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load lung model: {e}. Using fallback.")
            _model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            _model.fc = nn.Linear(_model.fc.in_features, len(CLASSES))
            _model.eval()

    _model.to(_device)
    return _model


def get_model():
    return _model
