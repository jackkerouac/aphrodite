"""
Activity Tracking Migrations Module

Provides database migration utilities for the activity tracking system.
"""

from .badge_applications import BadgeApplicationsMigration

__all__ = ['BadgeApplicationsMigration']
