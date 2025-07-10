"""
Activity Tracking API Routes

Provides endpoints for viewing media activity history.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.activity_tracking import get_activity_tracker
from app.models.media_activity import MediaActivityModel
from app.models.badge_application import BadgeApplicationModel
from app.models.poster_replacement import PosterReplacementModel
from shared.types import BaseResponse

router = APIRouter()


@router.get("/media/{media_id}/activities")
async def get_media_activity_history(
    media_id: str,
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    include_details: bool = Query(True, description="Include detailed badge application data"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get activity history for a specific media item.
    
    Returns a list of all logged activities for the media item, ordered by creation time.
    When include_details=True, badge applications will include detailed metrics.
    """
    try:
        from sqlalchemy import select, desc
        from sqlalchemy.orm import selectinload
        
        # Build base query
        query = select(MediaActivityModel).where(MediaActivityModel.media_id == media_id)
        
        if activity_type:
            query = query.where(MediaActivityModel.activity_type == activity_type)
        
        # Include detailed data if requested
        if include_details:
            query = query.options(
                selectinload(MediaActivityModel.badge_application),
                selectinload(MediaActivityModel.poster_replacement)
            )
        
        query = query.order_by(desc(MediaActivityModel.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        # Convert to enhanced dict format with details
        activity_list = []
        for activity in activities:
            activity_dict = activity.to_dict()
            
            # Add detailed data if available and requested
            if include_details:
                if activity.activity_type == 'badge_application' and activity.badge_application:
                    activity_dict['badge_details'] = activity.badge_application.to_dict()
                elif activity.activity_type == 'poster_replacement' and activity.poster_replacement:
                    activity_dict['replacement_details'] = activity.poster_replacement.to_dict()
            
            activity_list.append(activity_dict)
        
        return {
            "success": True,
            "message": f"Retrieved {len(activity_list)} activities for media {media_id}",
            "data": {
                "media_id": media_id,
                "activities": activity_list,
                "total_returned": len(activity_list),
                "offset": offset,
                "limit": limit,
                "include_details": include_details,
                "filter": {"activity_type": activity_type} if activity_type else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve activity history: {str(e)}"
        )


@router.get("/activities/summary")
async def get_activity_summary(
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of recent activities"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a summary of recent activities across all media items.
    
    Useful for monitoring system activity and troubleshooting.
    """
    try:
        # This would require a more complex query, for now we'll implement a basic version
        from sqlalchemy import select, func, desc
        from app.models.media_activity import MediaActivityModel
        
        # Build query
        query = select(MediaActivityModel)
        
        if activity_type:
            query = query.where(MediaActivityModel.activity_type == activity_type)
        
        query = query.order_by(desc(MediaActivityModel.created_at)).limit(limit)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        # Convert to dict format
        activity_list = [activity.to_dict() for activity in activities]
        
        # Calculate summary statistics
        total_activities = len(activity_list)
        successful = sum(1 for a in activity_list if a.get('success') is True)
        failed = sum(1 for a in activity_list if a.get('success') is False)
        pending = sum(1 for a in activity_list if a.get('success') is None)
        
        return {
            "success": True,
            "message": f"Retrieved {total_activities} recent activities",
            "data": {
                "summary": {
                    "total_activities": total_activities,
                    "successful": successful,
                    "failed": failed,
                    "pending": pending
                },
                "recent_activities": activity_list,
                "filter": {"activity_type": activity_type} if activity_type else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve activity summary: {str(e)}"
        )


@router.get("/activities/types")
async def get_activity_types(db: AsyncSession = Depends(get_db_session)):
    """
    Get list of all activity types that have been logged.
    
    Useful for filtering and understanding what types of activities are tracked.
    """
    try:
        from sqlalchemy import select, distinct
        from app.models.media_activity import MediaActivityModel
        
        query = select(distinct(MediaActivityModel.activity_type)).where(
            MediaActivityModel.activity_type.isnot(None)
        )
        
        result = await db.execute(query)
        activity_types = [row[0] for row in result.fetchall()]
        
        return {
            "success": True,
            "message": f"Found {len(activity_types)} different activity types",
            "data": {
                "activity_types": sorted(activity_types),
                "count": len(activity_types)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve activity types: {str(e)}"
        )


@router.get("/activities/{activity_id}/badge_details")
async def get_badge_application_details(
    activity_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed badge application data for a specific activity.
    
    Returns comprehensive metrics including performance data, applied badges,
    failed badges, and quality metrics.
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Query for the activity with badge application details
        query = select(MediaActivityModel).where(
            MediaActivityModel.id == activity_id
        ).options(selectinload(MediaActivityModel.badge_application))
        
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=404,
                detail=f"Activity {activity_id} not found"
            )
        
        if activity.activity_type != 'badge_application':
            raise HTTPException(
                status_code=400,
                detail=f"Activity {activity_id} is not a badge application (type: {activity.activity_type})"
            )
        
        # Build response
        response_data = {
            "activity": activity.to_dict()
        }
        
        if activity.badge_application:
            response_data["badge_details"] = activity.badge_application.to_dict()
        else:
            response_data["badge_details"] = None
            response_data["warning"] = "No detailed badge application data available for this activity"
        
        return {
            "success": True,
            "message": f"Retrieved badge application details for activity {activity_id}",
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve badge application details: {str(e)}"
        )


@router.get("/activities/{activity_id}/replacement_details")
async def get_poster_replacement_details(
    activity_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed poster replacement data for a specific activity.
    
    Returns comprehensive metrics including source information, download/upload times,
    Jellyfin integration details, and quality assessments.
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Query for the activity with poster replacement details
        query = select(MediaActivityModel).where(
            MediaActivityModel.id == activity_id
        ).options(selectinload(MediaActivityModel.poster_replacement))
        
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=404,
                detail=f"Activity {activity_id} not found"
            )
        
        if activity.activity_type != 'poster_replacement':
            raise HTTPException(
                status_code=400,
                detail=f"Activity {activity_id} is not a poster replacement (type: {activity.activity_type})"
            )
        
        # Build response
        response_data = {
            "activity": activity.to_dict()
        }
        
        if activity.poster_replacement:
            response_data["replacement_details"] = activity.poster_replacement.to_dict()
        else:
            response_data["replacement_details"] = None
            response_data["warning"] = "No detailed poster replacement data available for this activity"
        
        return {
            "success": True,
            "message": f"Retrieved poster replacement details for activity {activity_id}",
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve poster replacement details: {str(e)}"
        )


@router.get("/activities/{activity_id}/performance_metrics")
async def get_activity_performance_metrics(
    activity_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed performance metrics for a specific activity.
    
    Returns comprehensive system performance data including CPU, memory, disk I/O,
    network usage, and processing stage breakdowns.
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.activity_performance_metric import ActivityPerformanceMetricModel
        
        # Query for the activity with performance metrics
        query = select(MediaActivityModel).where(
            MediaActivityModel.id == activity_id
        ).options(selectinload(MediaActivityModel.performance_metrics))
        
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=404,
                detail=f"Activity {activity_id} not found"
            )
        
        # Also query performance metrics directly (in case relationship isn't set up)
        metrics_query = select(ActivityPerformanceMetricModel).where(
            ActivityPerformanceMetricModel.activity_id == activity_id
        )
        metrics_result = await db.execute(metrics_query)
        performance_metrics = metrics_result.scalar_one_or_none()
        
        # Build response
        response_data = {
            "activity": activity.to_dict()
        }
        
        if performance_metrics:
            response_data["performance_metrics"] = performance_metrics.to_dict()
        else:
            response_data["performance_metrics"] = None
            response_data["warning"] = "No performance metrics data available for this activity"
        
        return {
            "success": True,
            "message": f"Retrieved performance metrics for activity {activity_id}",
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve performance metrics: {str(e)}"
        )


@router.get("/analytics/performance")
async def get_performance_analytics(
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    activity_subtype: Optional[str] = Query(None, description="Filter by activity subtype"),
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get aggregated performance analytics across activities.
    
    Provides insights into system performance trends, averages, and bottlenecks.
    """
    try:
        from sqlalchemy import select, func, and_
        from app.models.activity_performance_metric import ActivityPerformanceMetricModel
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build base query joining activities and performance metrics
        query = select(
            MediaActivityModel.activity_type,
            MediaActivityModel.activity_subtype,
            func.count(ActivityPerformanceMetricModel.id).label('total_activities'),
            func.avg(ActivityPerformanceMetricModel.cpu_usage_percent).label('avg_cpu'),
            func.max(ActivityPerformanceMetricModel.cpu_usage_percent).label('max_cpu'),
            func.avg(ActivityPerformanceMetricModel.memory_usage_mb).label('avg_memory'),
            func.max(ActivityPerformanceMetricModel.memory_usage_mb).label('max_memory'),
            func.avg(ActivityPerformanceMetricModel.disk_io_read_mb).label('avg_disk_read'),
            func.avg(ActivityPerformanceMetricModel.disk_io_write_mb).label('avg_disk_write'),
            func.avg(ActivityPerformanceMetricModel.network_download_mb).label('avg_network_download'),
            func.avg(ActivityPerformanceMetricModel.network_upload_mb).label('avg_network_upload'),
            func.avg(ActivityPerformanceMetricModel.throughput_items_per_second).label('avg_throughput'),
            func.avg(ActivityPerformanceMetricModel.server_load_average).label('avg_load')
        ).select_from(
            MediaActivityModel.__table__.join(
                ActivityPerformanceMetricModel.__table__,
                MediaActivityModel.id == ActivityPerformanceMetricModel.activity_id
            )
        ).where(
            MediaActivityModel.created_at >= start_date
        )
        
        # Apply filters
        if activity_type:
            query = query.where(MediaActivityModel.activity_type == activity_type)
        if activity_subtype:
            query = query.where(MediaActivityModel.activity_subtype == activity_subtype)
        
        # Group by activity type and subtype
        query = query.group_by(
            MediaActivityModel.activity_type,
            MediaActivityModel.activity_subtype
        )
        
        result = await db.execute(query)
        analytics_data = result.fetchall()
        
        # Convert to dict format
        performance_summary = []
        for row in analytics_data:
            summary = {
                'activity_type': row.activity_type,
                'activity_subtype': row.activity_subtype,
                'total_activities': row.total_activities,
                'avg_cpu_percent': float(row.avg_cpu) if row.avg_cpu else None,
                'max_cpu_percent': float(row.max_cpu) if row.max_cpu else None,
                'avg_memory_mb': float(row.avg_memory) if row.avg_memory else None,
                'max_memory_mb': float(row.max_memory) if row.max_memory else None,
                'avg_disk_read_mb': float(row.avg_disk_read) if row.avg_disk_read else None,
                'avg_disk_write_mb': float(row.avg_disk_write) if row.avg_disk_write else None,
                'avg_network_download_mb': float(row.avg_network_download) if row.avg_network_download else None,
                'avg_network_upload_mb': float(row.avg_network_upload) if row.avg_network_upload else None,
                'avg_throughput_items_per_second': float(row.avg_throughput) if row.avg_throughput else None,
                'avg_server_load': float(row.avg_load) if row.avg_load else None
            }
            performance_summary.append(summary)
        
        # Get bottleneck analysis
        bottleneck_query = select(
            ActivityPerformanceMetricModel.bottleneck_stage,
            func.count(ActivityPerformanceMetricModel.id).label('frequency')
        ).select_from(
            MediaActivityModel.__table__.join(
                ActivityPerformanceMetricModel.__table__,
                MediaActivityModel.id == ActivityPerformanceMetricModel.activity_id
            )
        ).where(
            and_(
                MediaActivityModel.created_at >= start_date,
                ActivityPerformanceMetricModel.bottleneck_stage.isnot(None)
            )
        )
        
        if activity_type:
            bottleneck_query = bottleneck_query.where(MediaActivityModel.activity_type == activity_type)
        
        bottleneck_query = bottleneck_query.group_by(
            ActivityPerformanceMetricModel.bottleneck_stage
        ).order_by(func.count(ActivityPerformanceMetricModel.id).desc())
        
        bottleneck_result = await db.execute(bottleneck_query)
        bottlenecks = [{
            'stage': row.bottleneck_stage,
            'frequency': row.frequency
        } for row in bottleneck_result.fetchall()]
        
        return {
            "success": True,
            "message": f"Retrieved performance analytics for {days} days",
            "data": {
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "filters": {
                    "activity_type": activity_type,
                    "activity_subtype": activity_subtype
                },
                "performance_summary": performance_summary,
                "bottleneck_analysis": bottlenecks,
                "total_activity_types": len(performance_summary)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve performance analytics: {str(e)}"
        )
