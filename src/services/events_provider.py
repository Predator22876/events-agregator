from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx

from src.config import settings


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme == "http":
        parsed = parsed._replace(scheme="https")
    return urlunparse(parsed)


class EventsProviderClient:
    def __init__(self) -> None:
        self.base_url = normalize_url(settings.EVENTS_PROVIDER_URL).rstrip("/")
        self.headers = {
            "x-api-key": settings.EVENTS_PROVIDER_API_KEY,
        }

    async def get_events(
        self,
        changed_at: str,
        cursor_url: str | None = None,
    ) -> dict[str, Any]:
        url = cursor_url or f"{self.base_url}/api/events/"

        params = None
        if not cursor_url:
            params = {"changed_at": changed_at}

        url = normalize_url(url)

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers=self.headers,
                params=params,
            )

            response.raise_for_status()

            return response.json()

    async def get_available_seats(
        self,
        event_id: str,
    ) -> dict[str, Any]:
        url = normalize_url(f"{self.base_url}/api/events/{event_id}/seats/")

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers=self.headers,
            )

            response.raise_for_status()

            return response.json()

    async def register_ticket(
        self,
        event_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        url = normalize_url(f"{self.base_url}/api/events/{event_id}/register/")

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
            )

            response.raise_for_status()

            return response.json()

    async def unregister_ticket(
        self,
        event_id: str,
        ticket_id: str,
    ) -> dict[str, Any]:
        url = normalize_url(f"{self.base_url}/api/events/{event_id}/unregister/")

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.delete(
                url,
                headers=self.headers,
                json={"ticket_id": ticket_id},
            )

            response.raise_for_status()

            return response.json()