"""Add query template fields

Revision ID: 1234567890ab
Revises: 72deb3bc2fe3
Create Date: 2025-11-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = '72deb3bc2fe3'
branch_labels = None
depends_on = None


def upgrade():
    # Add elasticsearch_query_template to request_types table
    op.add_column('request_types', sa.Column('elasticsearch_query_template', postgresql.JSON, nullable=True))
    
    # Add placeholder_key to request_type_parameters table
    op.add_column('request_type_parameters', sa.Column('placeholder_key', sa.String(100), nullable=True))
    
    # Make the new columns required after existing data is migrated
    op.execute("""
        UPDATE request_types 
        SET elasticsearch_query_template = '{}'::json 
        WHERE elasticsearch_query_template IS NULL
    """)
    
    op.execute("""
        UPDATE request_type_parameters 
        SET placeholder_key = name 
        WHERE placeholder_key IS NULL
    """)
    
    op.alter_column('request_types', 'elasticsearch_query_template',
                    existing_type=postgresql.JSON,
                    nullable=False)
    
    op.alter_column('request_type_parameters', 'placeholder_key',
                    existing_type=sa.String(100),
                    nullable=False)


def downgrade():
    op.drop_column('request_type_parameters', 'placeholder_key')
    op.drop_column('request_types', 'elasticsearch_query_template')