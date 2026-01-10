# OWM Precipitation Forecast Integration for Home Assistant

[![CI](https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/actions/workflows/ci.yml/badge.svg)](https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jeffjensen/ha-owm-precipitation-forecast-integration/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffjensen/ha-owm-precipitation-forecast-integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://hacs.xyz)

A comprehensive Home Assistant integration for detailed precipitation forecasts using OpenWeatherMap data.

## Features

- ⛈️ **Rain and Snow Forecasts** - Separate tracking for rain and snow precipitation
- 📊 **Multiple Time Periods** - Hourly, daily, and 24-hour totals
- 📍 **Multiple Locations** - Configure unlimited locations
- ⚙️ **Highly Configurable** - Customize polling intervals, temperature-adjusted snow ratios, and more
- 🎯 **Precise Measurements** - Accumulation in inches with automatic cm conversion
- 🔄 **Reliable Updates** - Built-in retry logic and error handling
- 📈 **Rich Attributes** - Detailed sensor attributes for dashboards and cards

## Documentation

**📘 [Read the Full Documentation](README.adoc)**

The complete documentation includes:

- Detailed installation instructions
- Configuration guide
- Feature explanations
- API reference
- Troubleshooting
- And much more...

## Quick Links

- **[Installation Guide](README.adoc#installation)**
- **[Configuration](README.adoc#configuration)**
- **[Development Setup](docs/DEVELOPMENT_SETUP.adoc)**
- **[Contributing](CONTRIBUTING.adoc)**
- **[Changelog](CHANGELOG.md)**

## Quick Start

### Prerequisites

- Home Assistant 2024.1.0 or newer
- OpenWeatherMap API key (One Call API 3.0)
- HACS installed

### Installation via HACS

1. Open HACS in Home Assistant
2. Click "Integrations"
3. Click the three dots (⋮) in the top right
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration`
6. Select category: "Integration"
7. Click "Add"
8. Find "OWM Precipitation Forecast" in HACS
9. Click "Install"
10. Restart Home Assistant

### Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"OWM Precipitation Forecast"**
4. Follow the configuration wizard

## Support

- 🐛 [Report Issues](https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/issues)
- 💬 [Discussions](https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

⭐ If you find this integration useful, please star the repository!
