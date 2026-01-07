.PHONY: help install install-dev format lint type-check test test-cov clean build validate

help:
	@echo "OpenWeatherMap Precipitation Forecast Integration - Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install           Install dependencies"
	@echo "  make install-dev       Install dev dependencies"
	@echo ""
	@echo "Quality:"
	@echo "  make format            Format code with Black"
	@echo "  make lint              Run Pylint and Flake8"
	@echo "  make type-check        Run MyPy type checking"
	@echo "  make test              Run pytest"
	@echo "  make test-cov          Run pytest with coverage"
	@echo ""
	@echo "Integration:"
	@echo "  make validate          Validate manifest.json"
	@echo "  make all-checks        Run all quality checks (format, lint, type-check, test)"
	@echo ""
	@echo "Build:"
	@echo "  make build             Build package"
	@echo "  make clean             Clean build artifacts"

install:
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install -e .

install-dev:
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install -e ".[dev]"

format:
	black custom_components tests

lint:
	pylint custom_components/owm_precipitation_forecast
	flake8 custom_components/owm_precipitation_forecast tests

type-check:
	mypy custom_components/owm_precipitation_forecast

test:
	pytest

test-cov:
	pytest --cov=custom_components/owm_precipitation_forecast --cov-report=html:coverage_html_report --cov-report=term-missing

validate:
	@command -v hassfest >/dev/null 2>&1 || (echo "hassfest not installed. Install with: pip install homeassistant"; exit 1)
	hassfest -r .

all-checks: format lint type-check test
	@echo "All quality checks passed!"

build: clean
	python -m build

clean:
	rm -rf build dist *.egg-info __pycache__ .pytest_cache .coverage coverage_html_report
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.DEFAULT_GOAL := help

