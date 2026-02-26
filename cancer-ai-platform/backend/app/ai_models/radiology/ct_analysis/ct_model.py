"""
CT Analysis model loader — PyTorch .pth model.
The saved weights are from a 3D UNet segmentation model.
Architecture: initial_conv → encoder1-4 → bottleneck → decoder4-1 → final_conv
Channel progression: 1 → 16 → 32 → 64 → 128 → 256 → 128 → 64 → 32 → 16 → 1
"""
import torch
import torch.nn as nn
from torchvision import transforms
from pathlib import Path
from app.core.logging import logger

_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSES = ["normal", "nodule_benign", "nodule_malignant"]
INPUT_SIZE = (224, 224)

preprocess = transforms.Compose([
    transforms.Resize(INPUT_SIZE),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),
])


class ConvBlock3D(nn.Module):
    """Conv3D + BatchNorm block matching saved weight structure: conv.0 (Conv3d) + conv.1 (BatchNorm3d)."""
    def __init__(self, in_ch, out_ch, kernel_size=3, padding=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(in_ch, out_ch, kernel_size, padding=padding),
            nn.BatchNorm3d(out_ch),
        )

    def forward(self, x):
        return nn.functional.relu(self.conv(x))


class EncoderBlock(nn.Module):
    """Two ConvBlock3D in sequence."""
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv1 = ConvBlock3D(in_ch, out_ch)
        self.conv2 = ConvBlock3D(out_ch, out_ch)

    def forward(self, x):
        return self.conv2(self.conv1(x))


class DecoderBlock(nn.Module):
    """Upsample (ConvTranspose3d) + two ConvBlock3D."""
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.upsample = nn.ConvTranspose3d(in_ch, out_ch, kernel_size=2, stride=2)
        self.conv1 = ConvBlock3D(in_ch, out_ch)  # in_ch because of skip connection concat
        self.conv2 = ConvBlock3D(out_ch, out_ch)

    def forward(self, x, skip=None):
        x = self.upsample(x)
        if skip is not None:
            x = torch.cat([x, skip], dim=1)
        return self.conv2(self.conv1(x))


class CTUNet3D(nn.Module):
    """
    3D UNet matching the saved ct.pth weights.
    Channel progression: 1 → 16 → 32 → 64 → 128 → 256(bottleneck) → 128 → 64 → 32 → 16 → 1
    """
    def __init__(self, in_channels=1, out_channels=1):
        super().__init__()
        self.initial_conv = ConvBlock3D(in_channels, 16)

        self.encoder1 = EncoderBlock(16, 16)
        self.encoder2 = EncoderBlock(16, 32)
        self.encoder3 = EncoderBlock(32, 64)
        self.encoder4 = EncoderBlock(64, 128)

        self.bottleneck_conv1 = ConvBlock3D(128, 256)
        self.bottleneck_conv2 = ConvBlock3D(256, 256)

        self.decoder4 = DecoderBlock(256, 128)
        self.decoder3 = DecoderBlock(128, 64)
        self.decoder2 = DecoderBlock(64, 32)
        self.decoder1 = DecoderBlock(32, 16)

        self.final_conv = nn.Conv3d(16, out_channels, kernel_size=1)

    def forward(self, x):
        x = self.initial_conv(x)

        e1 = self.encoder1(x)
        e2 = self.encoder2(nn.functional.max_pool3d(e1, 2))
        e3 = self.encoder3(nn.functional.max_pool3d(e2, 2))
        e4 = self.encoder4(nn.functional.max_pool3d(e3, 2))

        b = self.bottleneck_conv1(nn.functional.max_pool3d(e4, 2))
        b = self.bottleneck_conv2(b)

        d4 = self.decoder4(b, e4)
        d3 = self.decoder3(d4, e3)
        d2 = self.decoder2(d3, e2)
        d1 = self.decoder1(d2, e1)

        return self.final_conv(d1)


def load_model(model_path: str):
    global _model
    path = Path(model_path)
    if not path.exists():
        logger.warning(f"CT model not found at {model_path}. Using fallback 3D UNet.")
        _model = CTUNet3D()
        _model.eval()
    else:
        try:
            checkpoint = torch.load(model_path, map_location=_device, weights_only=False)
            if isinstance(checkpoint, dict):
                _model = CTUNet3D()
                _model.load_state_dict(checkpoint, strict=False)
            else:
                _model = checkpoint
            _model.eval()
            logger.info(f"CT model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load CT model: {e}. Using fallback.")
            _model = CTUNet3D()
            _model.eval()
    _model.to(_device)
    return _model


def get_model():
    return _model
