"""WSGI entry point for production deployment.

This module provides the WSGI application instance for production servers
like Gunicorn, uWSGI, or Apache mod_wsgi.

Usage:
    gunicorn wsgi:application
    uwsgi --module wsgi:application
"""

from app import create_app
import os
import sys
from pathlib import Path

# Ensure the package is in the Python path
package_root = Path(__file__).parent
sys.path.insert(0, str(package_root))


# Set production environment if not already set
if not os.getenv('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

# Create application instance
app = create_app(config_name='production')

# Expose the Flask server for WSGI
application = app.server

# For compatibility with different WSGI servers
server = application

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    application.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8000)),
        debug=False
    )
