
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .owm_client import OpenWeatherMapClient
from .parser import parse_forecast
from .snow_ratio import SnowRatioCalculator

_LOGGER = logging.getLogger(__name__)

class OWMPrecipitationCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_key, lat, lon, interval, snow_ratios):
        session = hass.helpers.aiohttp_client.async_get_clientsession(hass)
        self._client = OpenWeatherMapClient(api_key, session)
        self._lat = lat
        self._lon = lon
        self._snow_calc = SnowRatioCalculator(snow_ratios)
        super().__init__(
            hass,
            _LOGGER,
            name="OWM Precipitation Forecast",
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self):
        try:
            raw = await self._client.fetch_forecast(self._lat, self._lon)
            return parse_forecast(raw, self._snow_calc)
        except Exception as err:
            raise UpdateFailed(err) from err
