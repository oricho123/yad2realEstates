"""Application settings and environment configuration.

This module provides environment-based configuration management following
Python web application best practices.
"""

import os
import logging
from pathlib import Path


# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Look for .env file in the project root (real_estate_analyzer directory)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(
            f"ℹ️  No .env file found at {env_path} - using system environment variables")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")


class BaseConfig:
    """Base configuration with common settings."""

    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = False

    # Directories
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIRECTORY = BASE_DIR / 'data' / 'scraped'
    LOG_DIRECTORY = BASE_DIR / 'logs'
    ASSETS_DIRECTORY = BASE_DIR / 'assets'

    # Server
    SERVER_HOST = os.getenv('HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('PORT', '8051'))

    # Cache
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))

    # API Configuration
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '1.0'))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Security (for future use)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    @classmethod
    def init_app(cls, app):
        """Initialize application with this configuration."""
        pass

    @classmethod
    def create_directories(cls):
        """Create necessary directories."""
        cls.DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SERVER_HOST = '127.0.0.1'
    LOG_LEVEL = 'DEBUG'
    CACHE_TIMEOUT = 60  # Shorter cache for development

    @classmethod
    def init_app(cls, app):
        """Initialize development-specific settings."""
        BaseConfig.init_app(app)

        # Setup development logging
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT
        )


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    SERVER_HOST = os.getenv('HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('PORT', '8000'))
    LOG_LEVEL = 'WARNING'

    # Production-specific settings
    CACHE_TIMEOUT = 3600  # Longer cache for production
    REQUEST_TIMEOUT = 60  # Longer timeout for production

    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        BaseConfig.init_app(app)

        # Setup production logging
        import logging.handlers

        cls.LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            cls.LOG_DIRECTORY / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(getattr(logging, cls.LOG_LEVEL))
        file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))

        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logger.setLevel(getattr(logging, cls.LOG_LEVEL))


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    SERVER_PORT = 8052  # Different port for testing
    CACHE_ENABLED = False  # Disable cache for testing
    LOG_LEVEL = 'DEBUG'

    # Test-specific directories
    DATA_DIRECTORY = BaseConfig.BASE_DIR / 'test_data'

    @classmethod
    def init_app(cls, app):
        """Initialize testing-specific settings."""
        BaseConfig.init_app(app)

        # Setup test logging
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT
        )


# Configuration registry
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> BaseConfig:
    """
    Get configuration class based on environment.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Configuration class instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    return config.get(config_name, config['default'])


# Legacy compatibility - keeping AppSettings for backward compatibility
AppSettings = DevelopmentConfig()

# Update AppSettings based on current environment
current_env = os.getenv('FLASK_ENV', 'development')
if current_env in config:
    AppSettings = config[current_env]()


class DashConfiguration:
    """Dash-specific configuration settings."""

    EXTERNAL_STYLESHEETS = [
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]

    SUPPRESS_CALLBACK_EXCEPTIONS = True

    META_TAGS = [
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description",
            "content": "Real Estate Price Analyzer - Interactive dashboard for property market analysis"},
        {"name": "author", "content": "Real Estate Analytics Team"},
        {"property": "og:title", "content": "Real Estate Price Analyzer"},
        {"property": "og:description",
            "content": "Analyze real estate market data with interactive visualizations"},
        {"property": "og:type", "content": "website"}
    ]
