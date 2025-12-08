"""add_profile_type_request_access_and_user_limits

Revision ID: 06eb34f02521
Revises: f0c11b666bb3
Create Date: 2025-12-04 05:35:45.953021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '06eb34f02521'
down_revision: Union[str, None] = 'f0c11b666bb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create profile_type_request_access table
    op.create_table('profile_type_request_access',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('profile_type_id', sa.String(50), nullable=False),
    sa.Column('request_type_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('max_requests_per_day', sa.Integer(), nullable=True),
    sa.Column('max_requests_per_month', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.ForeignKeyConstraint(['profile_type_id'], ['profile_type_configs.name'], ),
    sa.ForeignKeyConstraint(['request_type_id'], ['request_types.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('profile_type_id', 'request_type_id', name='uix_profile_request_type')
    )
    
    # Add limit columns to user_request_access table
    op.add_column('user_request_access', sa.Column('max_requests_per_day', sa.Integer(), nullable=True))
    op.add_column('user_request_access', sa.Column('max_requests_per_month', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove limit columns from user_request_access
    op.drop_column('user_request_access', 'max_requests_per_month')
    op.drop_column('user_request_access', 'max_requests_per_day')
    
    # Drop profile_type_request_access table
    op.drop_table('profile_type_request_access')
