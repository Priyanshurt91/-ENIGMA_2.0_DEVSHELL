"""
Blood Cancer model loader — loads a Keras .h5 model.
Configures TensorFlow GPU memory growth to coexist with PyTorch.
"""
import numpy as np
from pathlib import Path
from app.core.logging import logger

_model = None
CLASSES = ["normal", "leukemia"]
INPUT_SIZE = (224, 224)


def _configure_tf_gpu():
    """Configure TensorFlow to use GPU with memory growth (prevents hogging all VRAM)."""
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logger.info(f"TensorFlow GPU configured with memory growth: {[g.name for g in gpus]}")
        else:
            logger.info("TensorFlow: No GPU detected, using CPU.")
    except Exception as e:
        logger.warning(f"TensorFlow GPU config failed: {e}")


def load_model(model_path: str):
    """Load the blood cancer .h5 Keras model."""
    global _model

    # Configure GPU before loading
    _configure_tf_gpu()

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
