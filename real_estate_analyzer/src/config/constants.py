"""Business constants and configuration values."""


class PropertyValidation:
    """Property data validation constants."""
    MIN_REALISTIC_PRICE_PER_SQM = 1000
    MAX_REALISTIC_PRICE_PER_SQM = 100000
    MIN_PRICE = 0
    MAX_PRICE = 50000000
    MIN_SQUARE_METERS = 1
    MAX_SQUARE_METERS = 1000
    MIN_ROOMS = 0.5
    MAX_ROOMS = 20


class MapConfiguration:
    """Map visualization settings."""
    DEFAULT_ZOOM = 11
    DEFAULT_HEIGHT = 600
    DEFAULT_CENTER_LAT = 32.8
    DEFAULT_CENTER_LNG = 35.0
    MAPBOX_STYLE = "open-street-map"


class ChartConfiguration:
    """Chart visualization settings."""
    DEFAULT_HEIGHT = 350
    DEFAULT_WIDTH = 800
    SCATTER_SIZE_MAX = 20
    COLOR_SCALE = 'viridis'
    
    # Sizing and layout
    SIZE_MAX = 15
    OPACITY = 0.8
    LINE_WIDTH = 1
    LINE_COLOR = 'DarkSlateGrey'


class UIConfiguration:
    """UI component settings."""
    DEFAULT_SERVER_PORT = 8051
    FILTER_GRID_MIN_WIDTH = 280
    CARD_BORDER_RADIUS = 12
    LOADING_SPINNER_SIZE = 60
    
    # Responsive breakpoints
    MOBILE_BREAKPOINT = 900
    TABLET_BREAKPOINT = 1200


class ValueAnalysisConstants:
    """Constants for property value analysis."""
    EXCELLENT_DEAL_THRESHOLD = -15  # % below market
    GOOD_DEAL_THRESHOLD = -5        # % below market
    FAIR_PRICE_THRESHOLD = 5        # % above market
    ABOVE_MARKET_THRESHOLD = 15     # % above market
    
    # Trend line configuration
    POLYNOMIAL_DEGREE = 1  # Linear trend
    
    # Neighborhood analysis
    MIN_PROPERTIES_FOR_RANKING = 3
    AFFORDABILITY_WEIGHT = 0.7
    EFFICIENCY_WEIGHT = 0.3


class ScrapingConfiguration:
    """Scraping and API configuration."""
    REQUEST_TIMEOUT = 30
    RATE_LIMIT_DELAY = 1.0
    MAX_RETRIES = 3
    
    # Default search parameters
    DEFAULT_CITY = 9500
    DEFAULT_AREA = 6
    DEFAULT_TOP_AREA = 25
    DEFAULT_MIN_PRICE = 1350000
    DEFAULT_MAX_PRICE = 1420000


class DataQualityConstants:
    """Data quality and validation thresholds."""
    MIN_DATA_QUALITY_PERCENTAGE = 90
    MAX_MISSING_DATA_PERCENTAGE = 0.05  # 5%
    
    # File naming patterns
    CSV_FILENAME_PATTERN = "real_estate_listings_*.csv"
    JSON_FILENAME_PATTERN = "raw_api_response_*.json"


class CityOptions:
    """Available city options for scraping."""
    CITIES = [
        {'label': 'קרית ביאליק (Current)', 'value': 9500},
        {'label': 'תל אביב-יפו', 'value': 5000},
        {'label': 'ירושלים', 'value': 3000},
        {'label': 'חיפה', 'value': 8600},
        {'label': 'פתח תקווה', 'value': 7900},
        {'label': 'אשדוד', 'value': 1300},
        {'label': 'נתניה', 'value': 6300},
        {'label': 'באר שבע', 'value': 900}
    ]


class PropertyConditionMapping:
    """Mapping for property condition IDs to text."""
    CONDITION_MAP = {
        1: "חדש מיידי הבונה",
        2: "חדש/משופץ", 
        3: "במצב טוב",
        4: "דרוש שיפוץ",
        5: "דרוש שיפוץ כללי"
    }
    
    DEFAULT_CONDITION = 'לא ידוע' 