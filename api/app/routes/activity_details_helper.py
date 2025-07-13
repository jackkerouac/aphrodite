"""
Fixed activity details endpoint for analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from ..core.database import get_db_session

# Set up logging
logger = logging.getLogger(__name__)

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

async def get_activity_type_details_fixed(
    activity_type: str,
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    days: int = 7,
    db: AsyncSession = None
):
    """Get detailed list of activities for a specific activity type - fixed version"""
    
    try:
        # Import workflow models with better error handling
        try:
            from app.services.workflow.database.models import BatchJobModel
        except ImportError as e:
            logger.error(f"Failed to import BatchJobModel: {e}")
            # Return empty response if models not available
            return ActivityDetailResponse(
                activity_type=activity_type,
                total_count=0,
                activities=[],
                pagination={
                    "page": page,
                    "limit": limit,
                    "total_pages": 0,
                    "total_count": 0,
                    "has_next": False,
                    "has_prev": False
                }
            )
        
        # Map activity types to job characteristics
        activity_mapping = {
            "badge_application": ["badge", "badges"],
            "poster_replacement": ["poster", "posters", "replacement"]
        }
        
        if activity_type not in activity_mapping:
            raise HTTPException(status_code=400, detail=f"Unknown activity type: {activity_type}")
        
        # Calculate date range - make sure we use naive datetimes for PostgreSQL
        end_date = datetime.now()  # Remove timezone.utc to make it naive
        start_date = end_date - timedelta(days=days)
        
        # Check if BatchJobModel table exists by trying a simple query first
        try:
            test_result = await db.execute(select(func.count(BatchJobModel.id)))
            total_jobs = test_result.scalar() or 0
        except Exception as e:
            logger.warning(f"BatchJobModel table might not exist or be accessible: {e}")
            # Return empty response if table doesn't exist
            return ActivityDetailResponse(
                activity_type=activity_type,
                total_count=0,
                activities=[],
                pagination={
                    "page": page,
                    "limit": limit,
                    "total_pages": 0,
                    "total_count": 0,
                    "has_next": False,
                    "has_prev": False
                }
            )
        
        # Build base query with safer datetime handling
        try:
            query = select(BatchJobModel).where(
                BatchJobModel.created_at >= start_date
            )
            
            # Filter by status if provided
            if status and status != 'all':
                query = query.where(BatchJobModel.status == status)
            
            # Get all jobs in date range
            jobs_result = await db.execute(query)
            all_jobs = jobs_result.scalars().all()
            
            logger.info(f"Found {len(all_jobs)} jobs in date range")
            
        except Exception as e:
            logger.error(f"Error executing job query: {e}")
            # Try without date filter as fallback
            query = select(BatchJobModel).limit(20)
            if status and status != 'all':
                query = query.where(BatchJobModel.status == status)
            
            jobs_result = await db.execute(query)
            all_jobs = jobs_result.scalars().all()
            logger.info(f"Fallback query found {len(all_jobs)} jobs")
        
        # Filter jobs based on activity type by checking name or badge_types
        keywords = activity_mapping[activity_type]
        filtered_jobs = []
        
        for job in all_jobs:
            job_matches = False
            
            # Check job name for keywords
            if job.name:
                job_name_lower = job.name.lower()
                if any(keyword in job_name_lower for keyword in keywords):
                    job_matches = True
            
            # For badge application, also check badge_types
            if activity_type == "badge_application" and job.badge_types:
                job_matches = True
            
            # For poster replacement, check if no badge types (pure poster operations)
            if activity_type == "poster_replacement" and (not job.badge_types or len(job.badge_types) == 0):
                job_matches = True
            
            if job_matches:
                filtered_jobs.append(job)
        
        # Sort by created_at descending with safe datetime handling
        def safe_sort_key(job):
            if job.created_at:
                return job.created_at
            else:
                return datetime.min  # Use naive datetime.min
        
        filtered_jobs.sort(key=safe_sort_key, reverse=True)
        
        # Calculate pagination
        total_count = len(filtered_jobs)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        offset = (page - 1) * limit
        paginated_jobs = filtered_jobs[offset:offset + limit]
        
        # Build response with safer field access
        activities = []
        for job in paginated_jobs:
            try:
                activities.append(ActivityDetail(
                    id=str(job.id) if job.id else "unknown",
                    name=str(job.name) if job.name else "Unknown Job",
                    status=str(job.status) if job.status else "unknown",
                    badge_types=list(job.badge_types) if job.badge_types else [],
                    total_posters=int(job.total_posters) if job.total_posters is not None else 0,
                    completed_posters=int(job.completed_posters) if job.completed_posters is not None else 0,
                    failed_posters=int(job.failed_posters) if job.failed_posters is not None else 0,
                    created_at=job.created_at.isoformat() if job.created_at else "",
                    started_at=job.started_at.isoformat() if job.started_at else None,
                    completed_at=job.completed_at.isoformat() if job.completed_at else None,
                    user_id=str(job.user_id) if job.user_id else "unknown",
                    error_summary=str(job.error_summary) if job.error_summary else None
                ))
            except Exception as job_error:
                logger.warning(f"Error processing job {job.id}: {job_error}")
                # Skip this job and continue
                continue
        
        return ActivityDetailResponse(
            activity_type=activity_type,
            total_count=total_count,
            activities=activities,
            pagination={
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_activity_type_details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch activity details: {str(e)}")
