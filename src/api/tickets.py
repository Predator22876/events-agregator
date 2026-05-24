from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.ticket import (
    TicketCreateRequest,
    TicketCreateResponse,
    TicketDeleteResponse,
)
from src.services.ticket_service import TicketService

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("", response_model=TicketCreateResponse, status_code=201)
async def create_ticket(
    payload: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = TicketService(db)
    ticket_id = await service.create_ticket(payload)
    return TicketCreateResponse(ticket_id=ticket_id)


@router.delete("/{ticket_id}", response_model=TicketDeleteResponse)
async def delete_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = TicketService(db)
    success = await service.cancel_ticket(ticket_id)
    return TicketDeleteResponse(success=success)
