from __future__ import annotations


class OWMPrecipitationError(Exception):
    """Base error for this integration."""


class OWMPrecipitationAPIError(OWMPrecipitationError):
    """Raised when OWM API returns an error or bad data."""


class OWMPrecipitationConfigError(OWMPrecipitationError):
    """Raised for invalid configuration."""


class OWMPrecipitationCalculationError(OWMPrecipitationError):
    """Raised when calculations fail unexpectedly."""
