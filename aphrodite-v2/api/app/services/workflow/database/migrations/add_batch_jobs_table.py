"""
Initial workflow database tables

Creates batch_jobs and poster_processing_status tables.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


def upgrade():
    """Create workflow tables"""
    
    # Create batch_jobs table
    op.create_table(
        'batch_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source', sa.String(50), nullable=False, index=True),
        sa.Column('total_posters', sa.Integer(), nullable=False),
        sa.Column('completed_posters', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_posters', sa.Integer(), nullable=False, default=0),
        sa.Column('status', sa.String(50), nullable=False, default='queued', index=True),
        sa.Column('priority', sa.Integer(), nullable=False, default=5, index=True),
        sa.Column('badge_types', sa.JSON(), nullable=False),
        sa.Column('selected_poster_ids', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('estimated_completion', sa.DateTime(), nullable=True),
        sa.Column('error_summary', sa.Text(), nullable=True)
    )
    
    # Create poster_processing_status table
    op.create_table(
        'poster_processing_status',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('batch_job_id', sa.String(36), nullable=False),
        sa.Column('poster_id', sa.String(36), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('output_path', sa.String(500), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.ForeignKeyConstraint(['batch_job_id'], ['batch_jobs.id'], ondelete='CASCADE')
    )


def downgrade():
    """Drop workflow tables"""
    op.drop_table('poster_processing_status')
    op.drop_table('batch_jobs')
