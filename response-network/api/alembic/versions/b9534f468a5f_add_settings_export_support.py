"""Add settings export support

Revision ID: b9534f468a5f
Revises: cf4f98a0422f
Create Date: 2025-11-09 21:22:12.394570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9534f468a5f'
down_revision: Union[str, None] = 'cf4f98a0422f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_public column to settings table
    op.add_column('settings', sa.Column('is_public', sa.Boolean(), nullable=True))
    
    # Update existing rows to set is_public = false
    op.execute("UPDATE settings SET is_public = false")
    
    # Make is_public non-nullable
    op.alter_column('settings', 'is_public',
               existing_type=sa.Boolean(),
               nullable=False)


def downgrade() -> None:
    op.drop_column('settings', 'is_public')
