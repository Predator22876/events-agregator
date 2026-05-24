from datetime import date
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.event_repository import EventRepository


class EventService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = EventRepository(db)

    async def list_events(
        self,
        date_from: date | None,
        page: int,
        page_size: int,
    ) -> Tuple[int, list]:
        offset = (page - 1) * page_size
        total = await self.repo.count_events(date_from)
        events = await self.repo.list_events(date_from, offset, page_size)
        return total, events

    async def get_event(self, event_id: str):
        return await self.repo.get_by_id(event_id)
