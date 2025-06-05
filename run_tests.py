#!/usr/bin/env python3
"""
Test runner script for the real estate analyzer project.
Usage: python run_tests.py [pytest arguments]
"""
import sys
import subprocess
from pathlib import Path

def install_test_dependencies():
    """Install test dependencies if needed."""
    try:
        import pytest
    except ImportError:
        print("Installing test dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "tests/requirements-test.txt"
        ])

def run_tests(args=None):
    """Run the test suite."""
    if args is None:
        args = sys.argv[1:]
    
    # Install dependencies
    install_test_dependencies()
    
    # Run pytest
    cmd = [sys.executable, "-m", "pytest"] + args
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 