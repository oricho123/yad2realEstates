"""Application settings and environment configuration."""
import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Look for .env file in the project root (real_estate_analyzer directory)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"ℹ️  No .env file found at {env_path} - using system environment variables")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")


class AppSettings:
    """Main application settings."""
    
    # Environment
    DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIRECTORY = BASE_DIR / 'data' / 'scraped'
    LOG_DIRECTORY = BASE_DIR / 'logs'
    
    # Server
    SERVER_HOST = os.getenv('HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('PORT', '8051'))
    
    # Cache
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    
    # API
    REQUEST_TIMEOUT = 30
    RATE_LIMIT_DELAY = 1.0
    
    # Data processing
    MAX_CONCURRENT_REQUESTS = 5
    BATCH_SIZE = 1000
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        cls.DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_data_file_path(cls, filename: str) -> Path:
        """Get full path for a data file."""
        return cls.DATA_DIRECTORY / filename
    
    @classmethod
    def get_log_file_path(cls, filename: str) -> Path:
        """Get full path for a log file."""
        return cls.LOG_DIRECTORY / filename


class DashConfiguration:
    """Dash-specific configuration."""
    
    # App settings
    SUPPRESS_CALLBACK_EXCEPTIONS = True
    SERVE_LOCALLY = True
    
    # External stylesheets
    EXTERNAL_STYLESHEETS = [
        {
            'href': 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
            'rel': 'stylesheet'
        },
        {
            'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
            'rel': 'stylesheet'
        }
    ]
    
    # Meta tags
    META_TAGS = [
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]


class LoggingConfiguration:
    """Logging configuration."""
    
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Log file rotation
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5
    
    @classmethod
    def get_logging_config(cls) -> dict:
        """Get logging configuration dictionary."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': cls.LOG_FORMAT,
                    'datefmt': cls.LOG_DATE_FORMAT
                },
            },
            'handlers': {
                'console': {
                    'level': AppSettings.LOG_LEVEL,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': AppSettings.get_log_file_path('real_estate_analyzer.log'),
                    'maxBytes': cls.MAX_LOG_SIZE,
                    'backupCount': cls.BACKUP_COUNT,
                    'formatter': 'standard',
                },
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['console', 'file'],
                    'level': AppSettings.LOG_LEVEL,
                    'propagate': False
                }
            }
        }


class EnvironmentConfig:
    """Environment-specific configuration."""
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return AppSettings.DEBUG_MODE
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return not AppSettings.DEBUG_MODE
    
    @classmethod
    def get_environment_name(cls) -> str:
        """Get current environment name."""
        return "development" if cls.is_development() else "production" 