"""base

Revision ID: d892947e929a
Revises: b36d972e8c9e
Create Date: 2025-10-28 03:51:58.862665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd892947e929a'
down_revision: Union[str, None] = 'b36d972e8c9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass