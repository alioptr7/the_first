"""ایجاد جدول کاربران به عنوان منبع حقیقت

Revision ID: 86b63da76484
Revises: 
Create Date: 2025-10-12 09:01:42.494750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86b63da76484'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass