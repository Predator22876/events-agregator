from datetime import datetime

from pydantic import BaseModel


class SyncTriggerResponse(BaseModel):
    success: bool
    message: str


class SyncMetadataResponse(BaseModel):
    last_sync_time: datetime | None
    last_changed_at: datetime | None
    sync_status: str
