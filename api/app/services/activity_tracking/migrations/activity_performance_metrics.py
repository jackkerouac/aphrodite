"""
Activity Performance Metrics Migration

Creates the activity_performance_metrics table with proper foreign keys and indexes.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from aphrodite_logging import get_logger


class ActivityPerformanceMetricsMigration:
    """Migration for activity_performance_metrics table"""
    
    @staticmethod
    async def create_table(db_session: AsyncSession) -> bool:
        """Create the activity_performance_metrics table"""
        logger = get_logger("aphrodite.migration.performance_metrics", service="migration")
        
        try:
            # Create the table with proper foreign keys and indexes
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS activity_performance_metrics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                activity_id UUID NOT NULL REFERENCES media_activities(id) ON DELETE CASCADE,
                
                -- System Performance
                cpu_usage_percent DECIMAL(5,2),
                memory_usage_mb INTEGER,
                disk_io_read_mb DECIMAL(8,2),
                disk_io_write_mb DECIMAL(8,2),
                
                -- Network Performance
                network_download_mb DECIMAL(8,2),
                network_upload_mb DECIMAL(8,2),
                network_latency_ms INTEGER,
                
                -- Processing Stages
                stage_timings JSONB,
                bottleneck_stage VARCHAR(50),
                
                -- Quality Metrics
                error_rate DECIMAL(3,2),
                throughput_items_per_second DECIMAL(6,2),
                
                -- Environment
                server_load_average DECIMAL(4,2),
                concurrent_operations INTEGER,
                
                -- Timestamp
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
            """
            
            await db_session.execute(text(create_table_sql))
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_activity ON activity_performance_metrics(activity_id);",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_created_at ON activity_performance_metrics(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_cpu_usage ON activity_performance_metrics(cpu_usage_percent);",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_memory_usage ON activity_performance_metrics(memory_usage_mb);",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_bottleneck ON activity_performance_metrics(bottleneck_stage);"
            ]
            
            for index_sql in indexes:
                await db_session.execute(text(index_sql))
            
            await db_session.commit()
            logger.info("Created activity_performance_metrics table with indexes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create activity_performance_metrics table: {e}")
            await db_session.rollback()
            return False
    
    @staticmethod
    async def table_exists(db_session: AsyncSession) -> bool:
        """Check if the activity_performance_metrics table exists"""
        try:
            result = await db_session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'activity_performance_metrics'
                );
            """))
            return result.scalar()
        except Exception:
            return False
    
    @staticmethod
    async def drop_table(db_session: AsyncSession) -> bool:
        """Drop the activity_performance_metrics table (for cleanup)"""
        logger = get_logger("aphrodite.migration.performance_metrics", service="migration")
        
        try:
            await db_session.execute(text("DROP TABLE IF EXISTS activity_performance_metrics CASCADE;"))
            await db_session.commit()
            logger.info("Dropped activity_performance_metrics table")
            return True
        except Exception as e:
            logger.error(f"Failed to drop activity_performance_metrics table: {e}")
            await db_session.rollback()
            return False
