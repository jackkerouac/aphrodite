"""
Advanced Analytics API Routes

Provides Phase 6 advanced analytics endpoints including batch analytics,
user analytics, advanced search, and comprehensive system insights.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.analytics import (
    get_advanced_search_service,
    get_search_suggestions_service,
    get_analytics_statistics_service,
    get_batch_analytics_service,
    get_user_analytics_service
)

router = APIRouter()


@router.post("/activities/search")
async def advanced_activity_search(
    search_params: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Advanced search for activities with complex filtering.
    
    Supports multiple filters, sorting, pagination, and detailed data inclusion.
    """
    try:
        search_service = get_advanced_search_service()
        result = await search_service.search_activities(search_params, db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Advanced search failed: {str(e)}"
        )


@router.get("/activities/search/suggestions")
async def get_search_suggestions(db: AsyncSession = Depends(get_db_session)):
    """
    Get suggestions for search parameters based on existing data.
    
    Returns available values for filters, sort options, and date ranges.
    """
    try:
        suggestions_service = get_search_suggestions_service()
        result = await suggestions_service.get_search_suggestions(db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get search suggestions: {str(e)}"
        )


@router.post("/activities/statistics")
async def get_activity_statistics(
    search_params: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get aggregated statistics for activities matching search criteria.
    
    Provides summary stats without returning individual records.
    """
    try:
        statistics_service = get_analytics_statistics_service()
        result = await statistics_service.get_aggregated_statistics(search_params, db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate statistics: {str(e)}"
        )


@router.get("/analytics/batch/{batch_job_id}")
async def get_batch_analytics(
    batch_job_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get comprehensive analytics for a specific batch job.
    
    Returns success/failure counts, timing, performance metrics, and activity breakdown.
    """
    try:
        batch_service = get_batch_analytics_service()
        result = await batch_service.get_batch_summary(batch_job_id, db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch analytics: {str(e)}"
        )


@router.get("/analytics/batch/{batch_job_id}/performance")
async def get_batch_performance_analytics(
    batch_job_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get performance analytics for a specific batch job.
    
    Includes resource usage, bottlenecks, and performance trends.
    """
    try:
        batch_service = get_batch_analytics_service()
        result = await batch_service.get_batch_performance_analytics(batch_job_id, db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch performance analytics: {str(e)}"
        )


@router.get("/analytics/batches/recent")
async def get_recent_batches(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of batches"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get summary of recent batch operations.
    """
    try:
        batch_service = get_batch_analytics_service()
        batches = await batch_service.get_recent_batches(days, limit, db)
        
        return {
            "success": True,
            "message": f"Retrieved {len(batches)} recent batches",
            "data": {
                "batches": batches,
                "analysis_period": {
                    "days": days,
                    "limit": limit
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent batches: {str(e)}"
        )


@router.get("/analytics/users/{user_id}/summary")
async def get_user_activity_summary(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get comprehensive activity summary for a specific user.
    
    Returns activity counts, success rates, and usage patterns.
    """
    try:
        user_service = get_user_analytics_service()
        result = await user_service.get_user_summary(user_id, days, db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user summary: {str(e)}"
        )


@router.get("/analytics/users/{user_id}/timeline")
async def get_user_activity_timeline(
    user_id: str,
    days: int = Query(30, ge=1, le=90, description="Number of days for timeline"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a timeline of user activity showing daily patterns and trends.
    """
    try:
        user_service = get_user_analytics_service()
        result = await user_service.get_user_activity_timeline(user_id, days, db)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user timeline: {str(e)}"
        )


@router.get("/analytics/users/top")
async def get_top_users(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of users"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get the most active users in the specified time period.
    """
    try:
        user_service = get_user_analytics_service()
        users = await user_service.get_top_users(days, limit, db)
        
        return {
            "success": True,
            "message": f"Retrieved top {len(users)} users",
            "data": {
                "users": users,
                "analysis_period": {
                    "days": days,
                    "limit": limit
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get top users: {str(e)}"
        )


@router.get("/analytics/system/overview")
async def get_system_analytics_overview(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get comprehensive system analytics overview.
    
    Combines multiple analytics sources for a dashboard view.
    """
    try:
        # Get recent activity statistics
        statistics_service = get_analytics_statistics_service()
        batch_service = get_batch_analytics_service()
        user_service = get_user_analytics_service()
        
        # Calculate date range
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        search_params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        # Get overall statistics
        stats_result = await statistics_service.get_aggregated_statistics(search_params, db)
        
        # Get recent batches
        recent_batches = await batch_service.get_recent_batches(days, 10, db)
        
        # Get top users
        top_users = await user_service.get_top_users(days, 5, db)
        
        return {
            "success": True,
            "message": f"System analytics overview for {days} days",
            "data": {
                "analysis_period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "overall_statistics": stats_result.get("statistics", {}),
                "recent_batches": {
                    "count": len(recent_batches),
                    "batches": recent_batches[:5]  # Top 5 most recent
                },
                "top_users": {
                    "count": len(top_users),
                    "users": top_users
                },
                "summary": {
                    "total_activities": stats_result.get("statistics", {}).get("totals", {}).get("total_activities", 0),
                    "success_rate": stats_result.get("statistics", {}).get("totals", {}).get("success_rate", 0),
                    "active_users": len(top_users),
                    "active_batches": len(recent_batches)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system overview: {str(e)}"
        )
