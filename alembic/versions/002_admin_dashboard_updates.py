"""Add admin dashboard fields to engineer applications

Revision ID: 002_admin_dashboard_updates
Revises: 001_add_user_fields
Create Date: 2025-08-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002_admin_dashboard_updates'
down_revision = '001_add_user_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add new fields to engineer_applications table for admin dashboard."""
    # Add new columns to engineer_applications table
    op.add_column('engineer_applications', sa.Column('department', sa.String(100), nullable=True))
    op.add_column('engineer_applications', sa.Column('experience', sa.String(50), nullable=True))
    op.add_column('engineer_applications', sa.Column('skills', sa.Text(), nullable=True))
    op.add_column('engineer_applications', sa.Column('portfolio', sa.String(500), nullable=True))
    op.add_column('engineer_applications', sa.Column('cover_letter', sa.Text(), nullable=True))
    op.add_column('engineer_applications', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.add_column('engineer_applications', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add foreign key constraint for reviewer_id
    op.create_foreign_key(
        'fk_engineer_applications_reviewer_id',
        'engineer_applications',
        'users',
        ['reviewer_id'],
        ['id']
    )


def downgrade():
    """Remove admin dashboard fields from engineer_applications table."""
    # Drop foreign key constraint
    op.drop_constraint('fk_engineer_applications_reviewer_id', 'engineer_applications', type_='foreignkey')
    
    # Remove columns
    op.drop_column('engineer_applications', 'reviewed_at')
    op.drop_column('engineer_applications', 'reviewer_id')
    op.drop_column('engineer_applications', 'cover_letter')
    op.drop_column('engineer_applications', 'portfolio')
    op.drop_column('engineer_applications', 'skills')
    op.drop_column('engineer_applications', 'experience')
    op.drop_column('engineer_applications', 'department')
