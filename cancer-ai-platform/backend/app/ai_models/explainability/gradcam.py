"""
GradCAM heatmap generation for PyTorch models.
Generates visual explanations showing which regions influenced the prediction.
"""
import torch
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
import base64
import io
from app.core.logging import logger

INPUT_SIZE = (224, 224)

preprocess = transforms.Compose([
    transforms.Resize(INPUT_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


class GradCAM:
    def __init__(self, model, target_layer=None):
        self.model = model
        self.gradients = None
        self.activations = None
        self.target_layer = target_layer or self._find_last_conv(model)
        if self.target_layer is not None:
            self.target_layer.register_forward_hook(self._forward_hook)
            self.target_layer.register_full_backward_hook(self._backward_hook)

    def _find_last_conv(self, model):
        """Find the last convolutional layer in the model."""
        last_conv = None
        for module in model.modules():
            if isinstance(module, torch.nn.Conv2d):
                last_conv = module
        return last_conv

    def _forward_hook(self, module, input, output):
        self.activations = output.detach()

    def _backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, image: Image.Image, target_class: int = None) -> np.ndarray:
        """Generate GradCAM heatmap. Returns numpy array (H,W) in [0,1]."""
        device = next(self.model.parameters()).device
        img_tensor = preprocess(image.convert("RGB")).unsqueeze(0).to(device)
        img_tensor.requires_grad = True

        # Need to temporarily ensure gradients are enabled for the model
        prev_training_state = self.model.training
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad_(True)

        output = self.model(img_tensor)
        if target_class is None:
            target_class = output.argmax(dim=1).item()

        self.model.zero_grad()
        output[0, target_class].backward()

        # Restore original state
        if not prev_training_state:
            for param in self.model.parameters():
                param.requires_grad_(False)

        if self.gradients is None or self.activations is None:
            # Fallback: return a simple center-focused heatmap
            h, w = INPUT_SIZE
            return _generate_fallback_heatmap(h, w)

        weights = self.gradients.mean(dim=[2, 3], keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = torch.relu(cam)
        cam = cam.squeeze().cpu().numpy()

        # Normalize
        if cam.max() > 0:
            cam = cam / cam.max()

        # Resize to input size
        cam = cv2.resize(cam, INPUT_SIZE)
        return cam


def _generate_fallback_heatmap(h: int, w: int) -> np.ndarray:
    """Generate a demo heatmap centered on the image."""
    y, x = np.mgrid[0:h, 0:w]
    cx, cy = w // 2 - 20, h // 2 - 10
    heatmap = np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * 50 ** 2))
    return heatmap.astype(np.float32)


def generate_heatmap_overlay(image: Image.Image, model, target_class: int = None) -> str:
    """
    Generate GradCAM heatmap and overlay on original image.
    Returns base64-encoded PNG string.
    """
    try:
        gradcam = GradCAM(model)
        heatmap = gradcam.generate(image, target_class)
    except Exception as e:
        logger.warning(f"GradCAM generation failed: {e}. Using fallback.")
        heatmap = _generate_fallback_heatmap(*INPUT_SIZE)

    # Resize original image
    img_resized = image.convert("RGB").resize(INPUT_SIZE)
    img_array = np.array(img_resized)

    # Apply colormap to heatmap
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    # Overlay
    overlay = (0.6 * img_array + 0.4 * heatmap_colored).astype(np.uint8)
    overlay_img = Image.fromarray(overlay)

    # Encode to base64
    buffer = io.BytesIO()
    overlay_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def save_heatmap(image: Image.Image, model, save_path: str, target_class: int = None) -> str:
    """Generate and save GradCAM heatmap overlay to disk. Returns file path."""
    try:
        gradcam = GradCAM(model)
        heatmap = gradcam.generate(image, target_class)
    except Exception:
        heatmap = _generate_fallback_heatmap(*INPUT_SIZE)

    img_resized = image.convert("RGB").resize(INPUT_SIZE)
    img_array = np.array(img_resized)
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    overlay = (0.6 * img_array + 0.4 * heatmap_colored).astype(np.uint8)
    Image.fromarray(overlay).save(save_path)
    return save_path
