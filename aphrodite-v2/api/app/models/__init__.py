"""
Models module initialization
"""

# Import all models to ensure they're registered with SQLAlchemy
from .media import MediaItemModel
from .jobs import ProcessingJobModel
from .config import BadgeConfigModel, SystemConfigModel

__all__ = [
    "MediaItemModel",
    "ProcessingJobModel", 
    "BadgeConfigModel",
    "SystemConfigModel"
]
