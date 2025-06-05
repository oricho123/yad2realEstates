"""Real Estate Analyzer - A comprehensive property analysis dashboard."""

__version__ = "2.0.0"
__author__ = "Real Estate Analytics Team"

# Package metadata
PACKAGE_NAME = "real_estate_analyzer"
DESCRIPTION = "Interactive web dashboard for analyzing real estate prices from Yad2 listings"

# Main modules
from .src.config.settings import AppSettings
from .src.data.loaders import PropertyDataLoader
from .src.data.models import PropertyDataFrame 