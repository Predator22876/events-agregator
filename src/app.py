import asyncio
from contextlib import suppress
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
import uvicorn

from src.api.events import router as events_router
from src.api.sync import router as sync_router
from src.api.tickets import router as tickets_router
from src.database import async_session_maker, get_db
from src.services.sync_service import SyncService

app = FastAPI()
app.include_router(events_router)
app.include_router(tickets_router)
app.include_router(sync_router)

sync_task: asyncio.Task | None = None


async def _background_sync_loop() -> None:
    while True:
        try:
            async with async_session_maker() as session:
                await SyncService(session).sync_events()
        except Exception:
            pass

        await asyncio.sleep(timedelta(days=1).total_seconds())


@app.on_event("startup")
async def on_startup() -> None:
    global sync_task
    if sync_task is None:
        sync_task = asyncio.create_task(_background_sync_loop())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global sync_task
    if sync_task is not None:
        sync_task.cancel()
        with suppress(asyncio.CancelledError):
            await sync_task


@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(1))
        result.scalar_one()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="backend unavailable") from exc

    return {"status": "ok"}

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", reload=True)