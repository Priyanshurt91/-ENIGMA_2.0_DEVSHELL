"""
Brain Tumor MRI model loader — PyTorch .pth model.
The saved weights are from a MONAI BasicUNet (2D segmentation).
We load the segmentation model and extract classification-like
results by analyzing the output mask.
"""
import torch
import torch.nn as nn
from torchvision import transforms
from pathlib import Path
from app.core.logging import logger

_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSES = ["no_tumor", "glioma", "meningioma", "pituitary"]
INPUT_SIZE = (224, 224)

preprocess = transforms.Compose([
    transforms.Resize(INPUT_SIZE),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),
])


class BasicUNetBlock(nn.Module):
    """A simple 2D conv block used in the BasicUNet (matching MONAI's structure)."""
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, 3, padding=1)
        self.adn = nn.ModuleDict({"A": nn.PReLU(1)})

    def forward(self, x):
        return self.adn["A"](self.conv(x))


class BrainBasicUNet(nn.Module):
    """
    Matches the MONAI BasicUNet architecture from the saved weights.
    Structure: model.0 (down_conv) → model.1 (nested submodule chain) → model.2 (final conv)
    Channel progression: 1 → 16 → 32 → 64 → 128 → back up → 1 output
    """
    def __init__(self, in_channels=1, out_channels=1, features=(16, 32, 64, 128)):
        super().__init__()
        # Build the nested UNet structure matching MONAI's BasicUNet
        # model.0: initial conv (in_ch → features[0])
        self.model = nn.ModuleList()

        # model.0: first conv block
        self.model.append(BasicUNetBlock(in_channels, features[0]))

        # model.1: nested submodule (encoder-decoder chain)
        # Build from the bottom up
        inner = BasicUNetBlock(features[-1], features[-1])  # bottleneck
        for i in range(len(features) - 1, 0, -1):
            down = BasicUNetBlock(features[i-1], features[i])
            up = BasicUNetBlock(features[i], features[i-1])
            inner = _NestedBlock(down, inner, up)

        self.model.append(inner)

        # model.2: final conv
        self.model.append(nn.Sequential(
            nn.Conv2d(features[0], out_channels, 3, padding=1)
        ))

    def forward(self, x):
        x = self.model[0](x)
        x = self.model[1](x)
        x = self.model[2](x)
        return x


class _NestedBlock(nn.Module):
    """Nested down → submodule → up block matching MONAI structure."""
    def __init__(self, down_conv, submodule, up_conv):
        super().__init__()
        self.submodule = nn.ModuleList([down_conv, submodule, up_conv])

    def forward(self, x):
        d = self.submodule[0](x)
        d = nn.functional.max_pool2d(d, 2)
        d = self.submodule[1](d)
        d = nn.functional.interpolate(d, scale_factor=2, mode='bilinear', align_corners=True)
        d = self.submodule[2](d)
        return d


def load_model(model_path: str):
    global _model
    path = Path(model_path)
    if not path.exists():
        logger.warning(f"Brain MRI model not found at {model_path}. Using fallback UNet.")
        _model = BrainBasicUNet()
        _model.eval()
    else:
        try:
            checkpoint = torch.load(model_path, map_location=_device, weights_only=False)
            if isinstance(checkpoint, dict):
                _model = BrainBasicUNet()
                _model.load_state_dict(checkpoint, strict=False)
            else:
                _model = checkpoint
            _model.eval()
            logger.info(f"Brain MRI model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load brain model: {e}. Using fallback.")
            _model = BrainBasicUNet()
            _model.eval()
    _model.to(_device)
    return _model


def get_model():
    return _model
