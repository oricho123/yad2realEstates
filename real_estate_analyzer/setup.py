"""Setup configuration for Real Estate Analyzer package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements


def read_requirements(filename):
    """Read requirements from a file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#') and not line.startswith('-r')]


setup(
    name="real-estate-analyzer",
    version="2.0.0",
    author="Real Estate Analytics Team",
    author_email="team@real-estate-analyzer.com",
    description="Interactive web dashboard for analyzing real estate prices from Yad2 listings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/real-estate-analyzer",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/real-estate-analyzer/issues",
        "Documentation": "https://github.com/yourusername/real-estate-analyzer/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/real-estate-analyzer",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Dash",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements/base.txt"),
    extras_require={
        "dev": read_requirements("requirements/dev.txt"),
        "production": read_requirements("requirements/production.txt"),
    },
    entry_points={
        "console_scripts": [
            "real-estate-analyzer=cli:cli",
            "rea=cli:cli",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "": ["assets/*", "*.md", "*.txt", "*.env"],
    },
    zip_safe=False,
    keywords=[
        "real-estate", "analysis", "visualization", "yad2", "dashboard",
        "property", "market", "investment", "data-science"
    ],
)
