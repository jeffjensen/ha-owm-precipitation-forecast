"""Exceptions for OWM Precipitation Forecast integration."""


class OWMApiError(Exception):
    """Base exception for OWM API errors."""


class OWMApiKeyError(OWMApiError):
    """Exception for invalid API key."""


class OWMApiRateLimitError(OWMApiError):
    """Exception for rate limit exceeded."""


class OWMApiTimeoutError(OWMApiError):
    """Exception for request timeout."""


class OWMApiConnectionError(OWMApiError):
    """Exception for connection errors."""


class OWMApiResponseError(OWMApiError):
    """Exception for invalid API response."""


class OWMDataError(Exception):
    """Exception for data processing errors."""


class OWMConfigError(Exception):
    """Exception for configuration errors."""
