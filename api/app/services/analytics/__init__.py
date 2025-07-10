"""
Analytics Services Package

Provides access to all analytics-related services for activity tracking.
"""

from .advanced_search import get_advanced_search_service
from .search_suggestions import get_search_suggestions_service
from .analytics_statistics import get_analytics_statistics_service
from .batch_analytics import get_batch_analytics_service
from .user_analytics import get_user_analytics_service

__all__ = [
    'get_advanced_search_service',
    'get_search_suggestions_service', 
    'get_analytics_statistics_service',
    'get_batch_analytics_service',
    'get_user_analytics_service'
]
