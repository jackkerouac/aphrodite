"""
Simplified activity details endpoint - emergency fix
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

class SimpleActivityDetail(BaseModel):
    """Simple activity detail"""
    id: str
    name: str
    status: str
    total_posters: int
    completed_posters: int
    failed_posters: int
    created_at: str
    user_id: str

class SimpleActivityDetailResponse(BaseModel):
    """Simple response for activity type details"""
    activity_type: str
    total_count: int
    activities: List[SimpleActivityDetail]

async def get_activity_type_details_simple(
    activity_type: str,
    limit: int = 10,
    db: AsyncSession = None
):
    """Ultra-simple version that should work"""
    
    try:
        # Import workflow models
        from app.services.workflow.database.models import BatchJobModel
        
        logger.info(f"Getting simple activity details for {activity_type}")
        
        # Get recent jobs (last 7 days)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        # Simple query - just get recent jobs
        query = select(BatchJobModel).where(
            BatchJobModel.created_at >= start_date
        ).limit(limit)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        logger.info(f"Found {len(jobs)} jobs in last 7 days")
        
        # Convert to simple format
        activities = []
        for job in jobs:
            try:
                activities.append(SimpleActivityDetail(
                    id=job.id,
                    name=job.name or "Unknown Job",
                    status=job.status,
                    total_posters=job.total_posters or 0,
                    completed_posters=job.completed_posters or 0,
                    failed_posters=job.failed_posters or 0,
                    created_at=job.created_at.isoformat() if job.created_at else "",
                    user_id=job.user_id or "unknown"
                ))
            except Exception as e:
                logger.warning(f"Error processing job {job.id}: {e}")
                continue
        
        return SimpleActivityDetailResponse(
            activity_type=activity_type,
            total_count=len(activities),
            activities=activities
        )
        
    except Exception as e:
        logger.error(f"Error in simple activity details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simple endpoint failed: {str(e)}")
