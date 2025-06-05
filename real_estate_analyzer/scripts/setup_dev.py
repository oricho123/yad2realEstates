#!/usr/bin/env python3
"""Development environment setup script."""

import subprocess
import sys
from pathlib import Path


def run_command(command: str) -> bool:
    """Run a shell command and return success status."""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return False


def setup_development_environment():
    """Set up the development environment."""
    print("🔧 Setting up development environment...")

    # Install development dependencies
    print("📦 Installing development dependencies...")
    if not run_command("pip install black isort flake8 mypy pytest pytest-cov"):
        return False

    # Create necessary directories
    print("📁 Creating directory structure...")
    directories = [
        "src/config", "src/data", "src/analysis", "src/visualization/charts",
        "src/visualization/components", "src/dashboard/callbacks", "src/scraping",
        "src/utils", "tests/unit", "tests/integration", "tests/fixtures",
        "data/scraped", "docs", "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    # Create __init__.py files
    print("🔨 Creating __init__.py files...")
    init_files = [
        "src/__init__.py", "src/config/__init__.py", "src/data/__init__.py",
        "src/analysis/__init__.py", "src/visualization/__init__.py",
        "src/visualization/charts/__init__.py", "src/visualization/components/__init__.py",
        "src/dashboard/__init__.py", "src/dashboard/callbacks/__init__.py",
        "src/scraping/__init__.py", "src/utils/__init__.py",
        "tests/__init__.py", "tests/unit/__init__.py", "tests/integration/__init__.py"
    ]

    for init_file in init_files:
        Path(init_file).touch()

    print("✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Run the refactoring implementation")
    print("2. Start with Phase 1A tasks")
    print("3. Follow the REFACTORING_PLAN.md guide")


if __name__ == "__main__":
    setup_development_environment() 