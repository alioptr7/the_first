import uuid
from sqlalchemy import String, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base, TimestampMixin
from db.models.enums import RequestStatus


class Request(Base, TimestampMixin):
    """
    Represents a user's query request.
    """

    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    query_type: Mapped[str] = mapped_column(String(50), nullable=False)
    query_params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status_enum", create_type=True),
        default=RequestStatus.PENDING,
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="requests", lazy="selectin")

    def __repr__(self):
        return f"<Request(id={self.id}, status='{self.status.value}')>"