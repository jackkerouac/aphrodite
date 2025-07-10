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
