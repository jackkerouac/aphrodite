"""
Models module initialization
"""

# Import all models to ensure they're registered with SQLAlchemy
from .media import MediaItemModel
from .jobs import ProcessingJobModel
from .config import BadgeConfigModel, SystemConfigModel
from .schedules import ScheduleModel, ScheduleExecutionModel
from ..services.workflow.database import BatchJobModel, PosterProcessingStatusModel

__all__ = [
    "MediaItemModel",
    "ProcessingJobModel", 
    "BadgeConfigModel",
    "SystemConfigModel",
    "ScheduleModel",
    "ScheduleExecutionModel",
    "BatchJobModel",
    "PosterProcessingStatusModel"
]
