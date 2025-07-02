"""
Schedule management routes for Aphrodite v2
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete, and_
from pydantic import BaseModel, Field
import uuid

from ..core.database import get_db_session
from ..models.schedules import ScheduleModel, ScheduleExecutionModel
from ..services.jellyfin_service import get_jellyfin_service
from ..services.scheduler_service import get_scheduler_service


router = APIRouter(prefix="/schedules", tags=["schedules"])


# Pydantic models for API
class ScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    timezone: str = Field(default="UTC")
    cron_expression: str = Field(..., min_length=1, max_length=100)
    badge_types: List[str] = Field(default=[])
    reprocess_all: bool = Field(default=False)
    enabled: bool = Field(default=True)
    target_libraries: List[str] = Field(default=[])


class ScheduleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    timezone: Optional[str] = None
    cron_expression: Optional[str] = Field(None, min_length=1, max_length=100)
    badge_types: Optional[List[str]] = None
    reprocess_all: Optional[bool] = None
    enabled: Optional[bool] = None
    target_libraries: Optional[List[str]] = None


class ScheduleResponse(BaseModel):
    id: str
    name: str
    timezone: str
    cron_expression: str
    badge_types: List[str]
    reprocess_all: bool
    enabled: bool
    target_libraries: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Custom serializer to convert UUID to string
        json_encoders = {
            uuid.UUID: str
        }

    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle UUID conversion"""
        data = {
            'id': str(obj.id),
            'name': obj.name,
            'timezone': obj.timezone,
            'cron_expression': obj.cron_expression,
            'badge_types': obj.badge_types,
            'reprocess_all': obj.reprocess_all,
            'enabled': obj.enabled,
            'target_libraries': obj.target_libraries,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }
        return cls(**data)


class ScheduleExecutionResponse(BaseModel):
    id: str
    schedule_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    items_processed: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        # Custom serializer to convert UUID to string
        json_encoders = {
            uuid.UUID: str
        }

    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle UUID conversion"""
        data = {
            'id': str(obj.id),
            'schedule_id': str(obj.schedule_id),
            'status': obj.status,
            'started_at': obj.started_at,
            'completed_at': obj.completed_at,
            'error_message': obj.error_message,
            'items_processed': obj.items_processed,
            'created_at': obj.created_at,
        }
        return cls(**data)


# Available badge types
AVAILABLE_BADGE_TYPES = [
    "resolution",
    "audio", 
    "review",
    "awards"
]

# Cron presets
CRON_PRESETS = {
    "hourly": "0 * * * *",
    "daily_2am": "0 2 * * *",
    "weekly": "0 2 * * 0",
    "monthly": "0 2 1 * *",
    "every_6_hours": "0 */6 * * *",
    "weekdays_2am": "0 2 * * 1-5",
    "weekends_2am": "0 2 * * 6,0",
    "twice_daily": "0 2,14 * * *"
}


@router.get("/", response_model=List[ScheduleResponse])
@router.get("", response_model=List[ScheduleResponse])  # Handle both with and without trailing slash
async def get_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all schedules"""
    stmt = select(ScheduleModel).offset(skip).limit(limit)
    result = await db.execute(stmt)
    schedules = result.scalars().all()
    return [ScheduleResponse.from_orm(schedule) for schedule in schedules]


