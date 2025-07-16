"""Application factory for Real Estate Analyzer Dashboard.

This module provides the application factory pattern for creating
Dash application instances with different configurations.
"""

import os
import pandas as pd
from pathlib import Path
from src.dashboard.app import RealEstateDashboardApp
from src.config.settings import get_config


def create_app(config_name=None):
    """
    Application factory to create and configure the Dash application.

    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
                          If None, uses environment variable or defaults to 'development'

    Returns:
        dash.Dash: Configured Dash application instance
    """
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Get configuration
    config = get_config(config_name)

    # Load initial data (empty DataFrame if no data file exists)
    data_path = Path(__file__).parent / 'data' / 'scraped'
    initial_data = pd.DataFrame()

    # Look for existing scraped data files
    if data_path.exists():
        csv_files = list(data_path.glob('*.csv'))
        if csv_files:
            try:
                # Load the most recent data file
                latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                initial_data = pd.read_csv(latest_file)
                print(f"Loaded initial data from: {latest_file}")
            except Exception as e:
                print(f"Warning: Could not load data file: {e}")

    # Create dashboard application
    dashboard = RealEstateDashboardApp(initial_data)
    app = dashboard.app

    # Configure Flask server
    app.server.config.from_object(config)

    return app


def create_wsgi_app():
    """
    Create WSGI application for production deployment.

    Returns:
        Flask: WSGI application instance
    """
    app = create_app('production')
    return app.server


# For direct execution
if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 8051)),
        debug=os.getenv('DEBUG', 'true').lower() == 'true'
    )
