"""
Lung Cancer model loader and preprocessing.
Loads a PyTorch .pt model for lung cancer classification.
"""
import torch
import torch.nn as nn
from torchvision import transforms, models
from pathlib import Path
from app.core.logging import logger

_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSES = ["benign", "malignant"]
INPUT_SIZE = (224, 224)

preprocess = transforms.Compose([
    transforms.Resize(INPUT_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def load_model(model_path: str):
    """Load the lung cancer .pt model."""
    global _model
    path = Path(model_path)
    if not path.exists():
        logger.warning(f"Lung model not found at {model_path}. Using pretrained DenseNet121 as fallback.")
        _model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
        _model.classifier = nn.Linear(_model.classifier.in_features, len(CLASSES))
        _model.eval()
    else:
        try:
            _model = torch.load(model_path, map_location=_device, weights_only=False)
            if isinstance(_model, dict):
                # If it's a state_dict, build model structure first
                base = models.densenet121(weights=None)
                base.classifier = nn.Linear(base.classifier.in_features, len(CLASSES))
                base.load_state_dict(_model)
                _model = base
            _model.eval()
            logger.info(f"Lung cancer model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load lung model: {e}. Using fallback.")
            _model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
            _model.classifier = nn.Linear(_model.classifier.in_features, len(CLASSES))
            _model.eval()

    _model.to(_device)
    return _model


def get_model():
    return _model
