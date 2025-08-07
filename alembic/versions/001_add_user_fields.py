"""Add customer and engineer fields to users table

Revision ID: 001_add_user_fields
Revises: 
Create Date: 2025-08-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_user_fields'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add customer specific fields
    op.add_column('users', sa.Column('machine_model', sa.String(200), nullable=True))
    op.add_column('users', sa.Column('state', sa.String(100), nullable=True))
    
    # Add engineer specific fields
    op.add_column('users', sa.Column('department', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('dealer', sa.String(200), nullable=True))


def downgrade() -> None:
    # Remove customer specific fields
    op.drop_column('users', 'machine_model')
    op.drop_column('users', 'state')
    
    # Remove engineer specific fields
    op.drop_column('users', 'department')
    op.drop_column('users', 'dealer')
