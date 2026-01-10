#!/usr/bin/env python3
"""
Professional Build System for Home Assistant OWM Precipitation Forecast Integration
Single command verification: validate → format → lint → test → coverage
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional

class BuildSystem:
    def __init__(self):
        self.root = Path(__file__).parent
        self.commands = {
            'validate': self._validate,
            'format': self._format,
            'lint': self._lint,
            'test': self._test,
            'coverage': self._coverage,
            'clean': self._clean,
            'all': self._all
        }

    def run(self, args: List[str]) -> int:
        """Main entry point"""
        if not args:
            self._print_help()
            return 1

        cmd = args[^6_0]
        if cmd in self.commands:
            print(f"🚀 Running: build.py {cmd}")
            try:
                result = self.commands[cmd]()
                print("✅ All checks passed!")
                return result
            except subprocess.CalledProcessError as e:
                print(f"❌ {cmd} failed with exit code {e.returncode}")
                return 1
            except Exception as e:
                print(f"❌ {cmd} failed: {e}")
                return 1
        else:
            print(f"❌ Unknown command: {cmd}")
            self._print_help()
            return 1

    def _print_help(self):
        """Print usage information"""
        print("\nAvailable commands:")
        print("  validate    - Validate integration manifest and structure")
        print("  format      - Format all code (Black, isort, yamllint)")
        print("  lint        - Run all linters (Ruff, Pylint, mypy, yamllint)")
        print("  test        - Run test suite")
        print("  coverage    - Run tests with coverage report")
        print("  clean       - Remove build artifacts")
        print("  all         - Run complete pipeline (recommended)")
        print("\nExample: python build.py all")

    def _validate(self) -> int:
        """Validate manifest.json and project structure"""
        manifest = self.root / "custom_components/owm_precipitation_forecast/manifest.json"
        if not manifest.exists():
            raise FileNotFoundError("manifest.json not found")

        # Check JSON validity (simplified)
        import json
        with open(manifest) as f:
            json.load(f)
        print("✅ manifest.json is valid")
        return 0

    def _format(self) -> int:
        """Run code formatting tools"""
        subprocess.run([sys.executable, "-m", "black", "."], check=True)
        subprocess.run([sys.executable, "-m", "isort", "."], check=True)
        subprocess.run(["yamllint", "."], check=True)
        print("✅ Code formatted")
        return 0

    def _lint(self) -> int:
        """Run all linters"""
        subprocess.run(["ruff", "check", "."], check=True)
        subprocess.run(["pylint", "custom_components", "tests"], check=True)
        subprocess.run(["mypy", "."], check=True)
        print("✅ Linting passed")
        return 0

    def _test(self) -> int:
        """Run test suite"""
        subprocess.run([sys.executable, "-m", "pytest", "tests", "-v"], check=True)
        print("✅ Tests passed")
        return 0

    def _coverage(self) -> int:
        """Run tests with coverage"""
        subprocess.run([
            sys.executable, "-m", "pytest", "tests",
            "--cov=custom_components/owm_precipitation_forecast",
            "--cov-report=html"
        ], check=True)
        print("✅ Coverage report generated (htmlcov/index.html)")
        return 0

    def _clean(self) -> int:
        """Clean build artifacts"""
        for path in ["build", "dist", ".pytest_cache", "htmlcov", "__pycache__"]:
            import shutil
            if Path(path).exists():
                shutil.rmtree(path)
        print("✅ Artifacts cleaned")
        return 0

    def _all(self) -> int:
        """Run complete pipeline"""
        self._validate()
        self._format()
        self._lint()
        self._test()
        self._coverage()
        print("🎉 COMPLETE BUILD SUCCESS!")
        return 0

if __name__ == "__main__":
    sys.exit(BuildSystem().run(sys.argv[1:]))
