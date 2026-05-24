from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event
from src.models.place import Place
from src.models.sync_metadata import SyncMetadata
from src.services.events_provider import EventsProviderClient


class SyncService:
    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db
        self.client = EventsProviderClient()

    async def sync_events(self) -> None:
        sync_meta = await self._get_sync_metadata()

        changed_at = (
            sync_meta.last_changed_at.date().isoformat()
            if sync_meta.last_changed_at
            else "2000-01-01"
        )

        next_url = None
        max_changed_at = sync_meta.last_changed_at

        while True:
            response = await self.client.get_events(
                changed_at=changed_at,
                cursor_url=next_url,
            )

            events = response["results"]

            for event_data in events:
                await self._upsert_place(event_data["place"])
                await self._upsert_event(event_data)

                event_changed_at = datetime.fromisoformat(
                    event_data["changed_at"]
                )

                if (
                    max_changed_at is None
                    or event_changed_at > max_changed_at
                ):
                    max_changed_at = event_changed_at

            next_url = response["next"]

            if not next_url:
                break

        sync_meta.last_sync_time = datetime.utcnow()
        sync_meta.last_changed_at = max_changed_at
        sync_meta.sync_status = "success"

        await self.db.commit()

    async def _get_sync_metadata(
        self,
    ) -> SyncMetadata:
        result = await self.db.execute(
            select(SyncMetadata)
        )

        sync_meta = result.scalar_one_or_none()

        if not sync_meta:
            sync_meta = SyncMetadata()

            self.db.add(sync_meta)

            await self.db.commit()
            await self.db.refresh(sync_meta)

        return sync_meta

    async def _upsert_place(
        self,
        place_data: dict,
    ) -> None:
        result = await self.db.execute(
            select(Place).where(
                Place.id == place_data["id"]
            )
        )
        print(place_data)
        place = result.scalar_one_or_none()

        if place:
            place.name = place_data["name"]
            place.city = place_data["city"]
            place.address = place_data["address"]
            place.seats_pattern = place_data["seats_pattern"]
            place.changed_at = datetime.fromisoformat(
                place_data["changed_at"]
            )

        else:
            place = Place(
                id=place_data["id"],
                name=place_data["name"],
                city=place_data["city"],
                address=place_data["address"],
                seats_pattern=place_data["seats_pattern"],
                changed_at=datetime.fromisoformat(
                    place_data["changed_at"]
                ),
                created_at=datetime.fromisoformat(
                    place_data["created_at"]
                ),
            )

            self.db.add(place)

    async def _upsert_event(
        self,
        event_data: dict,
    ) -> None:
        result = await self.db.execute(
            select(Event).where(
                Event.id == event_data["id"]
            )
        )

        event = result.scalar_one_or_none()

        if event:
            event.name = event_data["name"]
            event.event_time = datetime.fromisoformat(
                event_data["event_time"]
            )
            event.registration_deadline = datetime.fromisoformat(
                event_data["registration_deadline"]
            )
            event.status = event_data["status"]
            event.number_of_visitors = event_data[
                "number_of_visitors"
            ]
            event.place_id = event_data["place"]["id"]
            event.changed_at = datetime.fromisoformat(
                event_data["changed_at"]
            )
            event.status_changed_at = datetime.fromisoformat(
                event_data["changed_at"]
            )

        else:
            event = Event(
                id=event_data["id"],
                name=event_data["name"],
                event_time=datetime.fromisoformat(
                    event_data["event_time"]
                ),
                registration_deadline=datetime.fromisoformat(
                    event_data["registration_deadline"]
                ),
                status=event_data["status"],
                number_of_visitors=event_data[
                    "number_of_visitors"
                ],
                place_id=event_data["place"]["id"],
                changed_at=datetime.fromisoformat(
                    event_data["changed_at"]
                ),
                created_at=datetime.fromisoformat(
                    event_data["created_at"]
                ),
                status_changed_at=datetime.fromisoformat(
                    event_data["changed_at"]
                ),
            )

            self.db.add(event)