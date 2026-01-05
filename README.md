# OpenWeatherMap Precipitation Forecast Integration

[![GitHub Release](https://img.shields.io/github/release/your-username/ha-owm-precipitation-forecast.svg?style=flat-square)](https://github.com/your-username/ha-owm-precipitation-forecast/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-red.svg)](https://github.com/hacs/integration)

A Home Assistant integration that provides detailed precipitation forecasts from OpenWeatherMap, with separate tracking for rain and snow, including temperature-adjusted snow calculations.

## Features

- **Dual Precipitation Tracking**: Independent sensors for rain and snow
- **Multiple Time Horizons**: Hourly, daily, and 24-hour accumulations
- **Smart Snow Calculations**: Temperature-adjusted snow-to-liquid ratios
- **Configurable Polling**: Update intervals from 15 minutes to 24 hours
- **Health Monitoring**: Dedicated sensor for integration health status
- **OpenWeatherMap API 3.0**: Uses One Call API 3.0 for comprehensive weather data
- **Full UI Configuration**: Complete setup via Home Assistant UI
- **Entity Attributes**: Rich attribute data for cards and automations
- **Production Ready**: Full test coverage, CI/CD, code quality tools

## Installation

### Via HACS

1. Install [HACS](https://hacs.xyz/)
2. Add custom repository: https://github.com/your-username/ha-owm-precipitation-forecast
3. Search for "OpenWeatherMap Precipitation Forecast" and click install
4. Restart Home Assistant
5. Configure via Settings → Devices & Services → Create Integration

### Manual Installation

1. Copy `custom_components/ha_owm_precipitation_forecast` to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Configure via Settings → Devices & Services → Create Integration

## Configuration

### Initial Setup

1. Go to Settings → Devices & Services
2. Click "Create Integration"
3. Search for "OpenWeatherMap Precipitation Forecast"
4. Provide:
   - **API Key**: Get free key from [OpenWeatherMap](https://openweathermap.org/api)
   - **Latitude/Longitude**: Your location (defaults to Home Assistant location)
   - **Location Name**: Display name (e.g., "Home")
   - **Update Interval**: 15, 30, 60, 240, 480, 720, or 1440 minutes (default: 60)
   - **Enable Rain/Snow**: Toggle precipitation tracking
   - **Snow Ratio**: 10:1 by default (10 inches snow per 1 inch rain equivalent)
   - **Temperature-Adjusted Ratios**: Enable smart ratio selection

### Options (Reconfigurable)

Once installed, adjust settings via:
Settings → Devices & Services → Select Integration → Options

## Entities

All entities are prefixed with `sensor.owm_precipitation_forecast_{location}_`:

| Entity | Description | Unit |
|--------|-------------|------|
| `hourly_rain` | Rain accumulation (last 24 hours, per hour) | inches |
| `hourly_snow` | Snow accumulation (last 24 hours, per hour) | inches |
| `daily_rain` | Rain for today | inches |
| `daily_snow` | Snow for today | inches |
| `next24h_rain` | Expected rain next 24 hours | inches |
| `next24h_snow` | Expected snow next 24 hours | inches |
| `health` | Integration health status | ok/error/unavailable |

Each precipitation sensor includes hourly/daily breakdown in attributes for use in cards and automations.

## Snow Ratio Calculation

### Temperature-Adjusted Ratios

When enabled, automatically selects snow ratio based on temperature:

| Temperature (°F) | Snow Ratio |
|-----------------|-----------|
| < 0°F | 20:1 (very fluffy) |
| 0-10°F | 18:1 (optimal conditions) |
| 10-20°F | 14:1 |
| 20-28°F | 12:1 |
| 28-32°F | 8:1 (wet snow) |
| > 32°F | 0:1 (rain only) |

### Fixed Ratio

Use default or custom fixed ratio for consistency:
- Default: 10:1 (standard NOAA average)
- Range: 1:1 to 50:1

## Usage Examples

### Automation Example

```yaml
- alias: "Heavy Snow Warning"
  trigger:
    platform: numeric_state
    entity_id: sensor.owm_precipitation_forecast_home_next24h_snow
    above: 8
  action:
    service: notify.mobile_app_iphone
    data:
      message: "Heavy snow expected: {{ states('sensor.owm_precipitation_forecast_home_next24h_snow') }} inches"
```

### Card Example

```yaml
type: entities
entities:
  - entity_id: sensor.owm_precipitation_forecast_home_next24h_rain
    name: Next 24h Rain
  - entity_id: sensor.owm_precipitation_forecast_home_next24h_snow
    name: Next 24h Snow
  - entity_id: sensor.owm_precipitation_forecast_home_health
    name: Integration Health
```

## Requirements

- Home Assistant 2024.1.0 or later
- OpenWeatherMap API key (free tier available)
- Network connectivity

## Support

- Documentation: See [docs/](docs/) folder
- Issues: [GitHub Issues](https://github.com/your-username/ha-owm-precipitation-forecast/issues)
- Discussions: [GitHub Discussions](https://github.com/your-username/ha-owm-precipitation-forecast/discussions)

## License

This integration is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for weather data
- [Home Assistant](https://home-assistant.io/) for the automation platform
- [HACS](https://hacs.xyz/) for integration distribution

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Follow code style: `pylint`, `black`, `isort`
6. Submit a pull request

See [DEVELOPMENT.md](docs/SETUP.adoc) for development setup instructions.
