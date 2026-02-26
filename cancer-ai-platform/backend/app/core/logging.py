"""
Structured logging with loguru.
"""
import sys
from loguru import logger

# Remove default handler
logger.remove()

# Console handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# File handler
logger.add(
    "logs/chronoscan_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
)

__all__ = ["logger"]
