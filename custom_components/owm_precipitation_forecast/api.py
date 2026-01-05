"""OpenWeatherMap API Client."""
import aiohttp
import logging
from typing import Any, Dict

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

class OWMClient:
    """Client to interact with OWM OneCall API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self._api_key = api_key
        self._session = session

    async def get_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch weather data."""
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
            "exclude": "minutely,alerts",
            "units": "imperial" # Requesting Imperial returns Temp in F, Precip in mm (oddly enough, OWM standard)
        }

        # Note: OWM API 3.0 Standard:
        # Units 'imperial': Temp: F, Wind: mph, Precip: mm (yes, mm is standard for precip in OneCall 3.0 usually,
        # but let's verify standard behavior or handle conversion.
        # Actually, in 'imperial' mode, docs say 'rain' volume is mm. We must normalize.

        try:
            async with self._session.get(BASE_URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching data from OWM: %s", err)
            raise