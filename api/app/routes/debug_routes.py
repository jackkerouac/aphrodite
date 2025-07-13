"""
Debug endpoint to check workflow model availability
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
import logging

from ..core.database import get_db_session

router = APIRouter(prefix="/debug", tags=["debug"])
logger = logging.getLogger(__name__)

@router.get("/workflow-models")
async def check_workflow_models(db: AsyncSession = Depends(get_db_session)):
    """Debug endpoint to check if workflow models are available"""
    
    result = {
        "batch_job_model": False,
        "batch_job_table_exists": False,
        "batch_job_count": 0,
        "error": None
    }
    
    try:
        # Try to import BatchJobModel
        from app.services.workflow.database.models import BatchJobModel
        result["batch_job_model"] = True
        
        # Try to query the table
        count_result = await db.execute(select(func.count(BatchJobModel.id)))
        result["batch_job_count"] = count_result.scalar() or 0
        result["batch_job_table_exists"] = True
        
    except ImportError as e:
        result["error"] = f"Import error: {str(e)}"
    except Exception as e:
        result["error"] = f"Database error: {str(e)}"
    
    return result
