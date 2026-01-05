"""DataUpdateCoordinator for OWM Precipitation."""
from datetime import timedelta
import logging
import math

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OWMClient
from .calculator import SnowCalculator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class OWMPrecipitationCoordinator(DataUpdateCoordinator):
    """Class to manage fetching OWM data."""

    def __init__(self, hass: HomeAssistant, client: OWMClient, snow_calculator: SnowCalculator, config_entry):
        """Initialize."""
        self.client = client
        self.snow_calc = snow_calculator
        self.config_entry = config_entry
        self.lat = config_entry.data["latitude"]
        self.lon = config_entry.data["longitude"]

        # Set interval
        interval_hours = config_entry.options.get("polling_interval", config_entry.data.get("polling_interval", 1))
        update_interval = timedelta(hours=interval_hours)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            data = await self.client.get_forecast(self.lat, self.lon)
            return self._process_data(data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    def _process_data(self, data):
        """Process raw API data into precipitation totals."""
        processed = {
            "rain": {"hourly": [], "daily": [], "next24h": 0.0},
            "snow": {"hourly": [], "daily": [], "next24h": 0.0},
            "api_timestamp": data.get("current", {}).get("dt")
        }

        hourly_data = data.get("hourly", [])

        # OWM OneCall 3.0: rain/snow are objects like {"1h": 0.5} (mm)
        # Note: If units=imperial, OWM docs say precipitation is in mm.
        mm_to_in = 0.0393701

        # Process Hourly (Next 48h usually provided)
        for hour in hourly_data:
            temp_f = hour.get("temp", 32)

            # Rain (Liquid)
            rain_mm = hour.get("rain", {}).get("1h", 0)
            rain_in = rain_mm * mm_to_in

            # Snow (Liquid Equivalent)
            snow_mm = hour.get("snow", {}).get("1h", 0)
            snow_liquid_in = snow_mm * mm_to_in

            # Calculate Snow Accumulation
            snow_accum_in = self.snow_calc.calculate_snow(snow_liquid_in, temp_f)

            ts = hour.get("dt")

            processed["rain"]["hourly"].append({"dt": ts, "val": rain_in})
            processed["snow"]["hourly"].append({"dt": ts, "val": snow_accum_in})

        # Calculate Next 24h Totals
        processed["rain"]["next24h"] = sum(x["val"] for x in processed["rain"]["hourly"][:24])
        processed["snow"]["next24h"] = sum(x["val"] for x in processed["snow"]["hourly"][:24])

        # Process Daily
        daily_data = data.get("daily", [])
        for day in daily_data:
            ts = day.get("dt")
            # Daily 'rain'/'snow' in OWM is total volume mm
            rain_mm = day.get("rain", 0)
            rain_in = rain_mm * mm_to_in

            snow_mm = day.get("snow", 0)
            snow_liquid_in = snow_mm * mm_to_in

            # For daily snow, we use day avg temp or max?
            # Using 'morn', 'day', 'eve', 'night' temps is better, but complexity increases.
            # We will use 'day' temp as approximation or loop hourly if available.
            # Since daily object is summary, we apply ratio to summary using daily avg temp (morn+day+eve+night)/4?
            # Let's use daily.temp.day
            temp_f = day.get("temp", {}).get("day", 32)
            snow_accum_in = self.snow_calc.calculate_snow(snow_liquid_in, temp_f)

            processed["rain"]["daily"].append({"dt": ts, "val": rain_in})
            processed["snow"]["daily"].append({"dt": ts, "val": snow_accum_in})

        return processed