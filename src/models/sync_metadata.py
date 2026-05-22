from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )

    last_sync_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sync_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )