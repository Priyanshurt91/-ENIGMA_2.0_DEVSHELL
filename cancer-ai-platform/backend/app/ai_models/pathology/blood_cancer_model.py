"""
Blood Cancer model loader — loads a Keras .h5 model.
"""
import numpy as np
from pathlib import Path
from app.core.logging import logger

_model = None
CLASSES = ["normal", "leukemia"]
INPUT_SIZE = (224, 224)


def load_model(model_path: str):
    """Load the blood cancer .h5 Keras model."""
    global _model
    path = Path(model_path)
    if not path.exists():
        logger.warning(f"Blood cancer model not found at {model_path}. Will use fallback predictions.")
        _model = None
        return None

    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(model_path)
        logger.info(f"Blood cancer model loaded from {model_path}")
        return _model
    except Exception as e:
        logger.error(f"Failed to load blood cancer model: {e}. Using fallback.")
        _model = None
        return None


def preprocess_image(image):
    """Preprocess a PIL Image for the blood cancer model."""
    img = image.convert("RGB").resize(INPUT_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def get_model():
    return _model
