# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and development environment setup
- Comprehensive build system with quality tools
- VS Code configuration with recommended extensions
- CI/CD pipelines for testing and releases
- Documentation for development setup, building, and testing

## [1.0.0] - TBD

### Added
- Initial release
- OpenWeatherMap API integration for precipitation forecasts
- Rain and snow accumulation tracking
- Hourly, daily, and 24-hour forecast periods
- Multiple location support
- Configurable polling intervals (15min to 24h)
- Temperature-adjusted snow ratio calculations
- Config flow for easy setup via UI
- Options flow for modifying configuration
- Health monitoring entity
- Comprehensive error handling and retry logic
- Rate limiting protection
- HACS compliance
- Full test coverage (unit, integration, advanced scenarios)

### Features
- **Sensors**
  - Hourly rain accumulation
  - Hourly snow accumulation
  - Daily rain accumulation
  - Daily snow accumulation
  - Next 24h rain accumulation
  - Next 24h snow accumulation
  - Integration health status

- **Configuration**
  - Enable/disable rain tracking
  - Enable/disable snow tracking
  - Configurable polling intervals
  - Multiple locations
  - Temperature-adjusted snow ratios
  - Unit preferences (inches/cm)

- **Quality**
  - 95%+ test coverage
  - Type-safe code
  - Comprehensive documentation
  - Fault-tolerant design

[Unreleased]: https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jeffjensen/ha-owm-precipitation-forecast-integration/releases/tag/v1.0.0
