from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.ticket_id == ticket_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        await self.db.flush()
        return ticket

    async def delete(self, ticket: Ticket) -> None:
        await self.db.delete(ticket)
