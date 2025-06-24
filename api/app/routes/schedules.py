"""
Schedule management routes for Aphrodite v2
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field
import uuid

from ..core.database import get_db_session
from ..models.schedules import ScheduleModel, ScheduleExecutionModel
from ..services.jellyfin_service import get_jellyfin_service


router = APIRouter(prefix="/v1/schedules", tags=["schedules"])


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
    
    # Create execution record
    execution = ScheduleExecutionModel(
        schedule_id=schedule_id,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # TODO: Queue the actual schedule execution job here
    # This would integrate with the existing job system
    
    return {"message": "Schedule execution queued", "execution_id": str(execution.id)}
