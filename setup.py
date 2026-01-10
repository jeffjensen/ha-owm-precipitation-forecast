"""Setup for OWM Precipitation Forecast integration."""
from setuptools import find_packages, setup

setup(
    name="owm_precipitation_forecast",
    version="0.1.0",
    description="Home Assistant integration for OpenWeatherMap precipitation forecasts",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(include=["custom_components"]),
    zip_safe=False,
    install_requires=[],
    tests_require=[
        "pytest==8.2.0",
        "pytest-asyncio==0.23.6",
        "pytest-cov==5.0.0",
        "aioresponses==0.7.7",
        "homeassistant==2024.1.0",
    ],
)
