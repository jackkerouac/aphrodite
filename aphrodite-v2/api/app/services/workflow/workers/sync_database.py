"""
Synchronous Database Operations for Celery Worker

Provides sync database operations to avoid event loop conflicts in Celery tasks.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, select, update, insert
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.core.config import get_settings
from app.services.workflow.database.models import BatchJobModel, PosterProcessingStatusModel
from app.services.workflow.types import JobStatus, PosterStatus
from aphrodite_logging import get_logger

logger = get_logger("aphrodite.worker.sync_db")

class SyncJobRepository:
    """Synchronous job repository for Celery workers"""
    
    def __init__(self):
        """Initialize sync database connection"""
        settings = get_settings()
        # Convert async URL to sync URL
        sync_url = settings.database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        self.engine = create_engine(
            sync_url,
            echo=settings.debug,
            pool_size=2,  # Smaller pool for worker
            max_overflow=1,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_job_by_id(self, job_id: str) -> Optional[BatchJobModel]:
        """Get job by ID"""
        with self.get_session() as session:
            return session.query(BatchJobModel).filter(
                BatchJobModel.id == job_id
            ).first()
    
    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """Update job status"""
        with self.get_session() as session:
            result = session.query(BatchJobModel).filter(
                BatchJobModel.id == job_id
            ).update({"status": status.value})
            return result > 0
    
    def update_job_started_at(self, job_id: str, started_at: datetime) -> bool:
        """Update job started timestamp"""
        with self.get_session() as session:
            result = session.query(BatchJobModel).filter(
                BatchJobModel.id == job_id
            ).update({"started_at": started_at})
            return result > 0
    
    def update_job_completed_at(self, job_id: str, completed_at: datetime) -> bool:
        """Update job completed timestamp"""
        with self.get_session() as session:
            result = session.query(BatchJobModel).filter(
                BatchJobModel.id == job_id
            ).update({"completed_at": completed_at})
            return result > 0
    
    def update_job_progress(self, job_id: str, completed: int, failed: int) -> bool:
        """Update job progress counters"""
        with self.get_session() as session:
            result = session.query(BatchJobModel).filter(
                BatchJobModel.id == job_id
            ).update({
                "completed_posters": completed,
                "failed_posters": failed
            })
            return result > 0
    
    def update_job_error(self, job_id: str, error_message: str) -> bool:
        """Update job error message"""
        with self.get_session() as session:
            result = session.query(BatchJobModel).filter(
                BatchJobModel.id == job_id
            ).update({"error_summary": error_message})
            return result > 0
    
    def update_poster_status(
        self, 
        job_id: str, 
        poster_id: str, 
        status: PosterStatus,
        output_path: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update poster processing status"""
        with self.get_session() as session:
            # Try to find existing status record
            existing = session.query(PosterProcessingStatusModel).filter(
                PosterProcessingStatusModel.batch_job_id == job_id,
                PosterProcessingStatusModel.poster_id == poster_id
            ).first()
            
            if existing:
                # Update existing record
                update_data = {"status": status.value}
                if output_path:
                    update_data["output_path"] = output_path
                if error_message:
                    update_data["error_message"] = error_message
                if status == PosterStatus.PROCESSING:
                    update_data["started_at"] = datetime.utcnow()
                elif status in [PosterStatus.COMPLETED, PosterStatus.FAILED]:
                    update_data["completed_at"] = datetime.utcnow()
                
                session.query(PosterProcessingStatusModel).filter(
                    PosterProcessingStatusModel.id == existing.id
                ).update(update_data)
            else:
                # Create new record
                new_status = PosterProcessingStatusModel(
                    batch_job_id=job_id,
                    poster_id=poster_id,
                    status=status.value,
                    output_path=output_path,
                    error_message=error_message,
                    started_at=datetime.utcnow() if status == PosterStatus.PROCESSING else None,
                    completed_at=datetime.utcnow() if status in [PosterStatus.COMPLETED, PosterStatus.FAILED] else None
                )
                session.add(new_status)
            
            return True
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.debug("Sync database connections closed")
