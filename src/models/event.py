from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Event(Base):
    __tablename__ = "events"

    __table_args__ = (
        Index("idx_events_event_time", "event_time"),
        Index("idx_events_changed_at", "changed_at"),
        Index("idx_events_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    place_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("places.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    number_of_visitors: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    place: Mapped["Place"] = relationship(
        back_populates="events",
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )