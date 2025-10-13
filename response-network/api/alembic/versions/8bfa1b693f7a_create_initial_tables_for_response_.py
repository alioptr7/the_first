"""Create initial tables for response network

Revision ID: 8bfa1b693f7a
Revises: d1eca0e3b964
Create Date: 2025-10-13 12:16:05.343865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bfa1b693f7a'
down_revision: Union[str, None] = 'd1eca0e3b964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass