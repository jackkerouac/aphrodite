"""
User Analytics Service

Provides analytics for user-specific activity tracking including
usage patterns, success rates, and activity summaries.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta

from app.models.media_activity import MediaActivityModel
from app.models.badge_application import BadgeApplicationModel
from app.models.poster_replacement import PosterReplacementModel


class UserAnalyticsService:
    """Service for analyzing user-specific activity patterns"""
    
    async def get_user_summary(
        self,
        user_id: str,
        days: int = 30,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get comprehensive activity summary for a specific user.
        
        Returns activity counts, success rates, and usage patterns.
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get all user activities in the time range
            query = select(MediaActivityModel).where(
                and_(
                    MediaActivityModel.user_id == user_id,
                    MediaActivityModel.created_at >= start_date
                )
            ).order_by(desc(MediaActivityModel.created_at))
            
            result = await db_session.execute(query)
            activities = result.scalars().all()
            
            if not activities:
                return {
                    "user_id": user_id,
                    "found": False,
                    "message": f"No activities found for user in the last {days} days"
                }
            
            # Calculate basic statistics
            total_activities = len(activities)
            successful = sum(1 for a in activities if a.success is True)
            failed = sum(1 for a in activities if a.success is False)
            pending = sum(1 for a in activities if a.success is None)
            
            # Activity type breakdown
            activity_types = {}
            for activity in activities:
                activity_type = activity.activity_type
                if activity_type not in activity_types:
                    activity_types[activity_type] = {
                        "total": 0, 
                        "successful": 0, 
                        "failed": 0,
                        "avg_processing_time_ms": None
                    }
                
                activity_types[activity_type]["total"] += 1
                if activity.success is True:
                    activity_types[activity_type]["successful"] += 1
                elif activity.success is False:
                    activity_types[activity_type]["failed"] += 1
            
            # Calculate average processing times per activity type
            for activity_type in activity_types:
                type_activities = [a for a in activities if a.activity_type == activity_type]
                processing_times = [a.processing_duration_ms for a in type_activities if a.processing_duration_ms]
                if processing_times:
                    activity_types[activity_type]["avg_processing_time_ms"] = round(
                        sum(processing_times) / len(processing_times)
                    )
            
            # Initiated by breakdown
            initiated_by_stats = {}
            for activity in activities:
                initiated_by = activity.initiated_by or "unknown"
                initiated_by_stats[initiated_by] = initiated_by_stats.get(initiated_by, 0) + 1
            
            # Daily activity pattern (last 7 days)
            daily_pattern = {}
            for i in range(7):
                day = end_date - timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                daily_pattern[day_str] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0
                }
            
            for activity in activities:
                if activity.created_at:
                    day_str = activity.created_at.strftime('%Y-%m-%d')
                    if day_str in daily_pattern:
                        daily_pattern[day_str]["total"] += 1
                        if activity.success is True:
                            daily_pattern[day_str]["successful"] += 1
                        elif activity.success is False:
                            daily_pattern[day_str]["failed"] += 1
            
            # Most common errors
            error_summary = {}
            for activity in activities:
                if activity.error_message:
                    error_msg = activity.error_message[:100]  # Truncate long errors
                    error_summary[error_msg] = error_summary.get(error_msg, 0) + 1
            
            # Top errors (max 5)
            top_errors = sorted(error_summary.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "user_id": user_id,
                "found": True,
                "analysis_period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_activities": total_activities,
                    "successful": successful,
                    "failed": failed,
                    "pending": pending,
                    "success_rate": round(successful / total_activities * 100, 2) if total_activities > 0 else 0
                },
                "activity_breakdown": activity_types,
                "usage_patterns": {
                    "initiated_by": initiated_by_stats,
                    "daily_pattern": daily_pattern
                },
                "top_errors": [
                    {"error": error, "count": count}
                    for error, count in top_errors
                ],
                "recent_activities": [
                    {
                        "activity_id": str(activity.id),
                        "media_id": activity.media_id,
                        "activity_type": activity.activity_type,
                        "status": activity.status,
                        "success": activity.success,
                        "created_at": activity.created_at.isoformat() if activity.created_at else None,
                        "processing_duration_ms": activity.processing_duration_ms
                    } for activity in activities[:10]  # Last 10 activities
                ]
            }
            
        except Exception as e:
            return {
                "user_id": user_id,
                "found": False,
                "error": f"Failed to analyze user activity: {str(e)}"
            }
    
    async def get_top_users(
        self,
        days: int = 30,
        limit: int = 10,
        db_session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get the most active users in the specified time period.
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user activity statistics
            query = select(
                MediaActivityModel.user_id,
                func.count(MediaActivityModel.id).label('total_activities'),
                func.sum(func.case([(MediaActivityModel.success == True, 1)], else_=0)).label('successful'),
                func.sum(func.case([(MediaActivityModel.success == False, 1)], else_=0)).label('failed'),
                func.avg(MediaActivityModel.processing_duration_ms).label('avg_processing_time')
            ).where(
                and_(
                    MediaActivityModel.user_id.isnot(None),
                    MediaActivityModel.created_at >= start_date
                )
            ).group_by(
                MediaActivityModel.user_id
            ).order_by(
                desc(func.count(MediaActivityModel.id))
            ).limit(limit)
            
            result = await db_session.execute(query)
            user_data = result.fetchall()
            
            users = []
            for row in user_data:
                total = row.total_activities or 0
                successful = row.successful or 0
                failed = row.failed or 0
                
                users.append({
                    "user_id": row.user_id,
                    "total_activities": total,
                    "successful": successful,
                    "failed": failed,
                    "pending": total - successful - failed,
                    "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
                    "average_processing_time_ms": round(float(row.avg_processing_time)) if row.avg_processing_time else None
                })
            
            return users
            
        except Exception as e:
            raise Exception(f"Failed to retrieve top users: {str(e)}")
    
    async def get_user_activity_timeline(
        self,
        user_id: str,
        days: int = 30,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get a timeline of user activity showing daily patterns and trends.
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user activities
            query = select(MediaActivityModel).where(
                and_(
                    MediaActivityModel.user_id == user_id,
                    MediaActivityModel.created_at >= start_date
                )
            ).order_by(MediaActivityModel.created_at)
            
            result = await db_session.execute(query)
            activities = result.scalars().all()
            
            # Create daily timeline
            timeline = {}
            for i in range(days + 1):
                day = start_date + timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                timeline[day_str] = {
                    "date": day_str,
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "pending": 0,
                    "activity_types": {},
                    "avg_processing_time_ms": None
                }
            
            # Populate timeline with activity data
            daily_processing_times = {}
            for activity in activities:
                if activity.created_at:
                    day_str = activity.created_at.strftime('%Y-%m-%d')
                    if day_str in timeline:
                        timeline[day_str]["total"] += 1
                        
                        if activity.success is True:
                            timeline[day_str]["successful"] += 1
                        elif activity.success is False:
                            timeline[day_str]["failed"] += 1
                        else:
                            timeline[day_str]["pending"] += 1
                        
                        # Track activity types
                        activity_type = activity.activity_type
                        if activity_type not in timeline[day_str]["activity_types"]:
                            timeline[day_str]["activity_types"][activity_type] = 0
                        timeline[day_str]["activity_types"][activity_type] += 1
                        
                        # Track processing times for average calculation
                        if activity.processing_duration_ms:
                            if day_str not in daily_processing_times:
                                daily_processing_times[day_str] = []
                            daily_processing_times[day_str].append(activity.processing_duration_ms)
            
            # Calculate average processing times
            for day_str in timeline:
                if day_str in daily_processing_times:
                    times = daily_processing_times[day_str]
                    timeline[day_str]["avg_processing_time_ms"] = round(sum(times) / len(times))
            
            # Convert to list and sort by date
            timeline_list = list(timeline.values())
            timeline_list.sort(key=lambda x: x["date"])
            
            return {
                "user_id": user_id,
                "period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "timeline": timeline_list,
                "summary": {
                    "total_days_with_activity": sum(1 for day in timeline_list if day["total"] > 0),
                    "most_active_day": max(timeline_list, key=lambda x: x["total"]) if timeline_list else None,
                    "average_daily_activities": round(sum(day["total"] for day in timeline_list) / len(timeline_list), 2) if timeline_list else 0
                }
            }
            
        except Exception as e:
            return {
                "user_id": user_id,
                "error": f"Failed to generate activity timeline: {str(e)}"
            }


def get_user_analytics_service() -> UserAnalyticsService:
    """Get singleton instance of UserAnalyticsService"""
    if not hasattr(get_user_analytics_service, '_instance'):
        get_user_analytics_service._instance = UserAnalyticsService()
    return get_user_analytics_service._instance
