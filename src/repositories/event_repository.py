from datetime import date, datetime, time, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.event import Event


class EventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_events(
        self,
        date_from: date | None,
        offset: int,
        limit: int,
    ) -> list[Event]:
        stmt = (
            select(Event).options(selectinload(Event.place)).order_by(Event.event_time)
        )

        if date_from is not None:
            boundary = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            stmt = stmt.where(Event.event_time >= boundary)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_events(self, date_from: date | None) -> int:
        stmt = select(func.count()).select_from(Event)

        if date_from is not None:
            boundary = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            stmt = stmt.where(Event.event_time >= boundary)

        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, event_id: str) -> Event | None:
        stmt = (
            select(Event).options(selectinload(Event.place)).where(Event.id == event_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
