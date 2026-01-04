# Makes package installable with pip
# Used for building distributions

"""Setup configuration."""
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ha-owm-precipitation-forecast",
    version="1.0.0",
    description="Home Assistant integration for OpenWeatherMap precipitation forecast",
    long_description=long_description,
    long_description_content_type="text/plain",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/ha-owm-precipitation-forecast",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.11",
    install_requires=[
        "aiohttp>=3.9.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: AsyncIO",
    ],
    keywords="home-assistant homeassistant hacs openweathermap weather precipitation",
)
