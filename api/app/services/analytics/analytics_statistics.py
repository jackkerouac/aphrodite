"""
Analytics Statistics Service

Provides aggregated statistics and analysis capabilities for activity tracking data.
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
            
            # Get basic statistics
            stats = await self._get_basic_statistics(db_session, filters)
            
            # Get activity type breakdown
            type_breakdown = await self._get_activity_type_breakdown(db_session, filters)
            
            # Format results
            total_count = stats.total_count or 0
            successful_count = stats.successful_count or 0
            failed_count = stats.failed_count or 0
            pending_count = stats.pending_count or 0
            
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
                        "average_processing_time_ms": round(float(stats.avg_processing_time)) if stats.avg_processing_time else None
                    },
                    "scope": {
                        "unique_users": stats.unique_users or 0,
                        "unique_media_items": stats.unique_media_items or 0,
                        "earliest_activity": stats.earliest_activity.isoformat() if stats.earliest_activity else None,
                        "latest_activity": stats.latest_activity.isoformat() if stats.latest_activity else None
                    },
                    "activity_type_breakdown": [
                        {
                            "activity_type": row.activity_type,
                            "total": row.count,
                            "successful": row.successful or 0,
                            "failed": row.failed or 0,
                            "success_rate": round((row.successful or 0) / row.count * 100, 2) if row.count > 0 else 0
                        }
                        for row in type_breakdown
                    ]
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
    
    async def _get_basic_statistics(self, db_session: AsyncSession, filters: List):
        """Get basic aggregated statistics"""
        stats_query = select(
            func.count(MediaActivityModel.id).label('total_count'),
            func.sum(func.case([(MediaActivityModel.success == True, 1)], else_=0)).label('successful_count'),
            func.sum(func.case([(MediaActivityModel.success == False, 1)], else_=0)).label('failed_count'),
            func.sum(func.case([(MediaActivityModel.success.is_(None), 1)], else_=0)).label('pending_count'),
            func.avg(MediaActivityModel.processing_duration_ms).label('avg_processing_time'),
            func.min(MediaActivityModel.created_at).label('earliest_activity'),
            func.max(MediaActivityModel.created_at).label('latest_activity'),
            func.count(MediaActivityModel.user_id.distinct()).label('unique_users'),
            func.count(MediaActivityModel.media_id.distinct()).label('unique_media_items')
        )
        
        if filters:
            stats_query = stats_query.where(and_(*filters))
        
        result = await db_session.execute(stats_query)
        return result.fetchone()
    
    async def _get_activity_type_breakdown(self, db_session: AsyncSession, filters: List):
        """Get breakdown by activity type"""
        type_breakdown_query = select(
            MediaActivityModel.activity_type,
            func.count(MediaActivityModel.id).label('count'),
            func.sum(func.case([(MediaActivityModel.success == True, 1)], else_=0)).label('successful'),
            func.sum(func.case([(MediaActivityModel.success == False, 1)], else_=0)).label('failed')
        )
        
        if filters:
            type_breakdown_query = type_breakdown_query.where(and_(*filters))
        
        type_breakdown_query = type_breakdown_query.group_by(MediaActivityModel.activity_type)
        result = await db_session.execute(type_breakdown_query)
        return result.fetchall()


def get_analytics_statistics_service() -> AnalyticsStatisticsService:
    """Get singleton instance of AnalyticsStatisticsService"""
    if not hasattr(get_analytics_statistics_service, '_instance'):
        get_analytics_statistics_service._instance = AnalyticsStatisticsService()
    return get_analytics_statistics_service._instance
