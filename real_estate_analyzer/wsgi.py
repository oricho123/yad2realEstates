"""WSGI entry point for production deployment.

This module provides the WSGI application instance for production servers
like Gunicorn, uWSGI, or Apache mod_wsgi.

Usage:
    gunicorn wsgi:application
    uwsgi --module wsgi:application
"""

from src.config.settings import get_config
from app import create_app
import os
import sys
from pathlib import Path

# Ensure the package is in the Python path
package_root = Path(__file__).parent
sys.path.insert(0, str(package_root))

# Import configuration to ensure .env file is loaded

# Set production environment if not already set
if not os.getenv('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

# Get configuration (this will load .env file)
config = get_config('production')

# Create application instance
app = create_app(config_name='production')

# Expose the Flask server for WSGI
application = app.server

# For compatibility with different WSGI servers
server = application

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    # Use the configuration values that have been loaded from .env
    application.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=False
    )
