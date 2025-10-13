"""Create batch management tables

Revision ID: 31cd7d080fb2
Revises: db0a7d458bb7
Create Date: 2025-10-13 11:06:06.190889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31cd7d080fb2'
down_revision: Union[str, None] = 'db0a7d458bb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass