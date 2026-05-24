from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceBase(BaseModel):
    id: UUID
    name: str
    city: str
    address: str

    model_config = ConfigDict(from_attributes=True)


class PlaceDetailResponse(PlaceBase):
    seats_pattern: str


class EventBase(BaseModel):
    id: UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int

    model_config = ConfigDict(from_attributes=True)


class EventResponse(EventBase):
    place: PlaceBase


class EventDetailResponse(EventBase):
    place: PlaceDetailResponse


class PaginatedEventsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventResponse]