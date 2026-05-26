from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.event import (
    EventDetailResponse,
    PaginatedEventsResponse,
)
from src.schemas.seat import SeatsResponse
from src.services.event_service import EventService
from src.services.events_provider import EventsProviderClient

router = APIRouter(prefix="/api/events", tags=["Events"])


def _build_page_url(request: Request, page: int, page_size: int) -> str:
    return str(
        request.url.replace_query_params(
            page=page,
            page_size=page_size,
        )
    )


@router.get("", response_model=PaginatedEventsResponse)
async def list_events(
    request: Request,
    date_from: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    total, events = await service.list_events(date_from, page, page_size)

    next_url = None
    prev_url = None

    if page * page_size < total:
        next_url = _build_page_url(request, page + 1, page_size)

    if page > 1:
        prev_url = _build_page_url(request, page - 1, page_size)

    return PaginatedEventsResponse(
        count=total,
        next=next_url,
        previous=prev_url,
        results=events,
    )


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/{event_id}/seats", response_model=SeatsResponse)
async def get_event_seats(
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    print("EVENT:", event)
    client = EventsProviderClient()
    result = await client.get_available_seats(event_id)
    print("SEATS RESPONSE:", result)
    return SeatsResponse(
        event_id=event_id,
        available_seats=result.get("available_seats", []),
    )
