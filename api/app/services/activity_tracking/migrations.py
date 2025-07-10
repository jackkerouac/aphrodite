"""
Activity Tracking Database Migration

Creates the media_activities table for Phase 1 of the activity tracking system.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


def upgrade_media_activities():
    """Create media_activities table"""
    
    op.create_table(
        'media_activities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('media_id', sa.String(36), nullable=False, index=True),
        sa.Column('jellyfin_id', sa.String(100), nullable=True, index=True),
        sa.Column('activity_type', sa.String(50), nullable=False, index=True),
        sa.Column('activity_subtype', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending', index=True),
        
        # Operation Context
        sa.Column('initiated_by', sa.String(50), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('batch_job_id', sa.String(36), nullable=True, index=True),
        sa.Column('parent_activity_id', UUID(as_uuid=True), nullable=True),
        
        # Timing
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_duration_ms', sa.Integer(), nullable=True),
        
        # Input Parameters (JSON for flexibility)
        sa.Column('input_parameters', JSONB, nullable=True),
        
        # Results and Status
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('result_data', JSONB, nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        
        # Metadata
        sa.Column('system_version', sa.String(20), nullable=True),
        sa.Column('additional_metadata', JSONB, nullable=True),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['parent_activity_id'], ['media_activities.id']),
        
        # Indexes for performance
    )
    
    # Additional indexes
    op.create_index('idx_media_activities_media_id', 'media_activities', ['media_id'])
    op.create_index('idx_media_activities_type', 'media_activities', ['activity_type'])
    op.create_index('idx_media_activities_status', 'media_activities', ['status'])
    op.create_index('idx_media_activities_created_at', 'media_activities', ['created_at'])
    op.create_index('idx_media_activities_jellyfin_id', 'media_activities', ['jellyfin_id'])
    op.create_index('idx_media_activities_batch_job', 'media_activities', ['batch_job_id'])


def downgrade_media_activities():
    """Drop media_activities table"""
    op.drop_table('media_activities')


# Phase 2: Badge Applications Migration
def upgrade_badge_applications():
    """Create badge_applications table"""
    
    op.create_table(
        'badge_applications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('activity_id', UUID(as_uuid=True), nullable=False),
        
        # Badge Configuration
        sa.Column('badge_types', JSONB, nullable=False),
        sa.Column('badge_settings_snapshot', JSONB, nullable=True),
        sa.Column('badge_configuration_id', sa.String(50), nullable=True),
        
        # Processing Details
        sa.Column('poster_source', sa.String(100), nullable=True),
        sa.Column('original_poster_path', sa.Text(), nullable=True),
        sa.Column('output_poster_path', sa.Text(), nullable=True),
        sa.Column('intermediate_files', JSONB, nullable=True),
        
        # Badge Results
        sa.Column('badges_applied', JSONB, nullable=True),
        sa.Column('badges_failed', JSONB, nullable=True),
        sa.Column('final_poster_dimensions', sa.String(20), nullable=True),
        sa.Column('final_file_size', sa.Integer(), nullable=True),
        
        # Performance Metrics
        sa.Column('badge_generation_time_ms', sa.Integer(), nullable=True),
        sa.Column('poster_processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('total_processing_time_ms', sa.Integer(), nullable=True),
        
        # Quality Metrics
        sa.Column('poster_quality_score', sa.DECIMAL(3, 2), nullable=True),
        sa.Column('compression_ratio', sa.DECIMAL(5, 2), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['activity_id'], ['media_activities.id'], ondelete='CASCADE'),
    )
    
    # Additional indexes
    op.create_index('idx_badge_applications_activity', 'badge_applications', ['activity_id'])
    op.create_index('idx_badge_applications_types', 'badge_applications', ['badge_types'], postgresql_using='gin')
    op.create_index('idx_badge_applications_created_at', 'badge_applications', ['created_at'])


def downgrade_badge_applications():
    """Drop badge_applications table"""
    op.drop_table('badge_applications')


# Auto-run migration (this will be called from database initialization)
def run_migration():
    """Run the migration if the table doesn't exist"""
    import logging
    from sqlalchemy import inspect
    from app.core.database import get_engine
    
    logger = logging.getLogger(__name__)
    
    async def check_and_create():
        engine = get_engine()
        async with engine.begin() as conn:
            inspector = inspect(await conn.get_sync_connection())
            table_names = inspector.get_table_names()
            
            if 'media_activities' not in table_names:
                logger.info("Creating media_activities table...")
                upgrade_media_activities()
                logger.info("media_activities table created successfully")
            else:
                logger.info("media_activities table already exists")
                
            if 'badge_applications' not in table_names:
                logger.info("Creating badge_applications table...")
                upgrade_badge_applications()
                logger.info("badge_applications table created successfully")
            else:
                logger.info("badge_applications table already exists")
    
    return check_and_create()
