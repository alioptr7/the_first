"""Update request type and access models

Revision ID: cf4f98a0422f
Revises: add_user_request_access
Create Date: 2025-11-09 05:54:25.479382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf4f98a0422f'
down_revision: Union[str, None] = 'add_user_request_access'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
