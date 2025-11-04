"""add profile_type to user

Revision ID: e453d4e36baa
Revises: 5415c9300ae2
Create Date: 2025-11-03 13:04:12.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e453d4e36baa'
down_revision: Union[str, None] = '5415c9300ae2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add profile_type column as nullable first
    op.add_column('users', sa.Column('profile_type', sa.String(50), nullable=True))
    
    # Update existing rows with default value
    op.execute("UPDATE users SET profile_type = 'basic' WHERE profile_type IS NULL")
    
    # Make the column not nullable
    op.alter_column('users', 'profile_type',
                    existing_type=sa.String(50),
                    nullable=False,
                    server_default='basic')


def downgrade() -> None:
    op.drop_column('users', 'profile_type')