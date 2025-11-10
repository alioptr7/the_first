from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from shared.database.base import metadata

# Association table for request_types and validation_rules
request_type_validation_rules = Table(
    "request_type_validation_rules",
    metadata,
    Column("request_type_id", PGUUID, ForeignKey("request_types.id", ondelete="CASCADE"), primary_key=True),
    Column("validation_rule_id", PGUUID, ForeignKey("validation_rules.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("request_type_id", "validation_rule_id", name="uq_request_type_validation_rule")
)