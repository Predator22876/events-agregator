from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.sync import SyncTriggerResponse
from src.services.sync_service import SyncService

router = APIRouter(
    prefix="/api/sync",
    tags=["Sync"],
)


@router.post(
    "/trigger",
    response_model=SyncTriggerResponse,
)
async def trigger_sync(
    db: AsyncSession = Depends(get_db),
):
    sync_service = SyncService(db)

    await sync_service.sync_events()

    return SyncTriggerResponse(
        success=True,
        message="Sync completed successfully",
    )
