import aiohttp

class OpenWeatherMapClient:
    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self._api_key = api_key
        self._session = session

    async def fetch_forecast(self, lat: float, lon: float):
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
            "units": "imperial",
            "exclude": "current,minutely,alerts",
        }
        async with self._session.get(self.BASE_URL, params=params, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.json()
