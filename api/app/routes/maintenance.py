"""
FastAPI routes for maintenance operations.
This module is now modularized - importing from the maintenance package.
"""

from .maintenance import router

__all__ = ["router"]
