"""
Analytics endpoints for Aphrodite v2
Provides system analytics and metrics data
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, extract, select, text
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from ..core.database import get_db_session
from ..models.jobs import ProcessingJobModel
from ..models.schedules import ScheduleModel, ScheduleExecutionModel
from ..models.media import MediaItemModel
from ..services.jellyfin_service import get_jellyfin_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Set up logging
logger = logging.getLogger(__name__)


class AnalyticsOverview(BaseModel):
    """Overview analytics data"""
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    queued_jobs: int
    running_jobs: int
    total_schedules: int
    active_schedules: int
    total_media_items: int
    processing_success_rate: float


class JobStatusDistribution(BaseModel):
    """Job status distribution data"""
    status: str
    count: int
    percentage: float


class ProcessingTrend(BaseModel):
    """Processing trend data point"""
    date: str
    completed: int
    failed: int
    created: int


class ScheduleAnalytics(BaseModel):
    """Schedule analytics data"""
    id: str
    name: str
    enabled: bool
    badge_types: List[str]
    target_libraries: List[str]
    last_execution: Optional[datetime]
    execution_count: int
    success_rate: float


class JobTypeDistribution(BaseModel):
    """Job type distribution data"""
    job_type: str
    count: int
    success_rate: float
    avg_duration_seconds: Optional[float]


class SystemPerformance(BaseModel):
    """System performance metrics"""
    avg_job_duration_seconds: Optional[float]
    jobs_per_hour_24h: float
    peak_hour_jobs: int
    peak_hour: int
    queue_health_score: float


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(db: AsyncSession = Depends(get_db_session)):
    """Get high-level analytics overview using workflow data"""
    
    try:
        # Import workflow models
        from app.services.workflow.database.models import BatchJobModel
        
        # Job statistics from workflow tables
        total_jobs_result = await db.execute(select(func.count(BatchJobModel.id)))
        total_jobs = total_jobs_result.scalar() or 0
        
        completed_jobs_result = await db.execute(
            select(func.count(BatchJobModel.id)).where(BatchJobModel.status == "completed")
        )
        completed_jobs = completed_jobs_result.scalar() or 0
        
        failed_jobs_result = await db.execute(
            select(func.count(BatchJobModel.id)).where(BatchJobModel.status == "failed")
        )
        failed_jobs = failed_jobs_result.scalar() or 0
        
        queued_jobs_result = await db.execute(
            select(func.count(BatchJobModel.id)).where(BatchJobModel.status == "queued")
        )
        queued_jobs = queued_jobs_result.scalar() or 0
        
        running_jobs_result = await db.execute(
            select(func.count(BatchJobModel.id)).where(BatchJobModel.status.in_(["running", "processing"]))
        )
        running_jobs = running_jobs_result.scalar() or 0
        
        # Schedule statistics (keep original)
        total_schedules_result = await db.execute(select(func.count(ScheduleModel.id)))
        total_schedules = total_schedules_result.scalar() or 0
        
        active_schedules_result = await db.execute(
            select(func.count(ScheduleModel.id)).where(ScheduleModel.enabled == True)
        )
        active_schedules = active_schedules_result.scalar() or 0
        
        # Media statistics - try to get live count from Jellyfin, fallback to database
        total_media_items = await get_live_media_count()
        if total_media_items == 0:
            # Fallback to database count if Jellyfin unavailable
            total_media_items_result = await db.execute(select(func.count(MediaItemModel.id)))
            total_media_items = total_media_items_result.scalar() or 0
        
        # Success rate calculation
        processed_jobs = completed_jobs + failed_jobs
        success_rate = (completed_jobs / processed_jobs * 100) if processed_jobs > 0 else 0.0
        
        return AnalyticsOverview(
            total_jobs=total_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            queued_jobs=queued_jobs,
            running_jobs=running_jobs,
            total_schedules=total_schedules,
            active_schedules=active_schedules,
            total_media_items=total_media_items,
            processing_success_rate=round(success_rate, 2)
        )
    except Exception as e:
        logger.error(f"Error in get_analytics_overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics overview: {str(e)}")


@router.get("/jobs/status-distribution", response_model=List[JobStatusDistribution])
async def get_job_status_distribution(db: AsyncSession = Depends(get_db_session)):
    """Get distribution of job statuses from workflow data"""
    
    try:
        # Import workflow models
        from app.services.workflow.database.models import BatchJobModel
        
        total_jobs_result = await db.execute(select(func.count(BatchJobModel.id)))
        total_jobs = total_jobs_result.scalar() or 0
        
        if total_jobs == 0:
            return []
        
        status_counts_result = await db.execute(
            select(BatchJobModel.status, func.count(BatchJobModel.id).label("count"))
            .group_by(BatchJobModel.status)
        )
        status_counts = status_counts_result.all()
        
        return [
            JobStatusDistribution(
                status=status,
                count=count,
                percentage=round(count / total_jobs * 100, 2)
            )
            for status, count in status_counts
        ]
    except Exception as e:
        logger.error(f"Error in get_job_status_distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch job status distribution: {str(e)}")


@router.get("/jobs/trends", response_model=List[ProcessingTrend])
async def get_processing_trends(
    days: int = 30,
    db: AsyncSession = Depends(get_db_session)
):
    """Get processing trends over the specified number of days from workflow data"""
    
    try:
        # Import workflow models
        from app.services.workflow.database.models import BatchJobModel
        
        # Get all jobs and filter in Python to avoid date comparison issues
        all_jobs_result = await db.execute(
            select(BatchJobModel.created_at, BatchJobModel.status)
        )
        all_jobs = all_jobs_result.all()
        
        # Filter by date range in Python
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        filtered_jobs = []
        for job in all_jobs:
            if job.created_at:
                # Ensure job.created_at is timezone-aware
                job_time = job.created_at
                if job_time.tzinfo is None:
                    job_time = job_time.replace(tzinfo=timezone.utc)
                
                if start_date <= job_time <= end_date:
                    filtered_jobs.append(job)
        
        # Process the data in Python
        daily_stats = {}
        for job in filtered_jobs:
            if job.created_at:
                job_time = job.created_at
                if job_time.tzinfo is None:
                    job_time = job_time.replace(tzinfo=timezone.utc)
                
                date_key = job_time.date().isoformat()
                if date_key not in daily_stats:
                    daily_stats[date_key] = {"created": 0, "completed": 0, "failed": 0}
                
                daily_stats[date_key]["created"] += 1
                if job.status == "completed":
                    daily_stats[date_key]["completed"] += 1
                elif job.status == "failed":
                    daily_stats[date_key]["failed"] += 1
        
        # Fill in missing dates with zeros
        trends = []
        current_date = start_date.date()
        
        for i in range(days):
            date_str = current_date.isoformat()
            if date_str in daily_stats:
                stats = daily_stats[date_str]
                trends.append(ProcessingTrend(
                    date=date_str,
                    created=stats["created"],
                    completed=stats["completed"],
                    failed=stats["failed"]
                ))
            else:
                trends.append(ProcessingTrend(
                    date=date_str,
                    created=0,
                    completed=0,
                    failed=0
                ))
            current_date += timedelta(days=1)
        
        return trends
    except Exception as e:
        logger.error(f"Error in get_processing_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch processing trends: {str(e)}")


@router.get("/jobs/types", response_model=List[JobTypeDistribution])
async def get_job_type_distribution(db: AsyncSession = Depends(get_db_session)):
    """Get distribution and performance metrics by job type"""
    
    try:
        # Get all jobs and process in Python to avoid complex SQL
        jobs_result = await db.execute(
            select(ProcessingJobModel.job_type, ProcessingJobModel.status, 
                   ProcessingJobModel.started_at, ProcessingJobModel.completed_at)
            .where(ProcessingJobModel.job_type.isnot(None))
        )
        jobs = jobs_result.all()
        
        # Process in Python
        job_type_stats = {}
        
        for job in jobs:
            job_type = job.job_type
            if job_type not in job_type_stats:
                job_type_stats[job_type] = {
                    "total": 0,
                    "completed": 0,
                    "durations": []
                }
            
            job_type_stats[job_type]["total"] += 1
            
            if job.status == "completed":
                job_type_stats[job_type]["completed"] += 1
                
                # Calculate duration if we have both start and end times
                if job.started_at and job.completed_at:
                    duration = (job.completed_at - job.started_at).total_seconds()
                    job_type_stats[job_type]["durations"].append(duration)
        
        # Build response
        result = []
        for job_type, stats in job_type_stats.items():
            success_rate = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            avg_duration = sum(stats["durations"]) / len(stats["durations"]) if stats["durations"] else None
            
            result.append(JobTypeDistribution(
                job_type=job_type,
                count=stats["total"],
                success_rate=round(success_rate, 2),
                avg_duration_seconds=round(avg_duration, 2) if avg_duration else None
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error in get_job_type_distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch job type distribution: {str(e)}")


@router.get("/schedules", response_model=List[ScheduleAnalytics])
async def get_schedule_analytics(db: AsyncSession = Depends(get_db_session)):
    """Get analytics for all schedules"""
    
    try:
        schedules_result = await db.execute(select(ScheduleModel))
        schedules = schedules_result.scalars().all()
        
        schedule_analytics = []
        for schedule in schedules:
            # Get execution statistics
            executions_result = await db.execute(
                select(ScheduleExecutionModel).where(ScheduleExecutionModel.schedule_id == schedule.id)
            )
            executions = executions_result.scalars().all()
            
            execution_count = len(executions)
            success_count = len([e for e in executions if e.status == "completed"])
            success_rate = (success_count / execution_count * 100) if execution_count > 0 else 0.0
            
            # Get last execution
            last_execution = None
            if executions:
                sorted_executions = sorted(executions, key=lambda e: e.started_at or e.created_at, reverse=True)
                last_execution = sorted_executions[0].started_at
            
            schedule_analytics.append(ScheduleAnalytics(
                id=str(schedule.id),
                name=schedule.name,
                enabled=schedule.enabled,
                badge_types=schedule.badge_types or [],
                target_libraries=schedule.target_libraries or [],
                last_execution=last_execution,
                execution_count=execution_count,
                success_rate=round(success_rate, 2)
            ))
        
        return schedule_analytics
    except Exception as e:
        logger.error(f"Error in get_schedule_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch schedule analytics: {str(e)}")


@router.get("/performance", response_model=SystemPerformance)
async def get_system_performance(db: AsyncSession = Depends(get_db_session)):
    """Get system performance metrics"""
    
    try:
        # Get all jobs and filter in Python to avoid datetime issues
        all_jobs_result = await db.execute(
            select(ProcessingJobModel.created_at, ProcessingJobModel.status,
                   ProcessingJobModel.started_at, ProcessingJobModel.completed_at)
        )
        all_jobs = all_jobs_result.all()
        
        # Filter for recent jobs (last 24 hours) in Python
        twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_jobs = []
        completed_jobs = []
        
        for job in all_jobs:
            # Handle timezone awareness for created_at
            if job.created_at:
                job_time = job.created_at
                if job_time.tzinfo is None:
                    job_time = job_time.replace(tzinfo=timezone.utc)
                
                if job_time >= twenty_four_hours_ago:
                    recent_jobs.append(job)
            
            # Handle completed jobs for duration calculation
            if (job.status == "completed" and 
                job.started_at and job.completed_at):
                completed_jobs.append(job)
        
        # Calculate average duration
        durations = []
        for job in completed_jobs:
            if job.started_at and job.completed_at:
                # Handle timezone awareness for duration calculation
                start_time = job.started_at
                end_time = job.completed_at
                
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=timezone.utc)
                
                duration = (end_time - start_time).total_seconds()
                durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else None
        
        # Calculate jobs per hour
        jobs_per_hour_24h = len(recent_jobs) / 24.0
        
        # Calculate peak hour
        hourly_counts = {}
        for job in recent_jobs:
            if job.created_at:
                job_time = job.created_at
                if job_time.tzinfo is None:
                    job_time = job_time.replace(tzinfo=timezone.utc)
                
                hour = job_time.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        peak_hour = 0
        peak_hour_jobs = 0
        if hourly_counts:
            peak_hour = max(hourly_counts, key=hourly_counts.get)
            peak_hour_jobs = hourly_counts[peak_hour]
        
        # Calculate queue health
        queued_count_result = await db.execute(
            select(func.count(ProcessingJobModel.id)).where(ProcessingJobModel.status == "queued")
        )
        queued_count = queued_count_result.scalar() or 0
        
        total_recent = len(recent_jobs)
        failed_recent = len([j for j in recent_jobs if j.status == "failed"])
        
        # Health score: lower queue size and failure rate = higher score
        queue_factor = max(0, 100 - (queued_count * 2))  # Penalty for large queue
        failure_factor = 100 - ((failed_recent / total_recent * 100) if total_recent > 0 else 0)
        queue_health_score = (queue_factor + failure_factor) / 2
        
        return SystemPerformance(
            avg_job_duration_seconds=round(avg_duration, 2) if avg_duration else None,
            jobs_per_hour_24h=round(jobs_per_hour_24h, 2),
            peak_hour_jobs=peak_hour_jobs,
            peak_hour=peak_hour,
            queue_health_score=round(queue_health_score, 2)
        )
    except Exception as e:
        logger.error(f"Error in get_system_performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch system performance: {str(e)}")


class ActivityDetail(BaseModel):
    """Individual activity detail"""
    id: str
    name: str
    status: str
    badge_types: List[str]
    total_posters: int
    completed_posters: int
    failed_posters: int
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    user_id: str
    error_summary: Optional[str]
    

class ActivityDetailResponse(BaseModel):
    """Response for activity type details"""
    activity_type: str
    total_count: int
    activities: List[ActivityDetail]
    pagination: Dict[str, Any]


@router.get("/activity-details/{activity_type}", response_model=ActivityDetailResponse)
async def get_activity_type_details(
    activity_type: str,
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    days: int = 7,
    db: AsyncSession = Depends(get_db_session)
):
    """Get detailed list of activities for a specific activity type"""
    
    from .activity_details_helper import get_activity_type_details_fixed
    
    return await get_activity_type_details_fixed(
        activity_type=activity_type,
        page=page,
        limit=limit,
        status=status,
        days=days,
        db=db
    )


class PerformanceMetrics(BaseModel):
    """Performance metrics data"""
    avg_job_duration_seconds: Optional[float]
    total_jobs_processed: int
    average_throughput_posters_per_job: float
    success_rate_percentage: float
    jobs_per_hour_24h: float
    peak_processing_times: List[Dict[str, Any]]
    processing_efficiency: Dict[str, Any]
    system_load_trends: List[Dict[str, Any]]


@router.get("/performance-metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(db: AsyncSession = Depends(get_db_session)):
    """Get comprehensive performance metrics from batch jobs data"""
    
    try:
        # Import workflow models
        from app.services.workflow.database.models import BatchJobModel
        
        # Get all completed jobs with timing data
        completed_jobs_result = await db.execute(
            select(BatchJobModel)
            .where(
                and_(
                    BatchJobModel.status == "completed",
                    BatchJobModel.started_at.isnot(None),
                    BatchJobModel.completed_at.isnot(None)
                )
            )
        )
        completed_jobs = completed_jobs_result.scalars().all()
        
        # Get all jobs for broader statistics
        all_jobs_result = await db.execute(select(BatchJobModel))
        all_jobs = all_jobs_result.scalars().all()
        
        # Calculate basic metrics
        total_jobs = len(all_jobs)
        completed_count = len([j for j in all_jobs if j.status == "completed"])
        success_rate = (completed_count / total_jobs * 100) if total_jobs > 0 else 0
        
        # Calculate duration metrics
        durations = []
        throughput_data = []
        
        for job in completed_jobs:
            if job.started_at and job.completed_at:
                duration_seconds = (job.completed_at - job.started_at).total_seconds()
                durations.append(duration_seconds)
                
                # Calculate throughput (posters per second)
                if duration_seconds > 0 and job.total_posters:
                    throughput = job.total_posters / duration_seconds
                    throughput_data.append({
                        "job_id": job.id,
                        "duration": duration_seconds,
                        "posters": job.total_posters,
                        "throughput": throughput,
                        "created_at": job.created_at.isoformat() if job.created_at else None
                    })
        
        avg_duration = sum(durations) / len(durations) if durations else None
        avg_throughput = sum(job["posters"] for job in throughput_data) / len(throughput_data) if throughput_data else 0
        
        # Calculate jobs per hour (last 24 hours)
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        recent_jobs = [
            job for job in all_jobs 
            if job.created_at and job.created_at >= twenty_four_hours_ago
        ]
        jobs_per_hour = len(recent_jobs) / 24.0
        
        # Find peak processing times (group by hour)
        hourly_stats = {}
        for job in completed_jobs:
            if job.created_at:
                hour_key = job.created_at.replace(minute=0, second=0, microsecond=0)
                if hour_key not in hourly_stats:
                    hourly_stats[hour_key] = {"count": 0, "total_posters": 0, "total_duration": 0}
                
                hourly_stats[hour_key]["count"] += 1
                hourly_stats[hour_key]["total_posters"] += job.total_posters or 0
                
                if job.started_at and job.completed_at:
                    duration = (job.completed_at - job.started_at).total_seconds()
                    hourly_stats[hour_key]["total_duration"] += duration
        
        # Convert to list and sort by activity
        peak_times = []
        for hour, stats in hourly_stats.items():
            avg_duration_hour = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
            peak_times.append({
                "hour": hour.isoformat(),
                "jobs_count": stats["count"],
                "total_posters": stats["total_posters"],
                "avg_duration_seconds": round(avg_duration_hour, 2),
                "efficiency_score": round(stats["total_posters"] / max(avg_duration_hour, 1), 2)
            })
        
        # Sort by jobs count and take top 5
        peak_times.sort(key=lambda x: x["jobs_count"], reverse=True)
        top_peak_times = peak_times[:5]
        
        # Processing efficiency analysis
        efficiency_analysis = {
            "fastest_job_duration": min(durations) if durations else 0,
            "slowest_job_duration": max(durations) if durations else 0,
            "median_duration": sorted(durations)[len(durations)//2] if durations else 0,
            "efficiency_variance": round(max(durations) - min(durations), 2) if durations else 0,
            "high_throughput_jobs": len([d for d in throughput_data if d["throughput"] > 1]) if throughput_data else 0
        }
        
        # System load trends (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        daily_loads = {}
        
        for job in all_jobs:
            if job.created_at and job.created_at >= seven_days_ago:
                day_key = job.created_at.date()
                if day_key not in daily_loads:
                    daily_loads[day_key] = {"jobs": 0, "posters": 0, "completed": 0}
                
                daily_loads[day_key]["jobs"] += 1
                daily_loads[day_key]["posters"] += job.total_posters or 0
                if job.status == "completed":
                    daily_loads[day_key]["completed"] += 1
        
        load_trends = []
        for day, stats in daily_loads.items():
            success_rate_day = (stats["completed"] / stats["jobs"] * 100) if stats["jobs"] > 0 else 0
            load_trends.append({
                "date": day.isoformat(),
                "total_jobs": stats["jobs"],
                "total_posters": stats["posters"],
                "success_rate": round(success_rate_day, 2),
                "load_score": round(stats["jobs"] * stats["posters"] / 100, 2)  # Normalized load score
            })
        
        # Sort by date
        load_trends.sort(key=lambda x: x["date"])
        
        return PerformanceMetrics(
            avg_job_duration_seconds=round(avg_duration, 2) if avg_duration else None,
            total_jobs_processed=total_jobs,
            average_throughput_posters_per_job=round(avg_throughput, 2),
            success_rate_percentage=round(success_rate, 2),
            jobs_per_hour_24h=round(jobs_per_hour, 2),
            peak_processing_times=top_peak_times,
            processing_efficiency=efficiency_analysis,
            system_load_trends=load_trends
        )
        
    except Exception as e:
        logger.error(f"Error in get_performance_metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")


async def get_live_media_count() -> int:
    """Get live media count from Jellyfin"""
    try:
        jellyfin_service = get_jellyfin_service()
        
        # Load Jellyfin settings
        await jellyfin_service._load_jellyfin_settings()
        
        # Test connection first
        connection_ok, _ = await jellyfin_service.test_connection()
        if not connection_ok:
            logger.warning("Jellyfin connection failed for live media count")
            return 0
        
        # Get all libraries
        libraries = await jellyfin_service.get_libraries()
        if not libraries:
            logger.warning("No libraries found in Jellyfin")
            return 0
        
        total_count = 0
        
        # Count items in each library
        for library in libraries:
            library_id = library.get("ItemId")
            if not library_id:
                continue
                
            # Get library items count efficiently
            items = await jellyfin_service.get_library_items(library_id)
            
            # Filter for movies and TV shows only
            media_items = [
                item for item in items 
                if item.get("Type") in ["Movie", "Series"]
            ]
            
            total_count += len(media_items)
            logger.debug(f"Library {library.get('Name', 'Unknown')}: {len(media_items)} items")
        
        logger.info(f"Live media count from Jellyfin: {total_count}")
        return total_count
        
    except Exception as e:
        logger.error(f"Error getting live media count from Jellyfin: {e}")
        return 0
