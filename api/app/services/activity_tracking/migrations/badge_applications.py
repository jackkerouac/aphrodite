"""
Migration for badge_applications table - Phase 2 of Activity Tracking
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class BadgeApplicationsMigration:
    """Handles creation and management of badge_applications table"""
    
    @staticmethod
    async def create_table(db_session: AsyncSession) -> bool:
        """Create the badge_applications table"""
        try:
            create_sql = text("""
                CREATE TABLE IF NOT EXISTS badge_applications (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    activity_id UUID NOT NULL,
                    
                    -- Badge Configuration
                    badge_types JSONB NOT NULL,
                    badge_settings_snapshot JSONB,
                    badge_configuration_id VARCHAR(50),
                    
                    -- Processing Details
                    poster_source VARCHAR(100),
                    original_poster_path TEXT,
                    output_poster_path TEXT,
                    intermediate_files JSONB,
                    
                    -- Badge Results
                    badges_applied JSONB,
                    badges_failed JSONB,
                    final_poster_dimensions VARCHAR(20),
                    final_file_size INTEGER,
                    
                    -- Performance Metrics
                    badge_generation_time_ms INTEGER,
                    poster_processing_time_ms INTEGER,
                    total_processing_time_ms INTEGER,
                    
                    -- Quality Metrics
                    poster_quality_score DECIMAL(3,2),
                    compression_ratio DECIMAL(5,2),
                    
                    -- Timestamps
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    
                    CONSTRAINT fk_badge_applications_activity 
                        FOREIGN KEY (activity_id) REFERENCES media_activities(id) ON DELETE CASCADE
                );
            """)
            
            await db_session.execute(create_sql)
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_badge_applications_activity ON badge_applications(activity_id);",
                "CREATE INDEX IF NOT EXISTS idx_badge_applications_types ON badge_applications USING GIN(badge_types);",
                "CREATE INDEX IF NOT EXISTS idx_badge_applications_created_at ON badge_applications(created_at);"
            ]
            
            for index_sql in indexes:
                await db_session.execute(text(index_sql))
            
            await db_session.commit()
            return True
            
        except Exception as e:
            await db_session.rollback()
            print(f"Failed to create badge_applications table: {e}")
            return False
    
    @staticmethod
    async def drop_table(db_session: AsyncSession) -> bool:
        """Drop the badge_applications table"""
        try:
            drop_sql = text("DROP TABLE IF EXISTS badge_applications CASCADE;")
            await db_session.execute(drop_sql)
            await db_session.commit()
            return True
            
        except Exception as e:
            await db_session.rollback()
            print(f"Failed to drop badge_applications table: {e}")
            return False
    
    @staticmethod
    async def table_exists(db_session: AsyncSession) -> bool:
        """Check if badge_applications table exists"""
        try:
            check_sql = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'badge_applications'
                );
            """)
            result = await db_session.execute(check_sql)
            return result.scalar()
            
        except Exception:
            return False
