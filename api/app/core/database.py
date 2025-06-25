"""
Database Configuration and Session Management

Async PostgreSQL database setup with SQLAlchemy 2.0 and connection pooling.
"""

import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.config import get_settings
from aphrodite_logging import get_logger

# Create base class for models
Base = declarative_base()

# Global variables
async_engine: Optional[Engine] = None
async_session_factory: Optional[async_sessionmaker] = None

# Connection recovery utilities
def reset_database_connections():
    """Reset all database connections (for error recovery)"""
    global async_engine, async_session_factory
    
    logger = get_logger("aphrodite.database.recovery", service="database")
    logger.warning("Resetting database connections for error recovery")
    
    if async_engine:
        # Schedule engine disposal for next event loop iteration
        import asyncio
        asyncio.create_task(async_engine.dispose())
    
    async_engine = None
    async_session_factory = None

def get_engine() -> Engine:
    """Get the async database engine"""
    global async_engine
    if async_engine is None:
        settings = get_settings()
        # Use the new method that handles both Docker and local development
        database_url = settings.get_database_url()
        
        async_engine = create_async_engine(
            database_url,
            echo=settings.debug,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
            # CRITICAL FIX: Add connection error recovery options
            pool_reset_on_return='commit',
            pool_timeout=30,
            connect_args={
                "server_settings": {
                    "application_name": "aphrodite_v2",
                    "jit": "off"
                }
            },
            poolclass=NullPool if settings.environment == "testing" else None
        )
    return async_engine

def create_fresh_engine() -> Engine:
    """Create a completely new engine instance for connection recovery"""
    settings = get_settings()
    database_url = settings.get_database_url()
    
    return create_async_engine(
        database_url,
        echo=settings.debug,
        pool_size=5,  # Smaller pool for fresh connections
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=1800,  # Shorter recycle time
        pool_reset_on_return='commit',
        pool_timeout=20,
        connect_args={
            "server_settings": {
                "application_name": "aphrodite_v2_recovery",
                "jit": "off"
            }
        }
    )

async def init_db() -> None:
    """Initialize database connection and create tables"""
    global async_engine, async_session_factory
    
    logger = get_logger("aphrodite.database", service="database")
    
    try:
        # Get or create async engine
        async_engine = get_engine()
        
        # Create session factory
        async_session_factory = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Import all models to ensure they're registered
        from app.models import media, jobs, config, schedules
        from app.services.workflow.database.models import BatchJobModel, PosterProcessingStatusModel
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise

async def close_db() -> None:
    """Close database connections"""
    global async_engine
    
    logger = get_logger("aphrodite.database", service="database")
    
    if async_engine:
        await async_engine.dispose()
        logger.info("Database connections closed")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection with error recovery
    
    Yields:
        AsyncSession: Database session
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized")
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async with async_session_factory() as session:
                # Test the connection
                from sqlalchemy import text
                await session.execute(text("SELECT 1"))
                yield session
                break
        except Exception as e:
            retry_count += 1
            logger = get_logger("aphrodite.database.session", service="database")
            logger.warning(f"Database session attempt {retry_count} failed: {e}")
            
            if retry_count >= max_retries:
                logger.error(f"Failed to create database session after {max_retries} attempts")
                raise
            
            # Wait before retry
            import asyncio
            await asyncio.sleep(0.5 * retry_count)

async def get_fresh_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a completely fresh database session using a new engine
    
    Yields:
        AsyncSession: Fresh database session
    """
    fresh_engine = create_fresh_engine()
    fresh_session_factory = async_sessionmaker(
        fresh_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    try:
        async with fresh_session_factory() as session:
            # Test the connection
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            yield session
    finally:
        await fresh_engine.dispose()

class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    async def health_check() -> dict:
        """Check database health with multiple strategies"""
        logger = get_logger("aphrodite.database.health", service="database")
        
        try:
            if not async_engine:
                return {"status": "error", "message": "Database not initialized"}
            
            # Test connection using multiple strategies
            strategies = [
                ("main_engine", async_engine),
                ("fresh_engine", create_fresh_engine())
            ]
            
            for strategy_name, engine in strategies:
                try:
                    from sqlalchemy import text
                    async with engine.begin() as conn:
                        result = await conn.execute(text("SELECT 1"))
                        result.fetchone()
                    
                    logger.info(f"Database health check successful using {strategy_name}")
                    return {"status": "healthy", "message": f"Database connection successful ({strategy_name})"}
                    
                except Exception as strategy_error:
                    logger.warning(f"Database health check failed with {strategy_name}: {strategy_error}")
                    if strategy_name == "fresh_engine":
                        await engine.dispose()
                    continue
            
            return {"status": "error", "message": "All database connection strategies failed"}
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "error", "message": f"Database connection failed: {str(e)}"}
    
    @staticmethod
    async def get_connection_info() -> dict:
        """Get database connection information"""
        settings = get_settings()
        
        if not async_engine:
            return {"status": "not_initialized"}
        
        pool = async_engine.pool
        
        return {
            "status": "initialized",
            "url": settings.database_url.split('@')[1] if '@' in settings.database_url else "hidden",
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_in": pool.checkedin()
        }

# Event listeners for logging
@event.listens_for(Engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """Log database connections"""
    logger = get_logger("aphrodite.database.connection", service="database")
    logger.debug("New database connection established")

@event.listens_for(Engine, "checkout")
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout"""
    logger = get_logger("aphrodite.database.pool", service="database")
    logger.debug("Database connection checked out from pool")

@event.listens_for(Engine, "checkin")
def on_checkin(dbapi_connection, connection_record):
    """Log connection checkin"""
    logger = get_logger("aphrodite.database.pool", service="database")
    logger.debug("Database connection returned to pool")

@event.listens_for(Engine, "invalidate")
def on_invalidate(dbapi_connection, connection_record, exception):
    """Log connection invalidation"""
    logger = get_logger("aphrodite.database.connection", service="database")
    logger.warning(f"Database connection invalidated: {exception}")

@event.listens_for(Engine, "soft_invalidate")
def on_soft_invalidate(dbapi_connection, connection_record, exception):
    """Log soft connection invalidation"""
    logger = get_logger("aphrodite.database.connection", service="database")
    logger.warning(f"Database connection soft invalidated: {exception}")
