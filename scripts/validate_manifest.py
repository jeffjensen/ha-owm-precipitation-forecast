#!/usr/bin/env python3
"""Validate the manifest.json file for Home Assistant compliance."""

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "domain",
    "name",
    "version",
    "documentation",
    "issue_tracker",
    "requirements",
    "codeowners",
    "config_flow",
    "iot_class",
]

OPTIONAL_FIELDS = [
    "after_dependencies",
    "dependencies",
    "integration_type",
    "loggers",
]

VALID_IOT_CLASSES = [
    "cloud_polling",
    "cloud_push",
    "local_polling",
    "local_push",
    "calculated",
]


def load_manifest() -> dict[str, Any]:
    """Load the manifest.json file."""
    manifest_path = Path("custom_components/owm_precipitation_forecast/manifest.json")
    
    if not manifest_path.exists():
        print(f"ERROR: Manifest file not found at {manifest_path}")
        sys.exit(1)
    
    try:
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in manifest: {e}")
        sys.exit(1)


def validate_required_fields(manifest: dict[str, Any]) -> bool:
    """Validate that all required fields are present."""
    print("Checking required fields...")
    
    missing_fields = []
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"ERROR: Missing required fields: {', '.join(missing_fields)}")
        return False
    
    print("✓ All required fields present")
    return True


def validate_domain(manifest: dict[str, Any]) -> bool:
    """Validate the domain field."""
    print("Checking domain...")
    
    domain = manifest.get("domain")
    if not domain:
        print("ERROR: Domain is empty")
        return False
    
    if domain != "owm_precipitation_forecast":
        print(f"ERROR: Domain should be 'owm_precipitation_forecast', got '{domain}'")
        return False
    
    print(f"✓ Domain is valid: {domain}")
    return True


def validate_version(manifest: dict[str, Any]) -> bool:
    """Validate the version field."""
    print("Checking version...")
    
    version = manifest.get("version")
    if not version:
        print("ERROR: Version is empty")
        return False
    
    # Check semantic versioning format
    parts = version.split(".")
    if len(parts) != 3:
        print(f"ERROR: Version should follow semantic versioning (x.y.z), got '{version}'")
        return False
    
    try:
        for part in parts:
            int(part)
    except ValueError:
        print(f"ERROR: Version parts should be integers, got '{version}'")
        return False
    
    print(f"✓ Version is valid: {version}")
    return True


def validate_urls(manifest: dict[str, Any]) -> bool:
    """Validate URL fields."""
    print("Checking URLs...")
    
    documentation = manifest.get("documentation")
    issue_tracker = manifest.get("issue_tracker")
    
    if not documentation or not documentation.startswith("https://"):
        print(f"ERROR: Documentation URL is invalid: {documentation}")
        return False
    
    if not issue_tracker or not issue_tracker.startswith("https://"):
        print(f"ERROR: Issue tracker URL is invalid: {issue_tracker}")
        return False
    
    print(f"✓ Documentation URL: {documentation}")
    print(f"✓ Issue tracker URL: {issue_tracker}")
    return True


def validate_requirements(manifest: dict[str, Any]) -> bool:
    """Validate requirements field."""
    print("Checking requirements...")
    
    requirements = manifest.get("requirements", [])
    if not isinstance(requirements, list):
        print("ERROR: Requirements should be a list")
        return False
    
    print(f"✓ Requirements: {requirements}")
    return True


def validate_codeowners(manifest: dict[str, Any]) -> bool:
    """Validate codeowners field."""
    print("Checking codeowners...")
    
    codeowners = manifest.get("codeowners", [])
    if not isinstance(codeowners, list):
        print("ERROR: Codeowners should be a list")
        return False
    
    if not codeowners:
        print("WARNING: No codeowners specified")
        return True
    
    for owner in codeowners:
        if not owner.startswith("@"):
            print(f"ERROR: Codeowner should start with '@', got '{owner}'")
            return False
    
    print(f"✓ Codeowners: {codeowners}")
    return True


def validate_config_flow(manifest: dict[str, Any]) -> bool:
    """Validate config_flow field."""
    print("Checking config_flow...")
    
    config_flow = manifest.get("config_flow")
    if not isinstance(config_flow, bool):
        print("ERROR: config_flow should be a boolean")
        return False
    
    if not config_flow:
        print("WARNING: config_flow is disabled")
    
    print(f"✓ Config flow: {config_flow}")
    return True


def validate_iot_class(manifest: dict[str, Any]) -> bool:
    """Validate iot_class field."""
    print("Checking iot_class...")
    
    iot_class = manifest.get("iot_class")
    if iot_class not in VALID_IOT_CLASSES:
        print(f"ERROR: Invalid iot_class '{iot_class}'. Must be one of: {VALID_IOT_CLASSES}")
        return False
    
    print(f"✓ IoT class: {iot_class}")
    return True


def main() -> None:
    """Main validation function."""
    print("=" * 80)
    print("VALIDATING MANIFEST.JSON")
    print("=" * 80)
    print()
    
    manifest = load_manifest()
    
    validations = [
        validate_required_fields(manifest),
        validate_domain(manifest),
        validate_version(manifest),
        validate_urls(manifest),
        validate_requirements(manifest),
        validate_codeowners(manifest),
        validate_config_flow(manifest),
        validate_iot_class(manifest),
    ]
    
    print()
    print("=" * 80)
    
    if all(validations):
        print("✓ MANIFEST VALIDATION PASSED")
        print("=" * 80)
        sys.exit(0)
    else:
        print("✗ MANIFEST VALIDATION FAILED")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
