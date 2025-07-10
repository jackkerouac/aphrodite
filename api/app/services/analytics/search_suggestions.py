"""
Search Suggestions Service

Provides search parameter suggestions and data exploration capabilities.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.media_activity import MediaActivityModel


class SearchSuggestionsService:
    """Service for providing search suggestions and metadata"""
    
    async def get_search_suggestions(self, db_session: AsyncSession) -> Dict[str, Any]:
        """
        Get suggestions for search parameters based on existing data.
        
        Returns available values for various filter fields.
        """
        try:
            # Get available activity types
            activity_types = await self._get_distinct_values(
                db_session, MediaActivityModel.activity_type
            )
            
            # Get available statuses
            statuses = await self._get_distinct_values(
                db_session, MediaActivityModel.status
            )
            
            # Get available initiated_by values
            initiated_by = await self._get_distinct_values(
                db_session, MediaActivityModel.initiated_by
            )
            
            # Get available user IDs (last 50 active users)
            user_ids = await self._get_distinct_values(
                db_session, MediaActivityModel.user_id, limit=50
            )
            
            # Get date range of available data
            date_range = await self._get_date_range(db_session)
            
            return {
                "success": True,
                "suggestions": {
                    "activity_types": sorted(activity_types),
                    "statuses": sorted(statuses),
                    "initiated_by": sorted(initiated_by),
                    "user_ids": sorted(user_ids)[:20],  # Limit to 20 most recent
                    "date_range": date_range,
                    "sort_options": [
                        {"value": "created_at", "label": "Creation Time"},
                        {"value": "processing_duration_ms", "label": "Processing Duration"},
                        {"value": "activity_type", "label": "Activity Type"},
                        {"value": "status", "label": "Status"}
                    ],
                    "sort_orders": [
                        {"value": "desc", "label": "Descending (Newest First)"},
                        {"value": "asc", "label": "Ascending (Oldest First)"}
                    ]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get search suggestions: {str(e)}",
                "suggestions": {}
            }
    
    async def _get_distinct_values(
        self, 
        db_session: AsyncSession, 
        column, 
        limit: Optional[int] = None
    ) -> List[str]:
        """Get distinct values for a column"""
        query = select(column.distinct()).where(column.isnot(None))
        if limit:
            query = query.limit(limit)
        
        result = await db_session.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def _get_date_range(self, db_session: AsyncSession) -> Dict[str, Optional[str]]:
        """Get the date range of available activity data"""
        query = select(
            func.min(MediaActivityModel.created_at).label('earliest'),
            func.max(MediaActivityModel.created_at).label('latest')
        )
        
        result = await db_session.execute(query)
        date_range = result.fetchone()
        
        return {
            "earliest": date_range.earliest.isoformat() if date_range.earliest else None,
            "latest": date_range.latest.isoformat() if date_range.latest else None
        }


def get_search_suggestions_service() -> SearchSuggestionsService:
    """Get singleton instance of SearchSuggestionsService"""
    if not hasattr(get_search_suggestions_service, '_instance'):
        get_search_suggestions_service._instance = SearchSuggestionsService()
    return get_search_suggestions_service._instance
