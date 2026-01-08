from __future__ import annotations

import aiohttp
from typing import Any

class OWMClient:
    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        self._api_key = api_key
        self._session = session

    async def fetch(self, lat: float, lon: float) -> dict[str, Any]:
        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
            "units": "metric",
        }

        async with self._session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()
