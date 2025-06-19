"""
Performance indexes for workflow tables

Adds optimized indexes for common query patterns.
"""

from alembic import op


def upgrade():
    """Add performance indexes"""
    
    # Composite indexes for common queries
    op.create_index('idx_user_status', 'batch_jobs', ['user_id', 'status'])
    op.create_index('idx_priority_created', 'batch_jobs', ['priority', 'created_at'])
    op.create_index('idx_job_status', 'poster_processing_status', ['batch_job_id', 'status'])
    op.create_index('idx_poster_job', 'poster_processing_status', ['poster_id', 'batch_job_id'])


def downgrade():
    """Remove performance indexes"""
    op.drop_index('idx_poster_job', 'poster_processing_status')
    op.drop_index('idx_job_status', 'poster_processing_status')
    op.drop_index('idx_priority_created', 'batch_jobs')
    op.drop_index('idx_user_status', 'batch_jobs')
