"""Create cache and log tables

Revision ID: 831f290ef30e
Revises: 8bfa1b693f7a
Create Date: 2025-10-13 12:24:50.017421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '831f290ef30e'
down_revision: Union[str, None] = '8bfa1b693f7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass