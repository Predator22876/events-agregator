from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TicketCreateRequest(BaseModel):
    event_id: UUID
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    seat: str = Field(min_length=1, max_length=20)


class TicketCreateResponse(BaseModel):
    ticket_id: UUID


class TicketDeleteResponse(BaseModel):
    success: bool
