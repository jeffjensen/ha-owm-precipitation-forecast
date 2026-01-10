#!/usr/bin/env python3
"""Local build script for the OWM Precipitation Forecast integration."""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_step(message: str) -> None:
    """Print a step message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def run_command(
    command: list[str], description: str, check: bool = True
) -> subprocess.CompletedProcess[Any]:
    """Run a command and handle errors."""
    print(f"{Colors.OKBLUE}Running: {' '.join(command)}{Colors.ENDC}")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print(f"{Colors.OKGREEN}✓ {description} completed successfully{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ {description} failed{Colors.ENDC}")
            if result.stderr:
                print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}✗ {description} failed with error:{Colors.ENDC}")
        print(e.stderr)
        if check:
            sys.exit(1)
        return e


def format_code() -> bool:
    """Format code with Black and isort."""
    print_step("FORMATTING CODE")
    
    black_result = run_command(["black", "."], "Black formatting", check=False)
    isort_result = run_command(["isort", "."], "Import sorting", check=False)
    
    return black_result.returncode == 0 and isort_result.returncode == 0


def lint_code() -> bool:
    """Run linters on the code."""
    print_step("LINTING CODE")
    
    ruff_result = run_command(
        ["ruff", "check", "."], "Ruff linting", check=False
    )
    pylint_result = run_command(
        ["pylint", "custom_components/owm_precipitation_forecast"],
        "Pylint",
        check=False,
    )
    
    return ruff_result.returncode == 0 and pylint_result.returncode == 0


def type_check() -> bool:
    """Run type checking with MyPy."""
    print_step("TYPE CHECKING")
    
    result = run_command(
        ["mypy", "custom_components/owm_precipitation_forecast"],
        "MyPy type checking",
        check=False,
    )
    
    return result.returncode == 0


def security_check() -> bool:
    """Run security checks with Bandit."""
    print_step("SECURITY CHECKING")
    
    result = run_command(
        ["bandit", "-r", "custom_components/owm_precipitation_forecast"],
        "Bandit security check",
        check=False,
    )
    
    return result.returncode == 0


def run_tests(coverage: bool = True, markers: str | None = None) -> bool:
    """Run tests with pytest."""
    print_step("RUNNING TESTS")
    
    cmd = ["pytest", "tests", "-v"]
    
    if markers:
        cmd.extend(["-m", markers])
    
    if coverage:
        cmd.extend([
            "--cov=custom_components.owm_precipitation_forecast",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml",
        ])
    
    result = run_command(cmd, "Pytest", check=False)
    
    if coverage and result.returncode == 0:
        print(f"\n{Colors.OKCYAN}Coverage report generated in htmlcov/index.html{Colors.ENDC}")
    
    return result.returncode == 0


def validate_manifest() -> bool:
    """Validate the manifest.json file."""
    print_step("VALIDATING MANIFEST")
    
    manifest_path = Path("custom_components/owm_precipitation_forecast/manifest.json")
    
    if not manifest_path.exists():
        print(f"{Colors.WARNING}Manifest file not found at {manifest_path}{Colors.ENDC}")
        return False
    
    result = run_command(
        ["python", "scripts/validate_manifest.py"],
        "Manifest validation",
        check=False,
    )
    
    return result.returncode == 0


def build_package() -> bool:
    """Build the package."""
    print_step("BUILDING PACKAGE")
    
    result = run_command(
        ["python", "-m", "build"],
        "Package build",
        check=False,
    )
    
    return result.returncode == 0


def main() -> None:
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(
        description="Build script for OWM Precipitation Forecast integration"
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format code with Black and isort",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linters (Ruff, Pylint)",
    )
    parser.add_argument(
        "--type-check",
        action="store_true",
        help="Run type checking with MyPy",
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security checks with Bandit",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run tests with pytest",
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage when running tests",
    )
    parser.add_argument(
        "--test-markers",
        type=str,
        help="Pytest markers to filter tests (e.g., 'unit', 'integration')",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate manifest and HACS compliance",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build the package",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks and build",
    )
    
    args = parser.parse_args()
    
    # If no specific flags, run all
    if not any([
        args.format,
        args.lint,
        args.type_check,
        args.security,
        args.test,
        args.validate,
        args.build,
    ]):
        args.all = True
    
    results = {}
    
    if args.all or args.format:
        results["format"] = format_code()
    
    if args.all or args.lint:
        results["lint"] = lint_code()
    
    if args.all or args.type_check:
        results["type_check"] = type_check()
    
    if args.all or args.security:
        results["security"] = security_check()
    
    if args.all or args.test:
        results["test"] = run_tests(
            coverage=not args.no_coverage,
            markers=args.test_markers,
        )
    
    if args.all or args.validate:
        results["validate"] = validate_manifest()
    
    if args.all or args.build:
        results["build"] = build_package()
    
    # Print summary
    print_step("BUILD SUMMARY")
    
    all_passed = True
    for step, passed in results.items():
        status = f"{Colors.OKGREEN}✓ PASSED{Colors.ENDC}" if passed else f"{Colors.FAIL}✗ FAILED{Colors.ENDC}"
        print(f"{step.upper()}: {status}")
        all_passed = all_passed and passed
    
    if all_passed:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All checks passed!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Some checks failed{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
