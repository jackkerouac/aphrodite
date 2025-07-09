"""
Activity Tracking API Routes

Provides endpoints for viewing media activity history.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.activity_tracking import get_activity_tracker
from shared.types import BaseResponse

router = APIRouter()


@router.get("/media/{media_id}/activities")
async def get_media_activity_history(
    media_id: str,
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get activity history for a specific media item.
    
    Returns a list of all logged activities for the media item, ordered by creation time.
    """
    try:
        activity_tracker = get_activity_tracker()
        
        activities = await activity_tracker.get_activity_history(
            media_id=media_id,
            limit=limit,
            offset=offset,
            activity_type=activity_type,
            db_session=db
        )
        
        return {
            "success": True,
            "message": f"Retrieved {len(activities)} activities for media {media_id}",
            "data": {
                "media_id": media_id,
                "activities": activities,
                "total_returned": len(activities),
                "offset": offset,
                "limit": limit,
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
