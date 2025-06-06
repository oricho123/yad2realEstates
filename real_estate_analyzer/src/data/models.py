"""Data models and schemas for property data."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

from src.config.constants import PropertyValidation


@dataclass
class PropertyListing:
    """Represents a single property listing."""

    # Core identifiers
    id: Optional[str] = None
    token: Optional[str] = None

    # Financial data
    price: Optional[float] = None
    price_per_sqm: Optional[float] = None

    # Property details
    rooms: Optional[float] = None
    square_meters: Optional[float] = None
    property_type: Optional[str] = None
    condition_text: Optional[str] = None

    # Location data
    city: Optional[str] = None
    area: Optional[str] = None
    neighborhood: Optional[str] = None
    street: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    floor: Optional[str] = None

    # Metadata
    ad_type: Optional[str] = None
    full_url: Optional[str] = None
    scraped_at: Optional[datetime] = None

    # Calculated fields
    value_score: Optional[float] = field(default=None, init=False)
    value_category: Optional[str] = field(default=None, init=False)
    sqm_per_room: Optional[float] = field(default=None, init=False)

    def __post_init__(self):
        """Calculate derived fields after initialization."""
        if self.price_per_sqm is None and self.price and self.square_meters and self.square_meters > 0:
            self.price_per_sqm = self.price / self.square_meters

        if self.sqm_per_room is None:
            self.sqm_per_room = self.calculate_sqm_per_room()

    def calculate_sqm_per_room(self) -> Optional[float]:
        """Calculate square meters per room."""
        if self.square_meters and self.rooms and self.rooms > 0:
            return self.square_meters / self.rooms
        return None

    def is_valid(self) -> bool:
        """Check if property has minimum required data for analysis."""
        return (
            self.price is not None and self.price > PropertyValidation.MIN_PRICE and
            self.square_meters is not None and self.square_meters > PropertyValidation.MIN_SQUARE_METERS and
            self.price_per_sqm is not None and
            PropertyValidation.MIN_REALISTIC_PRICE_PER_SQM <= self.price_per_sqm <= PropertyValidation.MAX_REALISTIC_PRICE_PER_SQM
        )

    def has_location_data(self) -> bool:
        """Check if property has valid geographic coordinates."""
        return (
            self.lat is not None and self.lng is not None and
            isinstance(self.lat, (int, float)) and isinstance(self.lng, (int, float)) and
            not (np.isnan(self.lat) or np.isnan(self.lng))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            'id': self.id,
            'token': self.token,
            'price': self.price,
            'price_per_sqm': self.price_per_sqm,
            'rooms': self.rooms,
            'square_meters': self.square_meters,
            'property_type': self.property_type,
            'condition_text': self.condition_text,
            'city': self.city,
            'area': self.area,
            'neighborhood': self.neighborhood,
            'street': self.street,
            'lat': self.lat,
            'lng': self.lng,
            'floor': self.floor,
            'ad_type': self.ad_type,
            'full_url': self.full_url,
            'scraped_at': self.scraped_at,
            'value_score': self.value_score,
            'value_category': self.value_category,
            'sqm_per_room': self.sqm_per_room
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyListing':
        """Create PropertyListing from dictionary."""
        # Handle datetime conversion
        scraped_at = data.get('scraped_at')
        if isinstance(scraped_at, str):
            try:
                scraped_at = datetime.fromisoformat(scraped_at)
            except (ValueError, TypeError):
                scraped_at = None

        return cls(
            id=data.get('id'),
            token=data.get('token'),
            price=data.get('price'),
            price_per_sqm=data.get('price_per_sqm'),
            rooms=data.get('rooms'),
            square_meters=data.get('square_meters'),
            property_type=data.get('property_type'),
            condition_text=data.get('condition_text'),
            city=data.get('city'),
            area=data.get('area'),
            neighborhood=data.get('neighborhood'),
            street=data.get('street'),
            lat=data.get('lat'),
            lng=data.get('lng'),
            floor=data.get('floor'),
            ad_type=data.get('ad_type'),
            full_url=data.get('full_url'),
            scraped_at=scraped_at
        )


@dataclass
class PropertyFilters:
    """Represents filter criteria for property searches."""

    # Price filters
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    # Size filters
    min_square_meters: Optional[float] = None
    max_square_meters: Optional[float] = None

    # Room filters
    min_rooms: Optional[float] = None
    max_rooms: Optional[float] = None

    # Location filters
    neighborhoods: Optional[List[str]] = None
    exclude_neighborhoods: Optional[List[str]] = None

    # Category filters
    property_types: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    ad_types: Optional[List[str]] = None

    # Geographic filters
    has_coordinates: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert filters to dictionary for serialization."""
        return {
            'min_price': self.min_price,
            'max_price': self.max_price,
            'min_square_meters': self.min_square_meters,
            'max_square_meters': self.max_square_meters,
            'min_rooms': self.min_rooms,
            'max_rooms': self.max_rooms,
            'neighborhoods': self.neighborhoods,
            'exclude_neighborhoods': self.exclude_neighborhoods,
            'property_types': self.property_types,
            'conditions': self.conditions,
            'ad_types': self.ad_types,
            'has_coordinates': self.has_coordinates
        }