@router.post("/", response_model=ScheduleResponse)
@router.post("", response_model=ScheduleResponse)  # Handle both with and without trailing slash
async def create_schedule(
    schedule: ScheduleCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new schedule"""
    db_schedule = ScheduleModel(**schedule.dict())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return ScheduleResponse.from_orm(db_schedule)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific schedule"""
    stmt = select(ScheduleModel).where(ScheduleModel.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleResponse.from_orm(schedule)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_update: ScheduleUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update a schedule"""
    stmt = select(ScheduleModel).where(ScheduleModel.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    schedule.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(schedule)
    return ScheduleResponse.from_orm(schedule)


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a schedule"""
    stmt = select(ScheduleModel).where(ScheduleModel.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    await db.delete(schedule)
    await db.commit()
    return {"message": "Schedule deleted successfully"}


@router.get("/executions/history", response_model=List[ScheduleExecutionResponse])
async def get_schedule_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    schedule_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Get schedule execution history"""
    stmt = select(ScheduleExecutionModel)
    
    if schedule_id:
        stmt = stmt.where(ScheduleExecutionModel.schedule_id == schedule_id)
    if status:
        stmt = stmt.where(ScheduleExecutionModel.status == status)
    
    stmt = stmt.order_by(desc(ScheduleExecutionModel.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    executions = result.scalars().all()
    return [ScheduleExecutionResponse.from_orm(execution) for execution in executions]


@router.get("/config/badge-types")
async def get_available_badge_types():
    """Get available badge types"""
    return {"badge_types": AVAILABLE_BADGE_TYPES}


@router.get("/config/cron-presets")
async def get_cron_presets():
    """Get available cron presets"""
    return {"presets": CRON_PRESETS}


@router.get("/config/libraries")
async def get_target_libraries():
    """Get available libraries from Jellyfin"""
    try:
        jellyfin_service = get_jellyfin_service()
        libraries = await jellyfin_service.get_libraries()
        
        # Filter to only movies and shows - handle different field name formats
        target_libraries = []
        for lib in libraries:
            # VirtualFolders API uses different field names than Items API
            lib_id = lib.get("ItemId") or lib.get("Id") or lib.get("id")
            lib_name = lib.get("Name") or lib.get("name") or "Unknown Library"
            lib_type = lib.get("CollectionType") or lib.get("Type") or "unknown"
            
            # Only include movie and TV libraries
            if lib_type.lower() in ["movies", "tvshows", "movie", "tvshow"]:
                target_libraries.append({
                    "id": str(lib_id) if lib_id else f"lib_{len(target_libraries)}",
                    "name": lib_name,
                    "type": lib_type
                })
        
        return {"libraries": target_libraries}
    except Exception as e:
        # Log the full error for debugging
        from aphrodite_logging import get_logger
        logger = get_logger("aphrodite.api.schedules")
        logger.error(f"Libraries API error: {e}", exc_info=True)
        
        # Return empty list on error so frontend doesn't break
        return {"libraries": []}


@router.get("/{schedule_id}/executions/{execution_id}", response_model=ScheduleExecutionResponse)
async def get_schedule_execution(
    schedule_id: str,
    execution_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get details of a specific schedule execution"""
    stmt = select(ScheduleExecutionModel).where(
        and_(
            ScheduleExecutionModel.id == execution_id,
            ScheduleExecutionModel.schedule_id == schedule_id
        )
    )
    result = await db.execute(stmt)
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Schedule execution not found")
    return ScheduleExecutionResponse.from_orm(execution)


@router.post("/{schedule_id}/execute")
async def execute_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Manually execute a schedule"""
    stmt = select(ScheduleModel).where(ScheduleModel.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Use scheduler service to execute the schedule
    scheduler_service = get_scheduler_service()
    execution_id = await scheduler_service.execute_schedule_manually(schedule_id)
    
    if execution_id:
        return {
            "message": "Schedule execution started successfully",
            "execution_id": execution_id,
            "schedule_name": schedule.name,
            "library_count": len(schedule.target_libraries),
            "badge_types": schedule.badge_types,
            "status": "processing"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to execute schedule")


@router.delete("/executions/history")
async def clear_schedule_history(
    schedule_id: Optional[str] = Query(None, description="Clear history for specific schedule, or all if not provided"),
    db: AsyncSession = Depends(get_db_session)
):
    """Clear schedule execution history"""
    if schedule_id:
        # Clear history for specific schedule
        stmt = delete(ScheduleExecutionModel).where(ScheduleExecutionModel.schedule_id == schedule_id)
        result = await db.execute(stmt)
        count = result.rowcount
        await db.commit()
        return {
            "message": f"Cleared {count} execution records for schedule",
            "count": count,
            "schedule_id": schedule_id
        }
    else:
        # Clear all history
        stmt = delete(ScheduleExecutionModel)
        result = await db.execute(stmt)
        count = result.rowcount
        await db.commit()
        return {
            "message": f"Cleared {count} execution records",
            "count": count
        }


@router.get("/{schedule_id}/debug")
async def debug_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Debug why a schedule is or isn't running"""
    stmt = select(ScheduleModel).where(ScheduleModel.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    from datetime import datetime, timezone
    from croniter import croniter
    from datetime import timedelta
    
    current_time = datetime.now(timezone.utc)
    
    # Get cron information
    try:
        cron = croniter(schedule.cron_expression, current_time)
        prev_run = cron.get_prev(datetime)
        next_run = cron.get_next(datetime)
        
        # Make timezone aware
        if prev_run.tzinfo is None:
            prev_run = prev_run.replace(tzinfo=timezone.utc)
        if next_run.tzinfo is None:
            next_run = next_run.replace(tzinfo=timezone.utc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cron expression: {e}")
    
    # Check for recent executions
    time_buffer = timedelta(minutes=10)
    earliest_time = prev_run - time_buffer
    
    stmt = select(ScheduleExecutionModel).where(
        and_(
            ScheduleExecutionModel.schedule_id == schedule.id,
            ScheduleExecutionModel.created_at >= earliest_time,
            ScheduleExecutionModel.created_at <= current_time
        )
    ).order_by(desc(ScheduleExecutionModel.created_at))
    result = await db.execute(stmt)
    recent_executions = result.scalars().all()
    
    # Get latest execution
    stmt = select(ScheduleExecutionModel).where(
        ScheduleExecutionModel.schedule_id == schedule.id
    ).order_by(desc(ScheduleExecutionModel.created_at)).limit(1)
    result = await db.execute(stmt)
    latest_execution = result.scalar_one_or_none()
    
    # Calculate status
    time_since_scheduled = current_time - prev_run
    is_overdue = time_since_scheduled > timedelta(minutes=15)  # Consider overdue after 15 minutes
    should_have_run = len(recent_executions) == 0
    
    # Parse latest execution items_processed if available
    latest_processing_info = None
    if latest_execution and latest_execution.items_processed:
        try:
            import json
            latest_processing_info = json.loads(latest_execution.items_processed)
        except:
            latest_processing_info = {"error": "Could not parse processing info"}
    
    debug_info = {
        "schedule": {
            "id": str(schedule.id),
            "name": schedule.name,
            "enabled": schedule.enabled,
            "cron_expression": schedule.cron_expression,
            "timezone": schedule.timezone,
            "target_libraries": schedule.target_libraries,
            "badge_types": schedule.badge_types,
            "reprocess_all": schedule.reprocess_all
        },
        "timing": {
            "current_time_utc": current_time.isoformat(),
            "previous_scheduled_run_utc": prev_run.isoformat(),
            "next_scheduled_run_utc": next_run.isoformat(),
            "time_since_scheduled": str(time_since_scheduled),
            "is_overdue": is_overdue,
            "should_have_run": should_have_run
        },
        "execution_status": {
            "recent_executions_count": len(recent_executions),
            "latest_execution": {
                "id": str(latest_execution.id) if latest_execution else None,
                "status": latest_execution.status if latest_execution else None,
                "created_at": latest_execution.created_at.isoformat() if latest_execution else None,
                "processing_info": latest_processing_info
            }
        },
        "diagnosis": []
    }
    
    # Add diagnostic messages
    if not schedule.enabled:
        debug_info["diagnosis"].append({
            "level": "error",
            "message": "Schedule is disabled. Enable it to start automatic execution."
        })
    
    if not schedule.target_libraries:
        debug_info["diagnosis"].append({
            "level": "error",
            "message": "No target libraries configured. Add libraries to process."
        })
    
    if should_have_run and schedule.enabled:
        if is_overdue:
            debug_info["diagnosis"].append({
                "level": "error",
                "message": f"Schedule is overdue by {time_since_scheduled}. Check if scheduler service is running."
            })
        else:
            debug_info["diagnosis"].append({
                "level": "warning",
                "message": f"Schedule should run soon (last scheduled: {time_since_scheduled} ago)."
            })
    
    if latest_processing_info:
        total_items = latest_processing_info.get("total_items", 0)
        processed_items = latest_processing_info.get("processed_items", 0)
        created_jobs = latest_processing_info.get("created_jobs", [])
        
        if total_items > 0 and processed_items == 0:
            if not schedule.reprocess_all:
                debug_info["diagnosis"].append({
                    "level": "info",
                    "message": f"Found {total_items} items but processed none. This is normal if all items already have badges (reprocess_all=false)."
                })
            else:
                debug_info["diagnosis"].append({
                    "level": "error",
                    "message": f"Found {total_items} items but processed none despite reprocess_all=true. Check logs for errors."
                })
        
        if len(created_jobs) == 0 and processed_items > 0:
            debug_info["diagnosis"].append({
                "level": "error",
                "message": "Items were marked for processing but no jobs were created. Check job system."
            })
    
    if not debug_info["diagnosis"]:
        debug_info["diagnosis"].append({
            "level": "success",
            "message": "No issues detected. Schedule appears to be configured correctly."
        })
    
    return debug_info
