"""
Analytics Statistics Service - Fixed Version

Provides aggregated statistics using safe SQLAlchemy patterns.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime

from app.models.media_activity import MediaActivityModel


class AnalyticsStatisticsService:
    """Service for aggregated statistics and analytics"""
    
    async def get_aggregated_statistics(
        self,
        search_params: Dict[str, Any],
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get aggregated statistics for the given search criteria.
        
        Provides summary stats without returning individual records.
        """
        try:
            # Build the same filters as in search
            filters = self._build_filters(search_params)
            
            # Get all matching activities and calculate stats manually to avoid SQLAlchemy issues
            query = select(MediaActivityModel)
            if filters:
                query = query.where(and_(*filters))
            
            result = await db_session.execute(query)
            activities = result.scalars().all()
            
            # Calculate basic statistics manually
            total_count = len(activities)
            successful_count = sum(1 for a in activities if a.success is True)
            failed_count = sum(1 for a in activities if a.success is False)
            pending_count = sum(1 for a in activities if a.success is None)
            
            # Performance stats
            processing_times = [a.processing_duration_ms for a in activities if a.processing_duration_ms]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else None
            
            # Scope stats
            unique_users = len(set(a.user_id for a in activities if a.user_id))
            unique_media_items = len(set(a.media_id for a in activities if a.media_id))
            
            # Date range
            created_times = [a.created_at for a in activities if a.created_at]
            earliest_activity = min(created_times) if created_times else None
            latest_activity = max(created_times) if created_times else None
            
            # Activity type breakdown
            type_breakdown = {}
            for activity in activities:
                activity_type = activity.activity_type
                if activity_type not in type_breakdown:
                    type_breakdown[activity_type] = {
                        "total": 0,
                        "successful": 0,
                        "failed": 0
                    }
                
                type_breakdown[activity_type]["total"] += 1
                if activity.success is True:
                    type_breakdown[activity_type]["successful"] += 1
                elif activity.success is False:
                    type_breakdown[activity_type]["failed"] += 1
            
            # Convert to list format
            activity_type_breakdown = [
                {
                    "activity_type": activity_type,
                    "total": stats["total"],
                    "successful": stats["successful"],
                    "failed": stats["failed"],
                    "success_rate": round(stats["successful"] / stats["total"] * 100, 2) if stats["total"] > 0 else 0
                }
                for activity_type, stats in type_breakdown.items()
            ]
            
            return {
                "success": True,
                "statistics": {
                    "totals": {
                        "total_activities": total_count,
                        "successful": successful_count,
                        "failed": failed_count,
                        "pending": pending_count,
                        "success_rate": round(successful_count / total_count * 100, 2) if total_count > 0 else 0
                    },
                    "performance": {
                        "average_processing_time_ms": round(avg_processing_time) if avg_processing_time else None
                    },
                    "scope": {
                        "unique_users": unique_users,
                        "unique_media_items": unique_media_items,
                        "earliest_activity": earliest_activity.isoformat() if earliest_activity else None,
                        "latest_activity": latest_activity.isoformat() if latest_activity else None
                    },
                    "activity_type_breakdown": activity_type_breakdown
                },
                "search_params": search_params
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to calculate statistics: {str(e)}",
                "statistics": {},
                "search_params": search_params
            }
    
    def _build_filters(self, search_params: Dict[str, Any]) -> List:
        """Build filters from search parameters (same logic as advanced search)"""
        filters = []
        
        if search_params.get('activity_types'):
            activity_types = search_params['activity_types']
            if isinstance(activity_types, str):
                activity_types = [activity_types]
            filters.append(MediaActivityModel.activity_type.in_(activity_types))
        
        if search_params.get('statuses'):
            statuses = search_params['statuses']
            if isinstance(statuses, str):
                statuses = [statuses]
            filters.append(MediaActivityModel.status.in_(statuses))
        
        if search_params.get('success') is not None:
            filters.append(MediaActivityModel.success == search_params['success'])
        
        if search_params.get('user_id'):
            filters.append(MediaActivityModel.user_id == search_params['user_id'])
        
        if search_params.get('start_date'):
            try:
                start_date = datetime.fromisoformat(search_params['start_date'].replace('Z', '+00:00'))
                filters.append(MediaActivityModel.created_at >= start_date)
            except ValueError:
                pass
        
        if search_params.get('end_date'):
            try:
                end_date = datetime.fromisoformat(search_params['end_date'].replace('Z', '+00:00'))
                filters.append(MediaActivityModel.created_at <= end_date)
            except ValueError:
                pass
        
        return filters


def get_analytics_statistics_service() -> AnalyticsStatisticsService:
    """Get singleton instance of AnalyticsStatisticsService"""
    if not hasattr(get_analytics_statistics_service, '_instance'):
        get_analytics_statistics_service._instance = AnalyticsStatisticsService()
    return get_analytics_statistics_service._instance
