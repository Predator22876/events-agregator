from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ticket import Ticket
from src.repositories.event_repository import EventRepository
from src.repositories.ticket_repository import TicketRepository
from src.schemas.ticket import TicketCreateRequest
from src.services.events_provider import EventsProviderClient


class TicketService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.event_repo = EventRepository(db)
        self.ticket_repo = TicketRepository(db)
        self.client = EventsProviderClient()

    async def create_ticket(
        self,
        payload: TicketCreateRequest,
    ) -> UUID:
        event = await self.event_repo.get_by_id(str(payload.event_id))
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        response = await self.client.register_ticket(
            str(payload.event_id),
            {
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "email": payload.email,
                "seat": payload.seat,
            },
        )

        ticket_id = UUID(response["ticket_id"])
        ticket = Ticket(
            ticket_id=ticket_id,
            event_id=payload.event_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            seat=payload.seat,
            created_at=datetime.now(timezone.utc),
        )

        await self.ticket_repo.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)

        return ticket.ticket_id

    async def cancel_ticket(self, ticket_id: UUID) -> bool:
        ticket = await self.ticket_repo.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )

        event = await self.event_repo.get_by_id(str(ticket.event_id))

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found",
            )

        now = datetime.now(timezone.utc)

        event_time = event.event_time

        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)

        if event_time < now:
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel registration for past event",
            )

        try:
            await self.client.unregister_ticket(
                str(ticket.event_id),
                str(ticket.ticket_id),
            )
        except Exception as e:
            print("UNREGISTER ERROR:", str(e))

        await self.ticket_repo.delete(ticket)

        await self.db.commit()

        return True
