"""
Advanced Search Service - Core Search Functions

Provides powerful, flexible search capabilities for activity tracking data.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, asc, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.media_activity import MediaActivityModel


class AdvancedSearchService:
    """Service for complex activity search and filtering"""
    
    async def search_activities(
        self,
        search_params: Dict[str, Any],
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Perform advanced search on activity data with complex filtering.
        """
        try:
            # Build base query
            query = select(MediaActivityModel)
            
            # Apply filters
            filters = self._build_filters(search_params)
            if filters:
                query = query.where(and_(*filters))
            
            # Include detailed data if requested
            include_details = search_params.get('include_details', False)
            if include_details:
                query = query.options(
                    selectinload(MediaActivityModel.badge_application),
                    selectinload(MediaActivityModel.poster_replacement),
                    selectinload(MediaActivityModel.performance_metrics)
                )
            
            # Apply sorting
            query = self._apply_sorting(query, search_params)
            
            # Get total count for pagination
            count_query = select(func.count(MediaActivityModel.id))
            if filters:
                count_query = count_query.where(and_(*filters))
            
            count_result = await db_session.execute(count_query)
            total_count = count_result.scalar()
            
            # Apply pagination
            limit = min(search_params.get('limit', 50), 500)  # Max 500 results
            offset = max(search_params.get('offset', 0), 0)
            query = query.limit(limit).offset(offset)
            
            # Execute query
            result = await db_session.execute(query)
            activities = result.scalars().all()
            
            # Convert to enhanced dict format
            activity_list = self._format_activity_results(activities, include_details)
            
            # Calculate pagination info
            has_next = (offset + len(activity_list)) < total_count
            has_prev = offset > 0
            
            return {
                "success": True,
                "message": f"Found {len(activity_list)} activities (total: {total_count})",
                "data": {
                    "activities": activity_list,
                    "pagination": {
                        "total_count": total_count,
                        "returned_count": len(activity_list),
                        "limit": limit,
                        "offset": offset,
                        "has_next": has_next,
                        "has_prev": has_prev,
                        "total_pages": (total_count + limit - 1) // limit if limit > 0 else 0,
                        "current_page": (offset // limit) + 1 if limit > 0 else 1
                    },
                    "search_params": search_params,
                    "filters_applied": len(filters)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "data": {
                    "activities": [],
                    "search_params": search_params
                }
            }
    
    def _build_filters(self, search_params: Dict[str, Any]) -> List:
        """Build SQLAlchemy filters from search parameters"""
        filters = []
        
        # Activity type filters
        if search_params.get('activity_types'):
            activity_types = search_params['activity_types']
            if isinstance(activity_types, str):
                activity_types = [activity_types]
            filters.append(MediaActivityModel.activity_type.in_(activity_types))
        
        # Status filters
        if search_params.get('statuses'):
            statuses = search_params['statuses']
            if isinstance(statuses, str):
                statuses = [statuses]
            filters.append(MediaActivityModel.status.in_(statuses))
        
        # Success/failure filter
        if search_params.get('success') is not None:
            filters.append(MediaActivityModel.success == search_params['success'])
        
        # Initiated by filters
        if search_params.get('initiated_by'):
            initiated_by = search_params['initiated_by']
            if isinstance(initiated_by, str):
                initiated_by = [initiated_by]
            filters.append(MediaActivityModel.initiated_by.in_(initiated_by))
        
        # User ID filter
        if search_params.get('user_id'):
            filters.append(MediaActivityModel.user_id == search_params['user_id'])
        
        # Batch job ID filter
        if search_params.get('batch_job_id'):
            filters.append(MediaActivityModel.batch_job_id == search_params['batch_job_id'])
        
        # Media ID filter
        if search_params.get('media_id'):
            filters.append(MediaActivityModel.media_id == search_params['media_id'])
        
        # Date range filters
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
        
        # Error message text search
        if search_params.get('error_text'):
            error_text = search_params['error_text']
            filters.append(MediaActivityModel.error_message.ilike(f'%{error_text}%'))
        
        # Processing duration filters
        if search_params.get('min_processing_time_ms'):
            filters.append(MediaActivityModel.processing_duration_ms >= search_params['min_processing_time_ms'])
        
        if search_params.get('max_processing_time_ms'):
            filters.append(MediaActivityModel.processing_duration_ms <= search_params['max_processing_time_ms'])
        
        return filters
    
    def _apply_sorting(self, query, search_params: Dict[str, Any]):
        """Apply sorting to query based on search parameters"""
        sort_by = search_params.get('sort_by', 'created_at')
        sort_order = search_params.get('sort_order', 'desc')
        
        if hasattr(MediaActivityModel, sort_by):
            sort_column = getattr(MediaActivityModel, sort_by)
            if sort_order.lower() == 'asc':
                return query.order_by(asc(sort_column))
            else:
                return query.order_by(desc(sort_column))
        else:
            # Default sorting
            return query.order_by(desc(MediaActivityModel.created_at))
    
    def _format_activity_results(self, activities, include_details: bool) -> List[Dict]:
        """Format activity results with optional detailed data"""
        activity_list = []
        for activity in activities:
            activity_dict = activity.to_dict()
            
            # Add detailed data if available and requested
            if include_details:
                if activity.activity_type == 'badge_application' and activity.badge_application:
                    activity_dict['badge_details'] = activity.badge_application.to_dict()
                elif activity.activity_type == 'poster_replacement' and activity.poster_replacement:
                    activity_dict['replacement_details'] = activity.poster_replacement.to_dict()
                
                if activity.performance_metrics:
                    activity_dict['performance_metrics'] = activity.performance_metrics.to_dict()
            
            activity_list.append(activity_dict)
        
        return activity_list


def get_advanced_search_service() -> AdvancedSearchService:
    """Get singleton instance of AdvancedSearchService"""
    if not hasattr(get_advanced_search_service, '_instance'):
        get_advanced_search_service._instance = AdvancedSearchService()
    return get_advanced_search_service._instance
