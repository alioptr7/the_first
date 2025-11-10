"""Add user_request_access table

Revision ID: add_user_request_access
Revises: 1234567890ab
Create Date: 2025-11-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_request_access'
down_revision = '1234567890ab'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_request_access',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('max_requests_per_hour', sa.Integer(), nullable=False, default=100),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['request_type_id'], ['request_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(
        'ix_user_request_access_user_id',
        'user_request_access',
        ['user_id']
    )
    op.create_index(
        'ix_user_request_access_request_type_id',
        'user_request_access',
        ['request_type_id']
    )
    # Create unique constraint to prevent duplicate access records
    op.create_unique_constraint(
        'uq_user_request_access_user_request_type',
        'user_request_access',
        ['user_id', 'request_type_id']
    )


def downgrade():
    op.drop_table('user_request_access')