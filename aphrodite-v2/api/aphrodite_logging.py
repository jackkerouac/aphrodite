"""
Minimal Logging Module

Simple logging replacement for aphrodite_logging to avoid import errors.
"""

import logging
import sys

def setup_logging(environment="development"):
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def get_logger(name, service=None):
    """Get a logger instance"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
    return logger

# Auto-setup on import
setup_logging()