class PropertyDataFrame:
    """Wrapper for property DataFrame with validation and utilities."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with property DataFrame."""
        self.data = data.copy() if not data.empty else pd.DataFrame()
        self._validate_columns()
        self._ensure_data_types()

    def _validate_columns(self):
        """Validate that required columns exist."""
        if self.data.empty:
            # Create empty DataFrame with correct structure
            self.data = self._create_empty_dataframe()
            return

        required_columns = [
            'price', 'square_meters', 'price_per_sqm', 'lat', 'lng',
            'neighborhood', 'rooms', 'condition_text', 'ad_type',
            'property_type', 'street', 'floor', 'full_url'
        ]

        missing_columns = set(required_columns) - set(self.data.columns)
        if missing_columns:
            # Add missing columns with default values
            for col in missing_columns:
                self.data[col] = None

    def _ensure_data_types(self):
        """Ensure proper data types for numeric columns."""
        if self.data.empty:
            return

        numeric_columns = ['price', 'square_meters',
                           'price_per_sqm', 'lat', 'lng', 'rooms']

        for col in numeric_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')

    def _create_empty_dataframe(self) -> pd.DataFrame:
        """Create an empty DataFrame with the correct structure."""
        return pd.DataFrame(columns=[
            'id', 'token', 'price', 'square_meters', 'price_per_sqm',
            'rooms', 'property_type', 'condition_text',
            'city', 'area', 'neighborhood', 'street', 'lat', 'lng', 'floor',
            'ad_type', 'full_url', 'scraped_at',
            'value_score', 'value_category', 'sqm_per_room'
        ])

    @property
    def is_empty(self) -> bool:
        """Check if the DataFrame is empty."""
        return len(self.data) == 0

    def get_valid_properties(self) -> 'PropertyDataFrame':
        """Return only properties with valid core data."""
        if self.is_empty:
            return PropertyDataFrame(pd.DataFrame())

        valid_data = self.data[
            (self.data['price'].notna()) & (self.data['price'] > PropertyValidation.MIN_PRICE) &
            (self.data['square_meters'].notna()) & (self.data['square_meters'] > PropertyValidation.MIN_SQUARE_METERS) &
            (self.data['price_per_sqm'].notna()) &
            (self.data['price_per_sqm'] >= PropertyValidation.MIN_REALISTIC_PRICE_PER_SQM) &
            (self.data['price_per_sqm'] <=
             PropertyValidation.MAX_REALISTIC_PRICE_PER_SQM)
        ].copy()

        return PropertyDataFrame(valid_data)

    def get_properties_with_location(self) -> 'PropertyDataFrame':
        """Return only properties with valid geographic coordinates."""
        if self.is_empty:
            return PropertyDataFrame(pd.DataFrame())

        location_data = self.data[
            (self.data['lat'].notna()) & (self.data['lng'].notna()) &
            (self.data['lat'] != 0) & (self.data['lng'] != 0)
        ].copy()

        return PropertyDataFrame(location_data)

    def apply_filters(self, filters: PropertyFilters) -> 'PropertyDataFrame':
        """Apply filters to the property data."""
        if self.is_empty:
            return PropertyDataFrame(pd.DataFrame())

        filtered_data = self.data.copy()

        # Price filters
        if filters.min_price is not None:
            filtered_data = filtered_data[filtered_data['price']
                                          >= filters.min_price]
        if filters.max_price is not None:
            filtered_data = filtered_data[filtered_data['price']
                                          <= filters.max_price]

        # Size filters
        if filters.min_square_meters is not None:
            filtered_data = filtered_data[filtered_data['square_meters']
                                          >= filters.min_square_meters]
        if filters.max_square_meters is not None:
            filtered_data = filtered_data[filtered_data['square_meters']
                                          <= filters.max_square_meters]

        # Room filters
        if filters.min_rooms is not None:
            filtered_data = filtered_data[filtered_data['rooms']
                                          >= filters.min_rooms]
        if filters.max_rooms is not None:
            filtered_data = filtered_data[filtered_data['rooms']
                                          <= filters.max_rooms]

        # Neighborhood filters
        if filters.neighborhoods and len(filters.neighborhoods) > 0:
            filtered_data = filtered_data[filtered_data['neighborhood'].isin(
                filters.neighborhoods)]

        if filters.exclude_neighborhoods and len(filters.exclude_neighborhoods) > 0:
            filtered_data = filtered_data[~filtered_data['neighborhood'].isin(
                filters.exclude_neighborhoods)]

        # Category filters
        if filters.property_types and len(filters.property_types) > 0:
            filtered_data = filtered_data[filtered_data['property_type'].isin(
                filters.property_types)]

        if filters.conditions and len(filters.conditions) > 0:
            filtered_data = filtered_data[filtered_data['condition_text'].isin(
                filters.conditions)]

        if filters.ad_types and len(filters.ad_types) > 0:
            filtered_data = filtered_data[filtered_data['ad_type'].isin(
                filters.ad_types)]

        # Geographic filters
        if filters.has_coordinates is True:
            filtered_data = filtered_data[
                (filtered_data['lat'].notna()) & (filtered_data['lng'].notna()) &
                (filtered_data['lat'] != 0) & (filtered_data['lng'] != 0)
            ]

        return PropertyDataFrame(filtered_data)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for the property data."""
        if self.is_empty:
            return {}

        valid_data = self.get_valid_properties().data

        if len(valid_data) == 0:
            return {}

        return {
            'total_properties': len(valid_data),
            'avg_price': valid_data['price'].mean(),
            'median_price': valid_data['price'].median(),
            'min_price': valid_data['price'].min(),
            'max_price': valid_data['price'].max(),
            'avg_price_per_sqm': valid_data['price_per_sqm'].mean(),
            'median_price_per_sqm': valid_data['price_per_sqm'].median(),
            'avg_square_meters': valid_data['square_meters'].mean(),
            'avg_rooms': valid_data['rooms'].mean(),
            'unique_neighborhoods': valid_data['neighborhood'].nunique() if 'neighborhood' in valid_data.columns else 0,
            'properties_with_location': len(self.get_properties_with_location().data)
        }

    def to_property_listings(self) -> List[PropertyListing]:
        """Convert DataFrame to list of PropertyListing objects."""
        if self.is_empty:
            return []

        return [PropertyListing.from_dict(row.to_dict()) for _, row in self.data.iterrows()]

    @classmethod
    def from_property_listings(cls, listings: List[PropertyListing]) -> 'PropertyDataFrame':
        """Create PropertyDataFrame from list of PropertyListing objects."""
        if not listings:
            return cls(pd.DataFrame())

        data = pd.DataFrame([listing.to_dict() for listing in listings])
        return cls(data)

    def __len__(self) -> int:
        """Return the number of properties."""
        return len(self.data)

    def __getitem__(self, key):
        """Allow direct access to underlying DataFrame."""
        return self.data[key]

    def __setitem__(self, key, value):
        """Allow direct assignment to underlying DataFrame."""
        self.data[key] = value

    def to_json_storage(self) -> str:
        """
        Convert PropertyDataFrame to JSON string for browser storage.

        Returns:
            JSON string representation of the data
        """
        if self.is_empty:
            return '[]'

        # Convert to records format and handle datetime serialization
        records = self.data.copy()

        # Convert datetime columns to ISO strings
        datetime_columns = ['scraped_at']
        for col in datetime_columns:
            if col in records.columns:
                records[col] = records[col].dt.strftime(
                    '%Y-%m-%dT%H:%M:%S.%f').fillna('')

        # Convert to dictionary records
        records_data = records.to_dict('records')

        # Convert to JSON
        import json
        return json.dumps(records_data, ensure_ascii=False, default=str)

    @classmethod
    def from_json_storage(cls, json_str: str) -> 'PropertyDataFrame':
        """
        Create PropertyDataFrame from JSON string stored in browser.

        Args:
            json_str: JSON string from browser storage

        Returns:
            PropertyDataFrame instance
        """
        import json

        try:
            if not json_str or json_str.strip() == '':
                return cls(pd.DataFrame())

            records = json.loads(json_str)

            if not records:
                return cls(pd.DataFrame())

            # Create DataFrame from records
            df = pd.DataFrame(records)

            # Ensure proper data types
            numeric_columns = ['price', 'square_meters',
                               'price_per_sqm', 'lat', 'lng', 'rooms']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Convert datetime columns
            datetime_columns = ['scraped_at']
            for col in datetime_columns:
                if col in df.columns and col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            return cls(df)

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to parse JSON storage data: {str(e)}")
            return cls(pd.DataFrame())

    def get_storage_size_bytes(self) -> int:
        """
        Calculate the approximate storage size in bytes for this dataset.

        Returns:
            Estimated size in bytes when stored as JSON
        """
        if self.is_empty:
            return 0

        json_str = self.to_json_storage()
        return len(json_str.encode('utf-8'))
