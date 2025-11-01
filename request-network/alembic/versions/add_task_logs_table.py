"""Add task_logs table

Revision ID: add_task_logs_table
Create Date: 2024-03-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_task_logs_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'task_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['request_id'], ['requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_task_logs_request_id'),
        'task_logs',
        ['request_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_task_logs_task_name'),
        'task_logs',
        ['task_name'],
        unique=False
    )
    op.create_index(
        op.f('ix_task_logs_status'),
        'task_logs',
        ['status'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_task_logs_status'), table_name='task_logs')
    op.drop_index(op.f('ix_task_logs_task_name'), table_name='task_logs')
    op.drop_index(op.f('ix_task_logs_request_id'), table_name='task_logs')
    op.drop_table('task_logs')