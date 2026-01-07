# OpenWeatherMap Precipitation Forecast Integration for Home Assistant

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=home%20assistant&logoColor=white&style=for-the-badge)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/jeffjensen/ha-owm-precipitation-forecast-integration?style=for-the-badge)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

A Home Assistant custom integration that provides hourly, daily, and next-24-hour precipitation forecasts (rain and snow) from OpenWeatherMap.

## Features

- 🌧️ **Rain Forecasts** - Hourly, daily, and 24-hour totals
- ❄️ **Snow Forecasts** - Temperature-adjusted precipitation-to-snow conversion
- 📍 **Multiple Locations** - Separate config entry per location
- ⚙️ **Highly Configurable** - Rain/snow toggles, polling intervals, custom snow ratios
- 📊 **Rich Attributes** - Hourly breakdowns and accumulated values for charts/cards
- 🔒 **Secure** - Uses OpenWeatherMap API key for data fetching
- 🏡 **Native HA Integration** - Full config flow UI, no YAML required

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click **Integrations**
3. Click the **+** button
4. Search for "OpenWeatherMap Precipitation Forecast"
5. Click **Install**
6. Restart Home Assistant

### Manual Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration.git
   ```

2. Copy the integration folder to your Home Assistant configuration:

   ```bash
   cp -r ha-owm-precipitation-forecast-integration/custom_components/owm_precipitation_forecast \
     ~/.homeassistant/custom_components/
   ```

3. Restart Home Assistant

## Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Create Automation** → **Integrations** tab
3. Search for and select **OpenWeatherMap Precipitation Forecast**
4. Follow the configuration flow to add your location:
   - Enter your OpenWeatherMap API key (get one free at [openweathermap.org](https://openweathermap.org/api))
   - Set location by coordinates (latitude/longitude)
   - Choose precipitation types (Rain, Snow, or both)
   - Select polling interval (15 min to 24 hours, default: 1 hour)

## Configuration

All configuration is done through Home Assistant UI. After initial setup, you can modify options by:

1. Going to **Settings** → **Devices & Services**
2. Finding your integration
3. Clicking the **Options** button to adjust:
   - Rain/Snow enabled toggles
   - Polling interval
   - Temperature-adjusted snow ratio configuration

### Temperature-Adjusted Snow Ratios

The integration converts liquid precipitation to snow using temperature-dependent ratios:

- **Cold (< 25°F)**: 15:1 ratio (15 inches of snow per 1 inch of rain)
- **Transitional (25-32°F)**: 10:1 ratio
- **Warm (> 32°F)**: 5:1 ratio (wetter snow)

These ratios are customizable in the options flow.

## Entities

For each location, the integration creates entities:

- `sensor.owm_precipitation_forecast_{location}_rain_hourly` - Hourly rain total (inches)
- `sensor.owm_precipitation_forecast_{location}_rain_daily` - Daily rain total (inches)
- `sensor.owm_precipitation_forecast_{location}_rain_next24h` - Next 24h rain total (inches)
- `sensor.owm_precipitation_forecast_{location}_snow_hourly` - Hourly snow total (inches)
- `sensor.owm_precipitation_forecast_{location}_snow_daily` - Daily snow total (inches)
- `sensor.owm_precipitation_forecast_{location}_snow_next24h` - Next 24h snow total (inches)
- `binary_sensor.owm_precipitation_forecast_{location}_health` - Integration health status

## Entity Attributes

Each precipitation sensor includes attributes for advanced charting and cards:

- `forecast` - Array of hourly forecasts with timestamps and values
- `timestamp` - Last update timestamp
- `unit_of_measurement` - "in" (inches)

## Troubleshooting

### Integration Not Showing Up

- Ensure you've installed to `custom_components/owm_precipitation_forecast/`
- Check Home Assistant logs for errors
- Restart Home Assistant after installation

### API Key Issues

- Verify your OpenWeatherMap API key is correct
- Check that your free tier includes the One Call API
- Wait a few minutes for the API to activate after sign-up

### Data Not Updating

- Verify internet connection
- Check integration health entity status
- Increase logging in configuration.yaml:
  ```yaml
  logger:
    logs:
      custom_components.owm_precipitation_forecast: debug
  ```

## Development

See [DEVELOPMENT.adoc](docs/DEVELOPMENT.adoc) for setup instructions.

### Testing

```bash
make test              # Run all tests
make test-cov          # Run tests with coverage report
make all-checks        # Format, lint, type-check, and test
```

See [TESTING.adoc](docs/TESTING.adoc) for detailed information.

## License

This integration is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Attribution

- OpenWeatherMap for weather data and API
- Home Assistant community for integration framework and best practices

## Support

- [GitHub Issues](https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/issues)
- [Home Assistant Community Forums](https://community.home-assistant.io/)

## Changelog

See [releases](https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/releases) for version history.
