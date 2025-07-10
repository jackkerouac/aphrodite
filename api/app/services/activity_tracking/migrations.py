"""
Activity Tracking Database Migration

Creates all activity tracking tables:
- Phase 1: media_activities (core activity tracking)
- Phase 2: badge_applications (detailed badge tracking)
- Phase 3: poster_replacements (detailed replacement tracking)
- Phase 5: activity_performance_metrics (performance analytics)
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


# Phase 3: Poster Replacements Migration
def upgrade_poster_replacements():
    """Create poster_replacements table"""
    
    op.create_table(
        'poster_replacements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('activity_id', UUID(as_uuid=True), nullable=False),
        
        # Source Information
        sa.Column('replacement_source', sa.String(50), nullable=False),
        sa.Column('source_poster_id', sa.String(100), nullable=True),
        sa.Column('source_poster_url', sa.Text(), nullable=True),
        sa.Column('search_query', sa.Text(), nullable=True),
        sa.Column('search_results_count', sa.Integer(), nullable=True),
        
        # Original Poster Info
        sa.Column('original_poster_url', sa.Text(), nullable=True),
        sa.Column('original_poster_cached_path', sa.Text(), nullable=True),
        sa.Column('original_poster_dimensions', sa.String(20), nullable=True),
        sa.Column('original_file_size', sa.Integer(), nullable=True),
        sa.Column('original_poster_hash', sa.String(64), nullable=True),
        
        # New Poster Info
        sa.Column('new_poster_dimensions', sa.String(20), nullable=True),
        sa.Column('new_file_size', sa.Integer(), nullable=True),
        sa.Column('new_poster_hash', sa.String(64), nullable=True),
        sa.Column('download_time_ms', sa.Integer(), nullable=True),
        sa.Column('upload_time_ms', sa.Integer(), nullable=True),
        
        # Jellyfin Integration
        sa.Column('jellyfin_upload_success', sa.Boolean(), nullable=True),
        sa.Column('tag_operations', JSONB, nullable=True),
        sa.Column('jellyfin_response', JSONB, nullable=True),
        
        # Quality Assessment
        sa.Column('quality_improvement_score', sa.DECIMAL(3, 2), nullable=True),
        sa.Column('visual_similarity_score', sa.DECIMAL(3, 2), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['activity_id'], ['media_activities.id'], ondelete='CASCADE'),
    )
    
    # Additional indexes
    op.create_index('idx_poster_replacements_activity', 'poster_replacements', ['activity_id'])
    op.create_index('idx_poster_replacements_source', 'poster_replacements', ['replacement_source'])
    op.create_index('idx_poster_replacements_created_at', 'poster_replacements', ['created_at'])


def downgrade_poster_replacements():
    """Drop poster_replacements table"""
    op.drop_table('poster_replacements')


# Phase 5: Performance Metrics Migration
def upgrade_activity_performance_metrics():
    """Create activity_performance_metrics table"""
    
    op.create_table(
        'activity_performance_metrics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('activity_id', UUID(as_uuid=True), nullable=False),
        
        # System Performance
        sa.Column('cpu_usage_percent', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('memory_usage_mb', sa.Integer(), nullable=True),
        sa.Column('disk_io_read_mb', sa.DECIMAL(8, 2), nullable=True),
        sa.Column('disk_io_write_mb', sa.DECIMAL(8, 2), nullable=True),
        
        # Network Performance
        sa.Column('network_download_mb', sa.DECIMAL(8, 2), nullable=True),
        sa.Column('network_upload_mb', sa.DECIMAL(8, 2), nullable=True),
        sa.Column('network_latency_ms', sa.Integer(), nullable=True),
        
        # Processing Stages
        sa.Column('stage_timings', JSONB, nullable=True),
        sa.Column('bottleneck_stage', sa.String(50), nullable=True),
        
        # Quality Metrics
        sa.Column('error_rate', sa.DECIMAL(3, 2), nullable=True),
        sa.Column('throughput_items_per_second', sa.DECIMAL(6, 2), nullable=True),
        
        # Environment
        sa.Column('server_load_average', sa.DECIMAL(4, 2), nullable=True),
        sa.Column('concurrent_operations', sa.Integer(), nullable=True),
        
        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['activity_id'], ['media_activities.id'], ondelete='CASCADE'),
    )
    
    # Additional indexes
    op.create_index('idx_performance_metrics_activity', 'activity_performance_metrics', ['activity_id'])
    op.create_index('idx_performance_metrics_created_at', 'activity_performance_metrics', ['created_at'])


def downgrade_activity_performance_metrics():
    """Drop activity_performance_metrics table"""
    op.drop_table('activity_performance_metrics')


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
                
            if 'poster_replacements' not in table_names:
                logger.info("Creating poster_replacements table...")
                upgrade_poster_replacements()
                logger.info("poster_replacements table created successfully")
            else:
                logger.info("poster_replacements table already exists")
                
            if 'activity_performance_metrics' not in table_names:
                logger.info("Creating activity_performance_metrics table...")
                upgrade_activity_performance_metrics()
                logger.info("activity_performance_metrics table created successfully")
            else:
                logger.info("activity_performance_metrics table already exists")
    
    return check_and_create()
