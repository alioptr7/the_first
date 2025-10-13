"""Create batch management tables

Revision ID: d1eca0e3b964
Revises: 31cd7d080fb2
Create Date: 2025-10-13 11:21:22.449398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1eca0e3b964'
down_revision: Union[str, None] = '31cd7d080fb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass